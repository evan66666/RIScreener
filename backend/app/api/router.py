import json
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from pydantic import BaseModel
from pathlib import Path
import asyncio

from app.database import engine, get_session
from app.models.schema import (
    Scan, Company, Actor, ActorAlias, ActorRelationship,
    Announcement, Document, DocumentPage,
    OwnershipSnapshot, OwnershipEvent, TransactionEvent,
    CorporateActionEvent, DocumentSignal, Evidence,
    ActorBehaviorState, IssuerIntelligenceState,
    IssuerActionState, SignalEvent, InvestorClassification, MarketStructureSnapshot,
    CorporateActionAssessment
)
from app.engine.pipeline import execute_screening_pipeline
from app.rules.definitions import ACTION_FAMILIES, TRANSFORMATION_FAMILIES

router = APIRouter(prefix="/api")

class ScreenRequest(BaseModel):
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    lookback_days: int = 60
    mode: str = "smart"  # smart, full_audit


async def _run_screening_task(scan_id: int, scan_from: datetime, scan_to: datetime, lookback_days: int, scan_mode: str = "smart"):
    with Session(engine) as session:
        try:
            await execute_screening_pipeline(
                session=session,
                scan_from=scan_from,
                scan_to=scan_to,
                lookback_days=lookback_days,
                scan_mode=scan_mode,
                scan_id=scan_id
            )
        except Exception as e:
            print(f"[Pipeline Task Error] Scan {scan_id} failed: {e}")
            try:
                scan = session.get(Scan, scan_id)
                if scan:
                    scan.status = "FAILED"
                    scan.completed_at = datetime.utcnow()
                    scan.summary_json = json.dumps({
                        "stage_message": f"Screening pipeline error: {str(e)}",
                        "progress_percent": 0,
                        "error": str(e)
                    })
                    session.add(scan)
                    session.commit()
            except Exception as commit_err:
                print(f"[Pipeline Task Error] Failed to update scan status: {commit_err}")


@router.post("/screen")
async def trigger_screening(
    req: ScreenRequest,
    session: Session = Depends(get_session)
):
    """Starts manual screening run asynchronously in background."""
    now = datetime.now()
    if req.date_from:
        d_from = datetime.fromisoformat(req.date_from).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        d_from = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if req.date_to:
        d_to = datetime.fromisoformat(req.date_to).replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        d_to = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    scan = Scan(
        scan_from=d_from,
        scan_to=d_to,
        lookback_days=req.lookback_days,
        scan_mode=req.mode,
        status="RUNNING",
        summary_json=json.dumps({
            "stage_message": f"Initializing {req.mode.upper()} screening and connecting to IDX...",
            "progress_percent": 5,
            "scan_mode": req.mode,
            "announcements_retrieved": 0,
            "tier_a_documents": 0,
            "tier_b_documents": 0,
            "tier_c_metadata_only": 0,
            "documents_processed": 0,
            "ownership_events": 0,
            "signals_total": 0
        })
    )
    session.add(scan)
    session.commit()
    session.refresh(scan)

    # Launch background task
    asyncio.create_task(_run_screening_task(scan.id, d_from, d_to, req.lookback_days, req.mode))

    return {
        "scan_id": scan.id,
        "status": scan.status,
        "scan_mode": scan.scan_mode,
        "message": f"Screening ({req.mode}) started in background",
        "announcements_found": 0,
        "documents_processed": 0,
        "summary": json.loads(scan.summary_json) if scan.summary_json else {}
    }


@router.get("/scans/latest")
def get_latest_scan(session: Session = Depends(get_session)):
    """Returns the most recent scan metadata and processing completeness metrics."""
    scan = session.exec(select(Scan).order_by(Scan.id.desc())).first()
    if not scan:
        return {"scan": None, "summary": None}
    
    return {
        "scan": scan,
        "summary": json.loads(scan.summary_json) if scan.summary_json else None
    }


@router.get("/scans/{id}")
def get_scan_by_id(id: int, session: Session = Depends(get_session)):
    scan = session.get(Scan, id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {
        "scan": scan,
        "summary": json.loads(scan.summary_json) if scan.summary_json else None
    }


@router.get("/signals")
def list_signals(
    priority: Optional[str] = Query(None),
    behavior: Optional[str] = Query(None),
    action_type: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    impact: Optional[str] = Query(None),
    ticker: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    """Returns ranked Smart Money & Strategic Positioning signals with unified search."""
    query = select(IssuerIntelligenceState).join(Company)

    # Determine unified search term (supports q, search, or ticker==actor from frontend)
    search_term = None
    if q and q.strip():
        search_term = q.strip()
    elif search and search.strip():
        search_term = search.strip()
    elif ticker and actor and ticker.strip() == actor.strip():
        search_term = ticker.strip()

    # If specific ticker only is provided (not a unified search)
    if ticker and not search_term:
        t_clean = ticker.strip().upper()
        query = query.where(
            (Company.ticker.contains(t_clean)) |
            (Company.name.contains(ticker.strip()))
        )

    intel_states = session.exec(query).all()
    results = []

    search_lower = search_term.lower() if search_term else None

    for intel in intel_states:
        comp = intel.company
        act = session.get(Actor, intel.primary_actor_id) if intel.primary_actor_id else None
        action_meta = ACTION_FAMILIES.get(intel.primary_action_type or "", {})
        action_name = action_meta.get("name", intel.primary_action_type or "")
        actor_name = act.canonical_name if act else "Disclosed Strategic Holder"

        # Unified Search filter: matches Ticker, Company Name, Actor, Action Name, or Summaries
        if search_lower:
            t_match = search_lower in comp.ticker.lower()
            c_match = search_lower in (comp.name or "").lower()
            a_match = search_lower in actor_name.lower()
            act_match = (
                search_lower in (intel.primary_action_type or "").lower() or
                search_lower in action_name.lower() or
                search_lower in action_meta.get("category", "").lower()
            )
            why_match = search_lower in (intel.why_flagged_summary or "").lower()
            what_match = search_lower in (intel.what_changed_summary or intel.current_summary or "").lower()
            if not (t_match or c_match or a_match or act_match or why_match or what_match):
                continue

        # Filter by specific actor name (only if not already filtered via search_term)
        if actor and not search_term:
            if actor.lower() not in actor_name.lower():
                continue

        # Filter by priority
        if priority and intel.overall_priority != priority.upper():
            continue

        # Filter by behavior
        if behavior and intel.primary_behavior != behavior.upper():
            continue

        # Filter by action type
        if action_type and intel.primary_action_type != action_type:
            continue

        # Filter by actor role / classification
        if role and role.strip():
            target_role = role.strip().upper()
            act_role = (act.actor_type if act else "").upper()
            if target_role == "CONTROLLER" and not ("CONTROLLER" in act_role or "PSP" in act_role):
                continue
            elif target_role in ("DIRECTOR", "COMMISSIONER", "STRATEGIC_INVESTOR", "INSTITUTION") and target_role not in act_role:
                continue
            elif target_role not in ("CONTROLLER", "DIRECTOR", "COMMISSIONER", "STRATEGIC_INVESTOR", "INSTITUTION") and target_role != act_role:
                continue

        # Get behavior state
        beh_state = None
        if act:
            beh_state = session.exec(
                select(ActorBehaviorState)
                .where(ActorBehaviorState.company_id == comp.id)
                .where(ActorBehaviorState.actor_id == act.id)
            ).first()

        # Get action state
        action_state = None
        if intel.primary_action_type:
            action_state = session.exec(
                select(IssuerActionState)
                .where(IssuerActionState.company_id == comp.id)
                .where(IssuerActionState.action_type == intel.primary_action_type)
            ).first()

        cur_stage = action_state.current_stage if action_state else (beh_state.current_stage if beh_state else "DEVELOPING")
        cur_impact = action_state.current_impact if action_state else "POSITIVE"

        if stage and cur_stage != stage.upper():
            continue
        if impact and cur_impact != impact.upper():
            continue

        # Get latest document and evidence
        latest_doc = session.exec(
            select(Document).join(Announcement)
            .where(Announcement.company_id == comp.id)
            .order_by(Document.id.desc())
        ).first()

        evidence_list = []
        if latest_doc:
            evs = session.exec(
                select(Evidence)
                .where(Evidence.source_document_id == latest_doc.id)
                .limit(5)
            ).all()
            for ev in evs:
                evidence_list.append({
                    "page_number": ev.page_number,
                    "excerpt": ev.excerpt,
                    "evidence_type": ev.evidence_type
                })

        action_meta = ACTION_FAMILIES.get(intel.primary_action_type or "", {})

        results.append({
            "id": intel.id,
            "company_id": comp.id,
            "ticker": comp.ticker,
            "company_name": comp.name or comp.ticker,
            "sector": comp.sector or "",
            "primary_actor_id": act.id if act else None,
            "actor_name": act.canonical_name if act else "Pihak Terlapor",
            "actor_type": act.actor_type if act else "SIGNIFICANT_HOLDER",
            "behavior_type": intel.primary_behavior or "STRATEGIC_POSITIONING_CANDIDATE",
            "total_shares_delta": beh_state.total_shares_delta if beh_state else 0.0,
            "pct_before": beh_state.pct_before if beh_state else 0.0,
            "pct_after": beh_state.pct_after if beh_state else 0.0,
            "delta_pct": beh_state.delta_pct if beh_state else 0.0,
            "avg_price": beh_state.avg_price if beh_state else None,
            "transaction_count": beh_state.transaction_count if beh_state else 1,
            "action_type": intel.primary_action_type or (action_state.action_type if action_state else "INFORMASI_MATERIAL"),
            "action_name": action_meta.get("name", (intel.primary_action_type or (action_state.action_type if action_state else "Keterbukaan Informasi")).replace("_", " ")),
            "category": action_meta.get("category", "CORPORATE_DISCLOSURE"),
            "stage": cur_stage,
            "impact": cur_impact,
            "priority": intel.overall_priority,
            "smart_money_score": intel.smart_money_score,
            "strategic_positioning_score": intel.strategic_positioning_score,
            "corporate_transformation_score": intel.corporate_transformation_score,
            "corporate_action_score": intel.corporate_action_score,
            "alignment_score": intel.alignment_score,
            "strategic_actor_score": intel.strategic_actor_score,
            "ownership_behavior_score": intel.ownership_behavior_score,
            "concentration_score": intel.concentration_score,
            "evidence_quality_score": intel.evidence_quality_score,
            "lead_time_quality_score": intel.lead_time_quality_score,
            "hsc_flag": intel.hsc_flag,
            "free_float_pct": intel.free_float_pct,
            "transaction_to_public_lag_days": intel.transaction_to_public_lag_days,
            "first_public_lead_days": intel.first_public_lead_days,
            "first_alignment_lead_days": intel.first_alignment_lead_days,
            "first_positioning_lead_days": intel.first_positioning_lead_days,
            "lead_time_days": intel.lead_time_days,
            "corroborating_docs_count": intel.corroborating_docs_count,
            "why_flagged": intel.why_flagged_summary,
            "what_changed": intel.what_changed_summary or intel.current_summary,
            "quality_score": intel.quality_score,
            "quality_label": intel.quality_label,
            "opportunity_state": intel.opportunity_state,
            "shareholder_value_score": intel.shareholder_value_score,
            "positive_drivers_count": intel.positive_drivers_count,
            "red_flags_count": intel.red_flags_count,
            "last_signal_at": intel.updated_at,
            "latest_document_id": latest_doc.id if latest_doc else None,
            "evidence": evidence_list
        })

    # Sort priority hierarchy: VERY_HIGH -> HIGH -> MEDIUM -> LOW -> WATCH, then score desc
    priority_order = {"VERY_HIGH": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "WATCH": 4}
    results.sort(key=lambda x: (
        priority_order.get(x["priority"], 5),
        -x["smart_money_score"]
    ))

    return results


@router.get("/signals/{id}")
def get_signal_detail(id: int, session: Session = Depends(get_session)):
    """Returns full signal detail, actor profile, ownership history, and timeline (PRD v7.2)."""
    intel = session.get(IssuerIntelligenceState, id)
    if not intel:
        raise HTTPException(status_code=404, detail="Signal not found")

    comp = intel.company
    act = session.get(Actor, intel.primary_actor_id) if intel.primary_actor_id else None

    # Fetch ownership events for this company
    ow_events = session.exec(
        select(OwnershipEvent)
        .where(OwnershipEvent.company_id == comp.id)
        .order_by(OwnershipEvent.event_date.desc())
    ).all()

    ownership_history = [
        {
            "id": e.id,
            "actor_id": e.actor_id,
            "actor_name": e.actor.canonical_name if e.actor else "",
            "event_date": e.event_date,
            "transaction_date": e.transaction_date,
            "reporting_date": e.reporting_date,
            "publication_date": e.publication_date,
            "event_type": e.event_type,
            "shares_before": e.shares_before,
            "shares_after": e.shares_after,
            "delta_shares": e.delta_shares,
            "pct_before": e.pct_before,
            "pct_after": e.pct_after,
            "delta_pct": e.delta_pct,
            "transaction_price": e.transaction_price,
            "estimated_value": e.estimated_value,
            "transaction_type": e.transaction_type,
            "administrative_flag": e.administrative_flag,
            "related_party_flag": e.related_party_flag,
            "pledge_flag": e.pledge_flag,
            "context_classification": e.context_classification,
            "source_document_id": e.source_document_id
        }
        for e in ow_events
    ]

    # Fetch documents and build multi-signal timeline
    docs = session.exec(
        select(Document).join(Announcement)
        .where(Announcement.company_id == comp.id)
        .order_by(Announcement.published_at.asc())
    ).all()

    timeline_items = []
    all_evidence = []

    for d in docs:
        ann = d.announcement
        has_local = bool(d.local_path and Path(d.local_path).exists())
        timeline_items.append({
            "document_id": d.id,
            "event_date": ann.published_at if ann else datetime.utcnow(),
            "title": ann.title if ann else "",
            "category": ann.category if ann else "",
            "priority": d.document_priority,
            "pdf_url": d.pdf_url,
            "has_local_pdf": has_local
        })

        evs = session.exec(select(Evidence).where(Evidence.source_document_id == d.id).limit(5)).all()
        for ev in evs:
            all_evidence.append({
                "document_id": d.id,
                "announcement_title": ann.title if ann else "",
                "page_number": ev.page_number,
                "excerpt": ev.excerpt,
                "evidence_type": ev.evidence_type
            })

    # Limit to top 40 most relevant excerpts for high-performance rendering
    all_evidence = all_evidence[:40]

    # Fetch actor aliases, relationships, and investor classifications
    actor_aliases = []
    actor_relationships = []
    investor_classes = []
    beneficial_owner_info = None
    controller_info = None

    if act:
        aliases_db = session.exec(select(ActorAlias).where(ActorAlias.actor_id == act.id)).all()
        actor_aliases = [a.alias for a in aliases_db]

        rels_db = session.exec(select(ActorRelationship).where(ActorRelationship.actor_id == act.id)).all()
        for r in rels_db:
            rel_act = session.get(Actor, r.related_actor_id)
            actor_relationships.append({
                "relationship_type": r.relationship_type,
                "related_actor": rel_act.canonical_name if rel_act else f"Actor #{r.related_actor_id}"
            })

        ics = session.exec(select(InvestorClassification).where(InvestorClassification.actor_id == act.id)).all()
        investor_classes = [
            {"raw_class": ic.raw_class, "normalized_class": ic.normalized_class, "source": ic.source, "observed_at": ic.observed_at}
            for ic in ics
        ]

        if act.beneficial_owner_id:
            bo = session.get(Actor, act.beneficial_owner_id)
            if bo:
                beneficial_owner_info = {"id": bo.id, "name": bo.canonical_name, "actor_type": bo.actor_type}

        if act.controller_id:
            ctrl = session.get(Actor, act.controller_id)
            if ctrl:
                controller_info = {"id": ctrl.id, "name": ctrl.canonical_name, "actor_type": ctrl.actor_type}

    beh_state = None
    if act:
        beh_state = session.exec(
            select(ActorBehaviorState)
            .where(ActorBehaviorState.company_id == comp.id)
            .where(ActorBehaviorState.actor_id == act.id)
        ).first()

    action_state = None
    if intel.primary_action_type:
        action_state = session.exec(
            select(IssuerActionState)
            .where(IssuerActionState.company_id == comp.id)
            .where(IssuerActionState.action_type == intel.primary_action_type)
        ).first()

    action_meta = ACTION_FAMILIES.get(intel.primary_action_type or "", {})

    actor_name = act.canonical_name if act else "Pihak Terlapor"
    actor_type = act.actor_type if act else "SIGNIFICANT_HOLDER"
    behavior_type = intel.primary_behavior or "STRATEGIC_POSITIONING_CANDIDATE"
    action_type = intel.primary_action_type or (action_state.action_type if action_state else "INFORMASI_MATERIAL")
    action_name = action_meta.get("name", (intel.primary_action_type or (action_state.action_type if action_state else "Keterbukaan Informasi")).replace("_", " "))

    current_stage = action_state.current_stage if action_state else (beh_state.current_stage if beh_state else "DEVELOPING")
    current_impact = action_state.current_impact if action_state else "POSITIVE"

    # Fetch CorporateActionAssessment for company
    ca_assessment = session.exec(
        select(CorporateActionAssessment)
        .where(CorporateActionAssessment.company_id == comp.id)
        .order_by(CorporateActionAssessment.updated_at.desc())
    ).first()

    assessment_payload = None
    if ca_assessment:
        assessment_payload = {
            "id": ca_assessment.id,
            "issuer_action_state_id": ca_assessment.issuer_action_state_id,
            "action_type": ca_assessment.action_type,
            "likelihood_score": ca_assessment.likelihood_score,
            "likelihood_stage": ca_assessment.likelihood_stage,
            "quality_score": ca_assessment.quality_score,
            "quality_label": ca_assessment.quality_label,
            "shareholder_value_score": ca_assessment.shareholder_value_score,
            "risk_score": ca_assessment.risk_score,
            "confidence": ca_assessment.confidence,
            "opportunity_state": ca_assessment.opportunity_state,
            "scores_decomposition": {
                "strategic_rationale_score": ca_assessment.strategic_rationale_score,
                "capital_efficiency_score": ca_assessment.capital_efficiency_score,
                "funding_quality_score": ca_assessment.funding_quality_score,
                "asset_quality_score": ca_assessment.asset_quality_score,
                "control_alignment_score": ca_assessment.control_alignment_score,
                "pricing_attractiveness_score": ca_assessment.pricing_attractiveness_score,
                "execution_risk_score": ca_assessment.execution_risk_score,
                "related_party_risk_score": ca_assessment.related_party_risk_score,
                "distress_risk_score": ca_assessment.distress_risk_score,
                "dilution_score": ca_assessment.dilution_score
            },
            "dilution_pct": ca_assessment.dilution_pct,
            "new_share_ratio": ca_assessment.new_share_ratio,
            "subscription_price": ca_assessment.subscription_price,
            "use_of_proceeds": json.loads(ca_assessment.use_of_proceeds_json) if ca_assessment.use_of_proceeds_json else [],
            "recipients": json.loads(ca_assessment.recipients_json) if ca_assessment.recipients_json else {},
            "positive_drivers": json.loads(ca_assessment.positive_drivers_json) if ca_assessment.positive_drivers_json else [],
            "red_flags": json.loads(ca_assessment.red_flags_json) if ca_assessment.red_flags_json else [],
            "why_attractive": ca_assessment.why_attractive,
            "why_risky": ca_assessment.why_risky
        }

    return {
        "id": intel.id,
        "company_id": comp.id,
        "ticker": comp.ticker,
        "company_name": comp.name or comp.ticker,
        "sector": comp.sector or "",
        "priority": intel.overall_priority,
        "primary_actor_id": intel.primary_actor_id,
        "actor_name": actor_name,
        "actor_type": actor_type,
        "behavior_type": behavior_type,
        "action_type": action_type,
        "action_name": action_name,
        "stage": current_stage,
        "impact": current_impact,
        "smart_money_score": intel.smart_money_score,
        "strategic_positioning_score": intel.strategic_positioning_score,
        "corporate_transformation_score": intel.corporate_transformation_score,
        "corporate_action_score": intel.corporate_action_score,
        "alignment_score": intel.alignment_score,
        "strategic_actor_score": intel.strategic_actor_score,
        "ownership_behavior_score": intel.ownership_behavior_score,
        "concentration_score": intel.concentration_score,
        "evidence_quality_score": intel.evidence_quality_score,
        "lead_time_quality_score": intel.lead_time_quality_score,
        "hsc_flag": intel.hsc_flag,
        "free_float_pct": intel.free_float_pct,
        "lead_time_days": intel.lead_time_days,
        "transaction_to_public_lag_days": intel.transaction_to_public_lag_days,
        "first_public_lead_days": intel.first_public_lead_days,
        "first_alignment_lead_days": intel.first_alignment_lead_days,
        "first_positioning_lead_days": intel.first_positioning_lead_days,
        "total_shares_delta": beh_state.total_shares_delta if beh_state else 0.0,
        "pct_before": beh_state.pct_before if beh_state else 0.0,
        "pct_after": beh_state.pct_after if beh_state else 0.0,
        "delta_pct": beh_state.delta_pct if beh_state else 0.0,
        "avg_price": beh_state.avg_price if beh_state else None,
        "transaction_count": beh_state.transaction_count if beh_state else 1,
        "corroborating_docs_count": len(timeline_items),
        "last_signal_at": (intel.updated_at or intel.first_signal_at or datetime.utcnow()).isoformat(),
        "actor": {
            "id": act.id if act else None,
            "canonical_name": actor_name,
            "actor_type": actor_type,
            "domicile": act.domicile if act else "DOMESTIC",
            "aliases": actor_aliases,
            "relationships": actor_relationships,
            "investor_classes": investor_classes,
            "beneficial_owner": beneficial_owner_info,
            "controller": controller_info
        },
        "behavior": {
            "behavior_type": behavior_type,
            "total_shares_delta": beh_state.total_shares_delta if beh_state else 0.0,
            "pct_before": beh_state.pct_before if beh_state else 0.0,
            "pct_after": beh_state.pct_after if beh_state else 0.0,
            "delta_pct": beh_state.delta_pct if beh_state else 0.0,
            "avg_price": beh_state.avg_price if beh_state else None,
            "transaction_count": beh_state.transaction_count if beh_state else 1,
        },
        "structural_context": {
            "hsc_flag": intel.hsc_flag,
            "free_float_pct": intel.free_float_pct,
            "concentration_score": intel.concentration_score
        },
        "timing_integrity": {
            "transaction_to_public_lag_days": intel.transaction_to_public_lag_days,
            "first_public_lead_days": intel.first_public_lead_days,
            "first_alignment_lead_days": intel.first_alignment_lead_days,
            "first_positioning_lead_days": intel.first_positioning_lead_days,
            "first_signal_at": intel.first_signal_at.isoformat() if intel.first_signal_at else None,
            "explicit_action_at": intel.explicit_action_at.isoformat() if intel.explicit_action_at else None
        },
        "scores": {
            "smart_money_score": intel.smart_money_score,
            "strategic_positioning_score": intel.strategic_positioning_score,
            "corporate_transformation_score": intel.corporate_transformation_score,
            "corporate_action_score": intel.corporate_action_score,
            "alignment_score": intel.alignment_score,
            "strategic_actor_score": intel.strategic_actor_score,
            "ownership_behavior_score": intel.ownership_behavior_score,
            "concentration_score": intel.concentration_score,
            "evidence_quality_score": intel.evidence_quality_score,
            "lead_time_quality_score": intel.lead_time_quality_score,
            "overall_priority": intel.overall_priority,
            "lead_time_days": intel.lead_time_days
        },
        "corporate_action": {
            "action_type": action_type,
            "action_name": action_name,
            "category": action_meta.get("category", "CAPITAL_RAISING"),
            "lifecycle_stages": action_meta.get("lifecycle_stages", [])
        },
        "corporate_action_assessment": assessment_payload,
        "quality_score": intel.quality_score or (assessment_payload.get("quality_score") if assessment_payload else None),
        "quality_label": intel.quality_label or (assessment_payload.get("quality_label") if assessment_payload else None),
        "opportunity_state": intel.opportunity_state or (assessment_payload.get("opportunity_state") if assessment_payload else None),
        "shareholder_value_score": intel.shareholder_value_score or (assessment_payload.get("shareholder_value_score") if assessment_payload else None),
        "positive_drivers_count": intel.positive_drivers_count or (len(assessment_payload.get("positive_drivers", [])) if assessment_payload else 0),
        "red_flags_count": intel.red_flags_count or (len(assessment_payload.get("red_flags", [])) if assessment_payload else 0),
        "why_flagged": intel.why_flagged_summary,
        "what_changed": intel.what_changed_summary or intel.current_summary,
        "ownership_history": ownership_history,
        "timeline": timeline_items,
        "evidence": all_evidence
    }


@router.get("/corporate-action-assessments/{issuer_action_state_id}")
def get_corporate_action_assessment(
    issuer_action_state_id: int,
    session: Session = Depends(get_session)
):
    """Returns detailed PRD v7.3 assessment for a specific corporate action state."""
    assessment = session.exec(
        select(CorporateActionAssessment)
        .where(CorporateActionAssessment.issuer_action_state_id == issuer_action_state_id)
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Corporate action assessment not found")
    
    return {
        "id": assessment.id,
        "issuer_action_state_id": assessment.issuer_action_state_id,
        "company_id": assessment.company_id,
        "action_type": assessment.action_type,
        "likelihood_score": assessment.likelihood_score,
        "likelihood_stage": assessment.likelihood_stage,
        "quality_score": assessment.quality_score,
        "quality_label": assessment.quality_label,
        "shareholder_value_score": assessment.shareholder_value_score,
        "risk_score": assessment.risk_score,
        "confidence": assessment.confidence,
        "opportunity_state": assessment.opportunity_state,
        "scores_decomposition": {
            "strategic_rationale_score": assessment.strategic_rationale_score,
            "capital_efficiency_score": assessment.capital_efficiency_score,
            "funding_quality_score": assessment.funding_quality_score,
            "asset_quality_score": assessment.asset_quality_score,
            "control_alignment_score": assessment.control_alignment_score,
            "pricing_attractiveness_score": assessment.pricing_attractiveness_score,
            "execution_risk_score": assessment.execution_risk_score,
            "related_party_risk_score": assessment.related_party_risk_score,
            "distress_risk_score": assessment.distress_risk_score,
            "dilution_score": assessment.dilution_score
        },
        "dilution_pct": assessment.dilution_pct,
        "new_share_ratio": assessment.new_share_ratio,
        "subscription_price": assessment.subscription_price,
        "use_of_proceeds": json.loads(assessment.use_of_proceeds_json) if assessment.use_of_proceeds_json else [],
        "recipients": json.loads(assessment.recipients_json) if assessment.recipients_json else {},
        "positive_drivers": json.loads(assessment.positive_drivers_json) if assessment.positive_drivers_json else [],
        "red_flags": json.loads(assessment.red_flags_json) if assessment.red_flags_json else [],
        "why_attractive": assessment.why_attractive,
        "why_risky": assessment.why_risky,
        "updated_at": assessment.updated_at
    }


@router.get("/actors/{id}")
def get_actor_detail(id: int, session: Session = Depends(get_session)):
    """Returns actor profile, aliases, and historical transactions across issuers."""
    actor = session.get(Actor, id)
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")

    aliases = session.exec(select(ActorAlias).where(ActorAlias.actor_id == actor.id)).all()
    transactions = session.exec(
        select(TransactionEvent)
        .where(TransactionEvent.actor_id == actor.id)
        .order_by(TransactionEvent.event_date.desc())
    ).all()

    tx_list = []
    for tx in transactions:
        c = session.get(Company, tx.company_id)
        tx_list.append({
            "ticker": c.ticker if c else "",
            "company_name": c.name if c else "",
            "event_date": tx.event_date,
            "direction": tx.direction,
            "quantity": tx.quantity,
            "price": tx.price,
            "estimated_value": tx.estimated_value
        })

    return {
        "id": actor.id,
        "canonical_name": actor.canonical_name,
        "actor_type": actor.actor_type,
        "normalized_key": actor.normalized_key,
        "aliases": [a.alias for a in aliases],
        "transaction_history": tx_list
    }


@router.get("/companies/{ticker}/intelligence")
def get_company_intelligence(ticker: str, session: Session = Depends(get_session)):
    """Returns issuer-level intelligence state."""
    company = session.exec(select(Company).where(Company.ticker == ticker.upper())).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    intel = session.exec(
        select(IssuerIntelligenceState).where(IssuerIntelligenceState.company_id == company.id)
    ).first()

    return {
        "ticker": company.ticker,
        "name": company.name,
        "sector": company.sector,
        "intelligence": intel
    }


@router.get("/documents/{id}")
def get_document_detail(id: int, session: Session = Depends(get_session)):
    doc = session.get(Document, id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    ann = doc.announcement
    pages = session.exec(select(DocumentPage).where(DocumentPage.document_id == doc.id).order_by(DocumentPage.page_number.asc())).all()

    return {
        "id": doc.id,
        "announcement_id": doc.announcement_id,
        "title": ann.title if ann else "",
        "published_at": ann.published_at if ann else None,
        "pdf_url": doc.pdf_url,
        "local_path": doc.local_path,
        "sha256": doc.sha256,
        "document_priority": doc.document_priority,
        "extraction_status": doc.extraction_status,
        "page_count": doc.page_count,
        "pages": [{"page_number": p.page_number, "text": p.extracted_text} for p in pages]
    }


@router.get("/documents/{id}/pdf")
def stream_pdf(id: int, session: Session = Depends(get_session)):
    """Streams local PDF file for in-browser inspection."""
    doc = session.get(Document, id)
    if not doc or not doc.local_path:
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    path = Path(doc.local_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Local PDF file does not exist on disk")

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=f"disclosure_{doc.id}.pdf"
    )


@router.get("/action-families")
def get_action_families():
    """Returns list of all 18 corporate action families and 14 transformation families."""
    return {
        "corporate_actions": [
            {
                "key": k,
                "name": v["name"],
                "category": v.get("category", "GENERAL"),
                "lifecycle_stages": v.get("lifecycle_stages", [])
            }
            for k, v in ACTION_FAMILIES.items()
        ],
        "corporate_transformations": [
            {
                "key": k,
                "name": v["name"]
            }
            for k, v in TRANSFORMATION_FAMILIES.items()
        ]
    }


@router.get("/companies")
def get_all_companies(
    search: Optional[str] = Query(None),
    sector: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    """Returns list of registered IDX listed companies."""
    query = select(Company)
    if search:
        query = query.where(
            (Company.ticker.contains(search.upper())) |
            (Company.name.contains(search))
        )
    if sector:
        query = query.where(Company.sector == sector)
    
    companies = session.exec(query.order_by(Company.ticker.asc())).all()
    return [{"ticker": c.ticker, "name": c.name, "sector": c.sector} for c in companies]


@router.get("/data-source")
async def get_data_source_status():
    """Returns data source status and Playwright readiness."""
    from app.config import settings
    playwright_available = False
    try:
        import playwright
        playwright_available = True
    except ImportError:
        pass

    cookie_file = settings.data_dir / "idx_cookies.json"
    cookies_cached = cookie_file.exists()

    return {
        "source_mode": "IDX_LIVE_PLAYWRIGHT" if (playwright_available and cookies_cached) else ("IDX_LIVE" if playwright_available else "SAMPLE_CORPUS"),
        "source_label": "Live IDX BEI Data" if playwright_available else "Sample Corpus (v7.0 Engine)",
        "playwright_installed": playwright_available,
        "cloudflare_cookies_cached": cookies_cached
    }
