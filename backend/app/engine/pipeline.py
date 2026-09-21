import json
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from sqlmodel import Session, select

from app.models.schema import (
    Scan, Company, Actor, ActorAlias, Announcement, Document, DocumentPage,
    OwnershipEvent, TransactionEvent, DocumentSignal, Evidence,
    ActorBehaviorState, IssuerIntelligenceState, IssuerActionState, SignalEvent,
    InvestorClassification, MarketStructureSnapshot, CorporateActionAssessment
)
from app.engine.ca_quality_engine import CorporateActionQualityEngine
from app.ingestion.idx_client import IDXClient
from app.ingestion.downloader import download_pdfs_batch
from app.ingestion.bootstrap import run_historical_bootstrap
from app.extractor.pdf_parser import extract_pdf_content
from app.extractor.actor_normalizer import resolve_or_create_actor
from app.extractor.ownership_extractor import extract_ownership_facts_from_text
from app.extractor.transformation_extractor import extract_transformation_signals
from app.rules.action_detector import detect_signals_in_document
from app.rules.importance_engine import evaluate_information_importance
from app.engine.document_router import classify_document_priority, is_impossible_corporate_action
from app.engine.positioning_engine import cluster_actor_behavior
from app.engine.cross_signal_engine import (
    calculate_strategic_actor_score,
    calculate_ownership_behavior_score,
    calculate_concentration_context_score,
    calculate_corporate_transformation_score,
    calculate_corporate_action_prep_score,
    calculate_market_anomaly_score,
    calculate_evidence_quality_score,
    calculate_lead_time_quality_score,
    calculate_alignment_score,
    calculate_decomposed_smart_money_score,
    calculate_lead_time_metrics
)
from app.engine.novelty_tracker import determine_novelty_class, build_what_changed_summary
from app.engine.corroborator import evaluate_corroboration
from app.engine.lifecycle_manager import determine_issuer_action_stage
from app.engine.impact_evaluator import evaluate_economic_impact
from app.engine.ranker import calculate_priority_score, get_priority_label


def _update_progress(
    session: Session,
    scan: Scan,
    stage_message: str,
    progress_percent: int,
    extra_summary: Optional[Dict[str, Any]] = None
):
    """Updates live scan progress in database."""
    try:
        current_data = json.loads(scan.summary_json) if scan.summary_json else {}
        current_data["stage_message"] = stage_message
        current_data["progress_percent"] = min(99, max(1, progress_percent))
        if extra_summary:
            current_data.update(extra_summary)
        scan.summary_json = json.dumps(current_data)
        session.add(scan)
        session.commit()
        session.refresh(scan)
    except Exception as e:
        print(f"[Pipeline] Progress update error: {e}")


async def _download_and_extract_batch(
    doc_tasks: List[Dict[str, Any]],
    cached_docs: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Batch download and extract PDFs, leveraging local cache when available."""
    cached_map = cached_docs or {}
    tasks_to_download = []
    results = []

    for item in doc_tasks:
        url = item.get("url", "")
        if url and url in cached_map:
            c = cached_map[url]
            results.append({
                **item,
                "success": True,
                "dl_status": "CACHED",
                "sha256": c["sha256"],
                "local_path": c["local_path"],
                "extracted": None
            })
        else:
            tasks_to_download.append(item)

    if tasks_to_download:
        urls = [item.get("url", "") for item in tasks_to_download if item.get("url")]
        dl_results = await download_pdfs_batch(urls)

        for item in tasks_to_download:
            url = item.get("url", "")
            success, dl_status, sha256, local_path = dl_results.get(url, (False, "NO_URL", None, None))
            extracted = None
            if success and local_path and Path(local_path).exists():
                try:
                    extracted = extract_pdf_content(Path(local_path))
                except Exception as e:
                    print(f"[Pipeline] Extraction error for {url}: {e}")
            results.append({
                **item,
                "success": success,
                "dl_status": dl_status,
                "sha256": sha256,
                "local_path": local_path,
                "extracted": extracted
            })

    return results


async def execute_screening_pipeline(
    session: Session,
    scan_from: datetime,
    scan_to: datetime,
    lookback_days: int = 60,
    scan_mode: str = "smart",
    scan_id: Optional[int] = None
) -> Scan:
    """
    Executes the v7.0 IDX Strategic Ownership, Smart Money & Corporate Transformation Pipeline.
    """
    if scan_id:
        scan = session.get(Scan, scan_id)
        if not scan:
            scan = Scan(scan_from=scan_from, scan_to=scan_to, lookback_days=lookback_days, scan_mode=scan_mode, status="RUNNING")
            session.add(scan)
            session.commit()
            session.refresh(scan)
    else:
        scan = Scan(
            scan_from=scan_from,
            scan_to=scan_to,
            lookback_days=lookback_days,
            scan_mode=scan_mode,
            status="RUNNING"
        )
        session.add(scan)
        session.commit()
        session.refresh(scan)

    try:
        # Step 1: Bootstrap companies registry
        _update_progress(session, scan, "Checking master IDX companies registry...", 5)
        bootstrap_done = await run_historical_bootstrap(session, lookback_days)
        scan.bootstrap_performed = bootstrap_done

        # Step 2: Retrieve announcements from IDX
        _update_progress(session, scan, "Retrieving IDX announcement metadata...", 15)
        idx_client = IDXClient()
        announcements_data = await idx_client.fetch_announcements(scan_from, scan_to)
        scan.announcements_found = len(announcements_data)
        session.add(scan)
        session.commit()

        if not announcements_data:
            _update_progress(session, scan, "No announcements found for selected date range.", 100)
            scan.completed_at = datetime.now(timezone.utc)
            scan.status = "COMPLETED"
            scan.summary_json = json.dumps({
                "stage_message": "Screening completed. No announcements found.",
                "progress_percent": 100,
                "announcements_retrieved": 0,
                "tier_a_documents": 0,
                "tier_b_documents": 0,
                "tier_c_metadata_only": 0,
                "documents_processed": 0,
                "ownership_events": 0,
                "high_priority_signals": 0
            })
            session.add(scan)
            session.commit()
            return scan

        # Step 3: Document Priority Routing (PRD Section 8)
        _update_progress(session, scan, "Routing disclosures by document intelligence priority (Tier A/B/C/D)...", 25)
        
        processed_announcements = []
        download_queue = []
        tier_a_count = 0
        tier_b_count = 0
        tier_c_count = 0

        for ann_data in announcements_data:
            ticker = ann_data["ticker"]
            company = session.exec(select(Company).where(Company.ticker == ticker)).first()
            if not company:
                company = Company(
                    ticker=ticker,
                    name=ann_data.get("name", ticker),
                    sector=ann_data.get("sector")
                )
                session.add(company)
                session.commit()
                session.refresh(company)

            src_id = ann_data["source_id"]
            existing_ann = session.exec(
                select(Announcement).where(Announcement.source_announcement_id == src_id)
            ).first()

            tier, _ = classify_document_priority(
                title=ann_data["title"],
                category=ann_data.get("category", ""),
                scan_mode=scan_mode
            )

            if tier == "TIER_A":
                tier_a_count += 1
            elif tier == "TIER_B":
                tier_b_count += 1
            else:
                tier_c_count += 1

            # PRD v5 All-Stock-Disclosure Acquisition:
            # Check if title is impossible to contain a corporate action (ad proofs, daily FX, non-stock debt)
            impossible = is_impossible_corporate_action(ann_data["title"], ann_data.get("category", ""))

            attachments = ann_data.get("attachments", [])
            if not attachments and "pdf_path" in ann_data:
                attachments = [{"url": str(ann_data["pdf_path"])}]

            # Under PRD v5: ALL stock disclosures with attachments are downloaded and deep-extracted
            # UNLESS the title is an impossible corporate action (ad proofs, daily FX, non-stock).
            should_deep = (not impossible) and bool(attachments)

            if not existing_ann:
                processing_state = f"{tier}_DEEP" if should_deep else ("EXCLUDED_ADMIN_NOISE" if impossible else "PROCESSED_METADATA_ONLY")
                announcement = Announcement(
                    company_id=company.id,
                    source_announcement_id=src_id,
                    title=ann_data["title"],
                    category=ann_data.get("category"),
                    published_at=ann_data["published_at"],
                    status="PENDING",
                    processing_state=processing_state,
                    is_historical_context=False
                )
                session.add(announcement)
                session.commit()
                session.refresh(announcement)
            else:
                announcement = existing_ann

            processed_announcements.append({
                "announcement": announcement,
                "company": company,
                "ann_data": ann_data,
                "attachments": attachments,
                "tier": tier,
                "should_deep": should_deep,
                "is_impossible": impossible
            })

            if should_deep:
                for att in attachments:
                    url = att.get("url", "")
                    if url:
                        download_queue.append({
                            "announcement_id": announcement.id,
                            "company_id": company.id,
                            "ticker": company.ticker,
                            "title": announcement.title,
                            "published_at": announcement.published_at,
                            "url": url,
                            "tier": tier
                        })

        scan.tier_a_documents = tier_a_count
        scan.tier_b_documents = tier_b_count
        scan.tier_c_metadata_only = tier_c_count
        session.add(scan)
        session.commit()

        # Step 4: Batch Concurrent Download & Extraction for Stock Filings (PRD v5 All-Disclosure Acquisition)
        total_download_items = len(download_queue)
        _update_progress(
            session, scan,
            f"Downloading & parsing {total_download_items} stock disclosure filings (Tier A: {tier_a_count}, Tier B: {tier_b_count}, Tier C: {tier_c_count})...",
            40
        )

        # Build local DB document cache to avoid re-downloading already processed PDFs
        existing_db_docs = session.exec(
            select(Document).where(Document.pdf_url.is_not(None))
        ).all()
        cached_docs = {}
        for d in existing_db_docs:
            if d.pdf_url and d.local_path and Path(d.local_path).exists():
                cached_docs[d.pdf_url] = {
                    "sha256": d.sha256,
                    "local_path": Path(d.local_path),
                }

        chunk_size = 40
        extracted_results = []
        for chunk_idx in range(0, max(1, total_download_items), chunk_size):
            chunk = download_queue[chunk_idx:chunk_idx + chunk_size]
            if chunk:
                batch_res = await _download_and_extract_batch(chunk, cached_docs)
                extracted_results.extend(batch_res)
                pct = 40 + int(35 * (len(extracted_results) / max(1, total_download_items)))
                _update_progress(
                    session, scan,
                    f"Parsed {len(extracted_results)} of {total_download_items} stock disclosure filings...",
                    pct
                )

        results_by_ann = {(r["announcement_id"], r["url"]): r for r in extracted_results}

        # Step 5: Multi-Layer Document Analysis (Actions, Ownership, Transformations)
        _update_progress(session, scan, "Extracting ownership facts, transformations, and corporate action lifecycles...", 78)

        ownership_events_total = 0
        companies_touched = set()

        for p_item in processed_announcements:
            announcement = p_item["announcement"]
            company = p_item["company"]
            attachments = p_item["attachments"]
            should_deep = p_item["should_deep"]
            tier = p_item["tier"]
            is_impossible = p_item.get("is_impossible", False)
            companies_touched.add(company.id)

            if not attachments or not should_deep:
                announcement.status = "EXCLUDED_ADMIN_NOISE" if is_impossible else "PROCESSED_METADATA_ONLY"
                session.add(announcement)
                session.commit()
                continue

            for att in attachments:
                url = att.get("url", "")
                r_item = results_by_ann.get((announcement.id, url))
                if not r_item or not r_item.get("success"):
                    continue

                sha256 = r_item.get("sha256")
                local_path = r_item.get("local_path")
                ext_res = r_item.get("extracted")

                existing_doc = None
                if sha256:
                    existing_doc = session.exec(select(Document).where(Document.sha256 == sha256)).first()

                if existing_doc and existing_doc.pages:
                    doc = existing_doc
                    extracted_pages = [{"page_number": p.page_number, "normalized_text": p.extracted_text} for p in existing_doc.pages]
                else:
                    doc = Document(
                        announcement_id=announcement.id,
                        pdf_url=url,
                        local_path=str(local_path) if local_path else None,
                        sha256=sha256,
                        document_priority=tier,
                        acquisition_status="DOWNLOADED",
                        extraction_status=ext_res.status if ext_res else "SKIPPED",
                        processed_at=datetime.now(timezone.utc),
                        page_count=ext_res.page_count if ext_res else 0
                    )
                    session.add(doc)
                    session.commit()
                    session.refresh(doc)

                    extracted_pages = []
                    if ext_res and ext_res.pages:
                        for p in ext_res.pages:
                            d_page = DocumentPage(
                                document_id=doc.id,
                                page_number=p["page_number"],
                                extracted_text=p["normalized_text"]
                            )
                            session.add(d_page)
                            extracted_pages.append(p)
                        session.commit()

                full_text = " ".join(p.get("normalized_text", "") for p in extracted_pages)

                # A. Extract Ownership Facts (PRD Section 12-15)
                ownership_facts = extract_ownership_facts_from_text(
                    full_text=full_text,
                    title=announcement.title,
                    published_date=announcement.published_at
                )

                for fact in ownership_facts:
                    actor, _ = resolve_or_create_actor(
                        session=session,
                        raw_name=fact["actor_name"],
                        context_text=full_text,
                        domicile=fact.get("domicile"),
                        beneficial_owner_name=fact.get("beneficial_owner_name"),
                        controller_name=fact.get("controller_name"),
                        raw_class=fact.get("raw_investor_class"),
                        normalized_class=fact.get("normalized_investor_class"),
                        source_doc_id=doc.id
                    )

                    # Save Market Structure Snapshot if HSC or Free Float disclosed
                    if fact.get("hsc_flag") or fact.get("free_float_pct") is not None:
                        mss = MarketStructureSnapshot(
                            company_id=company.id,
                            observation_date=fact.get("publication_date") or announcement.published_at,
                            hsc_flag=fact.get("hsc_flag", False),
                            free_float_pct=fact.get("free_float_pct"),
                            source_document_id=doc.id
                        )
                        session.add(mss)
                        session.commit()

                    ow_ev = OwnershipEvent(
                        company_id=company.id,
                        actor_id=actor.id,
                        event_date=fact["event_date"],
                        transaction_date=fact.get("transaction_date"),
                        reporting_date=fact.get("reporting_date"),
                        publication_date=fact.get("publication_date"),
                        event_type=fact["direction"],
                        shares_before=fact["shares_before"],
                        shares_after=fact["shares_after"],
                        delta_shares=fact["delta_shares"],
                        pct_before=fact["pct_before"],
                        pct_after=fact["pct_after"],
                        delta_pct=fact["delta_pct"],
                        transaction_price=fact["price"],
                        estimated_value=fact["estimated_value"],
                        transaction_type=fact.get("transaction_type"),
                        administrative_flag=fact.get("administrative_flag", False),
                        related_party_flag=fact.get("related_party_flag", False),
                        pledge_flag=fact.get("pledge_flag", False),
                        source_document_id=doc.id,
                        context_classification=fact["context_classification"],
                        confidence=fact["confidence"]
                    )
                    session.add(ow_ev)
                    session.commit()

                    tx_ev = TransactionEvent(
                        company_id=company.id,
                        actor_id=actor.id,
                        event_date=fact.get("transaction_date") or fact["event_date"],
                        direction=fact["direction"],
                        quantity=fact["delta_shares"],
                        price=fact["price"],
                        estimated_value=fact["estimated_value"],
                        source_document_id=doc.id
                    )
                    session.add(tx_ev)
                    session.commit()

                    # Save Ownership Evidence
                    ev_excerpt = f"{actor.canonical_name} ({fact['direction']}): {fact['delta_shares']:,.0f} saham ({fact['pct_before']:.2f}% -> {fact['pct_after']:.2f}%)"
                    if fact["price"]:
                        ev_excerpt += f" @ Rp {fact['price']:,.0f}"
                    if fact.get("pledge_flag"):
                        ev_excerpt += " [PLEDGE/FINANCING]"
                    if fact.get("administrative_flag"):
                        ev_excerpt += " [ADMINISTRATIVE]"
                    ow_evidence = Evidence(
                        source_document_id=doc.id,
                        page_number=1,
                        excerpt=ev_excerpt,
                        evidence_type="OWNERSHIP"
                    )
                    session.add(ow_evidence)
                    session.commit()
                    ownership_events_total += 1

                # B. Extract Corporate Actions (PRD Section 22-23)
                signals_detected = detect_signals_in_document(announcement.title, extracted_pages)
                imp_res = evaluate_information_importance(announcement.title, full_text, signals_detected)

                for sig in signals_detected:
                    action_type = sig["action_type"]
                    action_state = session.exec(
                        select(IssuerActionState)
                        .where(IssuerActionState.company_id == company.id)
                        .where(IssuerActionState.action_type == action_type)
                    ).first()

                    prior_events_db = []
                    if action_state:
                        prior_events_db = session.exec(
                            select(SignalEvent)
                            .where(SignalEvent.issuer_action_state_id == action_state.id)
                            .order_by(SignalEvent.event_date.asc())
                        ).all()

                    prior_events = [{"event_date": ev.event_date, "lifecycle_stage": ev.lifecycle_stage, "signal_type": ev.signal_type, "contribution": ev.contribution} for ev in prior_events_db]
                    novelty_cls = determine_novelty_class(sig, prior_events)

                    doc_signal = DocumentSignal(
                        document_id=doc.id,
                        action_type=action_type,
                        information_importance=imp_res["importance"],
                        novelty_type=novelty_cls,
                        impact=sig["impact"],
                        stage=sig["stage"],
                        strength=sig["strength"],
                        confidence=sig["confidence"],
                        lifecycle_stage=sig.get("lifecycle_stage"),
                        reason=sig["reason"],
                        is_negated=sig.get("is_negated", False),
                        is_cancelled=sig.get("is_cancelled", False),
                        is_distress=sig.get("is_distress", False)
                    )
                    session.add(doc_signal)
                    session.commit()
                    session.refresh(doc_signal)

                    for ev in sig.get("evidence_items", []):
                        ev_record = Evidence(
                            document_signal_id=doc_signal.id,
                            source_document_id=doc.id,
                            page_number=ev["page_number"],
                            excerpt=ev["excerpt"],
                            evidence_type=ev.get("evidence_type", "TRIGGER")
                        )
                        session.add(ev_record)
                    session.commit()

                    if not action_state:
                        action_state = IssuerActionState(
                            company_id=company.id,
                            action_type=action_type,
                            current_stage=sig["stage"],
                            current_impact=sig["impact"],
                            current_strength=sig["strength"],
                            current_confidence=sig["confidence"],
                            priority="MEDIUM",
                            first_signal_at=announcement.published_at,
                            last_signal_at=announcement.published_at,
                            state_status="ACTIVE",
                            corroborating_docs_count=1
                        )
                        session.add(action_state)
                        session.commit()
                        session.refresh(action_state)

                    sig_event = SignalEvent(
                        issuer_action_state_id=action_state.id,
                        document_id=doc.id,
                        event_date=announcement.published_at,
                        lifecycle_stage=sig.get("lifecycle_stage", "PRECURSOR"),
                        signal_type=sig["stage"],
                        contribution=novelty_cls,
                        status="ACTIVE"
                    )
                    session.add(sig_event)
                    session.commit()

                    # Re-evaluate stage and corroboration
                    all_events = session.exec(
                        select(SignalEvent).where(SignalEvent.issuer_action_state_id == action_state.id)
                    ).all()
                    event_dicts = [{"event_date": e.event_date, "lifecycle_stage": e.lifecycle_stage, "signal_type": e.signal_type, "contribution": e.contribution, "is_negated": sig.get("is_negated", False), "is_cancelled": sig.get("is_cancelled", False)} for e in all_events]
                    stage_res = determine_issuer_action_stage(event_dicts, lookback_days)
                    corrob_res = evaluate_corroboration(action_type, event_dicts)

                    has_pos = sig["impact"] == "POSITIVE"
                    has_dist = sig.get("is_distress", False)
                    final_impact = evaluate_economic_impact(action_type, stage_res["stage"], has_pos, has_dist, sig.get("is_negated", False), sig.get("is_cancelled", False))
                    p_score = calculate_priority_score(stage_res["stage"], final_impact, imp_res["importance"], corrob_res["doc_count"], stage_res["state_status"])

                    action_state.current_stage = stage_res["stage"]
                    action_state.current_impact = final_impact
                    action_state.current_strength = stage_res["strength"]
                    action_state.current_confidence = stage_res["confidence"]
                    action_state.priority = get_priority_label(p_score)
                    action_state.state_status = stage_res["state_status"]
                    action_state.last_signal_at = announcement.published_at
                    action_state.corroborating_docs_count = corrob_res["doc_count"]
                    action_state.why_flagged_summary = stage_res["why_flagged"]
                    action_state.what_changed_summary = build_what_changed_summary(event_dicts)
                    session.add(action_state)
                    session.commit()

                announcement.status = "PROCESSED_PDF"
                session.add(announcement)
                session.commit()

        # Step 6: Issuer Intelligence & Cross-Signal Scoring (PRD Section 4.1 & 25-26)
        _update_progress(session, scan, "Computing cross-signal alignment, actor clusters, and composite intelligence scores...", 90)

        strategic_candidates_count = 0

        for comp_id in companies_touched:
            company = session.get(Company, comp_id)
            if not company:
                continue

            # 1. Fetch ownership events for company
            comp_ow_events = session.exec(
                select(OwnershipEvent)
                .where(OwnershipEvent.company_id == comp_id)
                .order_by(OwnershipEvent.event_date.asc())
            ).all()

            # Group by actor
            events_by_actor: Dict[int, List[Dict[str, Any]]] = {}
            for ev in comp_ow_events:
                events_by_actor.setdefault(ev.actor_id, []).append({
                    "event_date": ev.event_date,
                    "transaction_date": ev.transaction_date,
                    "publication_date": ev.publication_date,
                    "direction": ev.event_type,
                    "delta_shares": ev.delta_shares,
                    "pct_before": ev.pct_before,
                    "pct_after": ev.pct_after,
                    "delta_pct": ev.delta_pct,
                    "price": ev.transaction_price,
                    "context_classification": ev.context_classification,
                    "administrative_flag": ev.administrative_flag,
                    "pledge_flag": ev.pledge_flag
                })

            best_actor_id = None
            best_cluster = None
            max_pos_score = 0
            best_act_score = 0
            best_beh_score = 0

            for act_id, ev_list in events_by_actor.items():
                actor = session.get(Actor, act_id)
                cluster = cluster_actor_behavior(act_id, comp_id, ev_list)
                act_score = calculate_strategic_actor_score(
                    actor_type=actor.actor_type if actor else "OTHER",
                    domicile=actor.domicile if actor else "DOMESTIC",
                    has_relationships=bool(actor and actor.aliases)
                )
                beh_score = calculate_ownership_behavior_score(cluster)
                p_score = (act_score + beh_score) // 2

                if p_score >= max_pos_score or best_actor_id is None:
                    max_pos_score = p_score
                    best_actor_id = act_id
                    best_cluster = cluster
                    best_act_score = act_score
                    best_beh_score = beh_score

                # Persist ActorBehaviorState
                beh_state = session.exec(
                    select(ActorBehaviorState)
                    .where(ActorBehaviorState.company_id == comp_id)
                    .where(ActorBehaviorState.actor_id == act_id)
                ).first()

                if not beh_state:
                    beh_state = ActorBehaviorState(
                        company_id=comp_id,
                        actor_id=act_id,
                        behavior_type=cluster["behavior_type"],
                        current_stage="DEVELOPING" if cluster["transaction_count"] > 1 else "EARLY",
                        priority="HIGH" if p_score >= 65 else ("MEDIUM" if p_score >= 40 else "LOW"),
                        confidence="HIGH",
                        total_shares_delta=cluster["total_shares_delta"],
                        pct_before=cluster["pct_before"],
                        pct_after=cluster["pct_after"],
                        delta_pct=cluster["delta_pct"],
                        avg_price=cluster["avg_price"],
                        transaction_count=cluster["transaction_count"],
                        first_signal_at=cluster.get("first_date", datetime.utcnow()),
                        last_signal_at=cluster.get("last_date", datetime.utcnow())
                    )
                else:
                    beh_state.behavior_type = cluster["behavior_type"]
                    beh_state.total_shares_delta = cluster["total_shares_delta"]
                    beh_state.pct_before = cluster["pct_before"]
                    beh_state.pct_after = cluster["pct_after"]
                    beh_state.delta_pct = cluster["delta_pct"]
                    beh_state.avg_price = cluster["avg_price"]
                    beh_state.transaction_count = cluster["transaction_count"]
                    beh_state.priority = "HIGH" if p_score >= 65 else ("MEDIUM" if p_score >= 40 else "LOW")
                    beh_state.last_signal_at = cluster.get("last_date", datetime.utcnow())

                session.add(beh_state)
                session.commit()

            if max_pos_score >= 50:
                strategic_candidates_count += 1

            # 2. Corporate Actions for Company
            # 2. Corporate Actions for Company & Corporate Action Quality (PRD v7.3 Patch)
            comp_actions = session.exec(
                select(IssuerActionState)
                .where(IssuerActionState.company_id == comp_id)
                .where(IssuerActionState.state_status == "ACTIVE")
            ).all()

            action_dicts = [{"stage": a.current_stage, "impact": a.current_impact, "corroborating_docs_count": a.corroborating_docs_count} for a in comp_actions]
            ca_score = calculate_corporate_action_prep_score(action_dicts)

            # Evaluate Corporate Action Quality & Shareholder Value (PRD v7.3)
            ca_q_engine = CorporateActionQualityEngine()
            primary_qa = None
            for a_state in comp_actions:
                # Find document texts associated with this corporate action
                action_events = session.exec(
                    select(SignalEvent).where(SignalEvent.issuer_action_state_id == a_state.id)
                ).all()
                doc_ids = [e.document_id for e in action_events if e.document_id]
                ca_text = ""
                if doc_ids:
                    ca_docs = session.exec(select(Document).where(Document.id.in_(doc_ids))).all()
                    ca_text = " ".join(" ".join(p.extracted_text for p in d.pages) for d in ca_docs)
                if not ca_text and comp_docs:
                    ca_text = " ".join(" ".join(p.extracted_text for p in d.pages) for d in comp_docs[:3])

                qa_result = ca_q_engine.evaluate_quality(
                    document_text=ca_text,
                    action_type=a_state.action_type,
                    lifecycle_stage=a_state.current_stage,
                    likelihood_score=80.0 if a_state.current_stage == "EXPLICIT" else (65.0 if a_state.current_stage == "DEVELOPING" else 40.0)
                )

                # Persist CorporateActionAssessment
                ca_assessment = session.exec(
                    select(CorporateActionAssessment)
                    .where(CorporateActionAssessment.issuer_action_state_id == a_state.id)
                ).first()

                if not ca_assessment:
                    ca_assessment = CorporateActionAssessment(
                        issuer_action_state_id=a_state.id,
                        company_id=comp_id,
                        action_type=a_state.action_type
                    )

                ca_assessment.likelihood_score = qa_result["likelihood_score"]
                ca_assessment.likelihood_stage = qa_result["likelihood_stage"]
                ca_assessment.quality_score = qa_result["quality_score"]
                ca_assessment.quality_label = qa_result["quality_label"]
                ca_assessment.shareholder_value_score = qa_result["shareholder_value_score"]
                ca_assessment.risk_score = qa_result["risk_score"]
                ca_assessment.confidence = qa_result["confidence"]
                ca_assessment.opportunity_state = qa_result["opportunity_state"]
                
                decomp = qa_result["scores_decomposition"]
                ca_assessment.strategic_rationale_score = decomp["strategic_rationale_score"]
                ca_assessment.capital_efficiency_score = decomp["capital_efficiency_score"]
                ca_assessment.funding_quality_score = decomp["funding_quality_score"]
                ca_assessment.asset_quality_score = decomp["asset_quality_score"]
                ca_assessment.control_alignment_score = decomp["control_alignment_score"]
                ca_assessment.pricing_attractiveness_score = decomp["pricing_attractiveness_score"]
                ca_assessment.execution_risk_score = decomp["execution_risk_score"]
                ca_assessment.related_party_risk_score = decomp["related_party_risk_score"]
                ca_assessment.distress_risk_score = decomp["distress_risk_score"]
                ca_assessment.dilution_score = decomp["dilution_score"]

                ca_assessment.dilution_pct = qa_result["dilution_pct"]
                ca_assessment.new_share_ratio = qa_result["new_share_ratio"]
                ca_assessment.subscription_price = qa_result["subscription_price"]
                ca_assessment.use_of_proceeds_json = json.dumps(qa_result["use_of_proceeds"])
                ca_assessment.recipients_json = json.dumps(qa_result["recipients"])
                ca_assessment.positive_drivers_json = json.dumps(qa_result["positive_drivers"])
                ca_assessment.red_flags_json = json.dumps(qa_result["red_flags"])
                ca_assessment.why_attractive = qa_result["why_attractive"]
                ca_assessment.why_risky = qa_result["why_risky"]
                ca_assessment.updated_at = datetime.utcnow()

                session.add(ca_assessment)
                session.commit()

                if not primary_qa:
                    primary_qa = qa_result

            # 3. Transformations for Company (from announcements text)
            comp_docs = session.exec(
                select(Document).join(Announcement).where(Announcement.company_id == comp_id)
            ).all()

            all_trans = []
            has_vol = False
            for d in comp_docs:
                full_doc_text = " ".join(p.extracted_text for p in d.pages)
                t_signals = extract_transformation_signals(full_doc_text, d.announcement.title if d.announcement else "")
                all_trans.extend(t_signals)
                if d.announcement and any(k in d.announcement.title.lower() for k in ["volatilitas", "unusual", "uma"]):
                    has_vol = True

            trans_score = calculate_corporate_transformation_score(all_trans)

            # 4. Market Structure (HSC & Free Float) Context
            latest_mss = session.exec(
                select(MarketStructureSnapshot)
                .where(MarketStructureSnapshot.company_id == comp_id)
                .order_by(MarketStructureSnapshot.observation_date.desc())
            ).first()

            comp_hsc = latest_mss.hsc_flag if latest_mss else False
            comp_ff = latest_mss.free_float_pct if latest_mss else None
            conc_score = calculate_concentration_context_score(comp_hsc, comp_ff)
            anomaly_score = calculate_market_anomaly_score(is_volatility=has_vol)
            ev_score = calculate_evidence_quality_score(len(comp_docs), has_exact_price=bool(best_cluster and best_cluster.get("avg_price")))

            # 5. Lead Time & Timing Integrity Metrics (PRD Section 10 & 11)
            first_sig_date = None
            expl_date = None
            for a in comp_actions:
                if not first_sig_date or a.first_signal_at < first_sig_date:
                    first_sig_date = a.first_signal_at
                if a.current_stage == "EXPLICIT" and (not expl_date or a.last_signal_at < expl_date):
                    expl_date = a.last_signal_at

            earliest_pos_date = best_cluster.get("earliest_public_date") if best_cluster else None
            if earliest_pos_date:
                if not first_sig_date or earliest_pos_date < first_sig_date:
                    first_sig_date = earliest_pos_date

            first_align_date = None
            if earliest_pos_date and comp_actions:
                first_align_date = max(earliest_pos_date, comp_actions[0].first_signal_at)

            earliest_tx_date = best_cluster.get("earliest_tx_date") if best_cluster else None
            lead_metrics = calculate_lead_time_metrics(
                earliest_public_date=first_sig_date,
                earliest_positioning_date=earliest_pos_date,
                first_alignment_date=first_align_date,
                explicit_ca_date=expl_date,
                transaction_date=earliest_tx_date
            )
            lead_days = lead_metrics["first_public_lead_days"]
            lt_qual_score = calculate_lead_time_quality_score(lead_metrics["transaction_to_public_lag_days"], lead_days)

            # 6. Decomposed Composite Scoring (PRD Section 21)
            total_docs_count = len(comp_docs)
            sm_score, overall_band, decomposed = calculate_decomposed_smart_money_score(
                strategic_actor_score=best_act_score,
                ownership_behavior_score=best_beh_score,
                concentration_score=conc_score,
                corporate_transformation_score=trans_score,
                corporate_action_score=ca_score,
                market_anomaly_score=anomaly_score,
                evidence_quality_score=ev_score,
                lead_time_quality_score=lt_qual_score,
                corroboration_docs_count=total_docs_count
            )

            # 7. Save IssuerIntelligenceState (with v7.3 quality indicators)
            intel_state = session.exec(
                select(IssuerIntelligenceState).where(IssuerIntelligenceState.company_id == comp_id)
            ).first()

            primary_act = session.get(Actor, best_actor_id) if best_actor_id else None
            primary_ca = comp_actions[0].action_type if comp_actions else None

            summary_text = f"{company.ticker}: "
            if primary_act and best_cluster:
                summary_text += f"{best_cluster['behavior_type'].replace('_', ' ').title()} by {primary_act.canonical_name}"
                if best_cluster.get('total_shares_delta'):
                    summary_text += f" ({best_cluster['total_shares_delta']:+,.0f} shares)"
            if primary_ca:
                summary_text += f" | Action: {primary_ca.replace('_', ' ').title()}"
            if comp_hsc:
                summary_text += " [HSC Context]"

            why_text = (
                f"Smart Money {sm_score}/100 | Actor: {best_act_score}, Behavior: {best_beh_score}, "
                f"Concentration: {conc_score}, CA Prep: {ca_score}, Trans: {trans_score}, Align: {decomposed['alignment_score']}"
            )

            primary_q_score = primary_qa["quality_score"] if primary_qa else None
            primary_q_label = primary_qa["quality_label"] if primary_qa else None
            primary_opp_state = primary_qa["opportunity_state"] if primary_qa else None
            primary_sv_score = primary_qa["shareholder_value_score"] if primary_qa else None
            primary_pos_count = len(primary_qa["positive_drivers"]) if primary_qa else 0
            primary_red_count = len(primary_qa["red_flags"]) if primary_qa else 0

            if not intel_state:
                intel_state = IssuerIntelligenceState(
                    company_id=comp_id,
                    smart_money_score=sm_score,
                    strategic_positioning_score=max_pos_score,
                    corporate_transformation_score=trans_score,
                    corporate_action_score=ca_score,
                    alignment_score=decomposed["alignment_score"],
                    strategic_actor_score=best_act_score,
                    ownership_behavior_score=best_beh_score,
                    concentration_score=conc_score,
                    evidence_quality_score=ev_score,
                    lead_time_quality_score=lt_qual_score,
                    hsc_flag=comp_hsc,
                    free_float_pct=comp_ff,
                    overall_priority=overall_band,
                    primary_actor_id=best_actor_id,
                    primary_behavior=best_cluster["behavior_type"] if best_cluster else None,
                    primary_action_type=primary_ca,
                    lead_time_days=lead_days,
                    transaction_to_public_lag_days=lead_metrics["transaction_to_public_lag_days"],
                    first_public_lead_days=lead_metrics["first_public_lead_days"],
                    first_alignment_lead_days=lead_metrics["first_alignment_lead_days"],
                    first_positioning_lead_days=lead_metrics["first_positioning_lead_days"],
                    first_signal_at=first_sig_date,
                    explicit_action_at=expl_date,
                    current_summary=summary_text,
                    why_flagged_summary=why_text,
                    corroborating_docs_count=total_docs_count,
                    quality_score=primary_q_score,
                    quality_label=primary_q_label,
                    opportunity_state=primary_opp_state,
                    shareholder_value_score=primary_sv_score,
                    positive_drivers_count=primary_pos_count,
                    red_flags_count=primary_red_count,
                    updated_at=datetime.utcnow()
                )
            else:
                intel_state.smart_money_score = sm_score
                intel_state.strategic_positioning_score = max_pos_score
                intel_state.corporate_transformation_score = trans_score
                intel_state.corporate_action_score = ca_score
                intel_state.alignment_score = decomposed["alignment_score"]
                intel_state.strategic_actor_score = best_act_score
                intel_state.ownership_behavior_score = best_beh_score
                intel_state.concentration_score = conc_score
                intel_state.evidence_quality_score = ev_score
                intel_state.lead_time_quality_score = lt_qual_score
                intel_state.hsc_flag = comp_hsc
                intel_state.free_float_pct = comp_ff
                intel_state.overall_priority = overall_band
                intel_state.primary_actor_id = best_actor_id
                intel_state.primary_behavior = best_cluster["behavior_type"] if best_cluster else None
                intel_state.primary_action_type = primary_ca
                intel_state.lead_time_days = lead_days
                intel_state.transaction_to_public_lag_days = lead_metrics["transaction_to_public_lag_days"]
                intel_state.first_public_lead_days = lead_metrics["first_public_lead_days"]
                intel_state.first_alignment_lead_days = lead_metrics["first_alignment_lead_days"]
                intel_state.first_positioning_lead_days = lead_metrics["first_positioning_lead_days"]
                intel_state.first_signal_at = first_sig_date
                intel_state.explicit_action_at = expl_date
                intel_state.current_summary = summary_text
                intel_state.why_flagged_summary = why_text
                intel_state.corroborating_docs_count = total_docs_count
                intel_state.quality_score = primary_q_score
                intel_state.quality_label = primary_q_label
                intel_state.opportunity_state = primary_opp_state
                intel_state.shareholder_value_score = primary_sv_score
                intel_state.positive_drivers_count = primary_pos_count
                intel_state.red_flags_count = primary_red_count
                intel_state.updated_at = datetime.utcnow()

            session.add(intel_state)
            session.commit()

        # Step 7: Final Scan Summary
        all_active_intel = session.exec(
            select(IssuerIntelligenceState)
            .where(IssuerIntelligenceState.overall_priority.in_(["VERY_HIGH", "HIGH", "MEDIUM"]))
        ).all()
        total_signals = len(all_active_intel)

        all_actions = session.exec(select(IssuerActionState).where(IssuerActionState.state_status == "ACTIVE")).all()
        db_early = sum(1 for a in all_actions if a.current_stage == "EARLY")
        db_dev = sum(1 for a in all_actions if a.current_stage == "DEVELOPING")
        db_expl = sum(1 for a in all_actions if a.current_stage == "EXPLICIT")

        scan.completed_at = datetime.now(timezone.utc)
        scan.status = "COMPLETED"
        scan.announcements_new = len(processed_announcements)
        scan.documents_processed = len(extracted_results)
        scan.pdfs_downloaded = len([r for r in extracted_results if r.get("success")])
        scan.pdfs_extracted = len([r for r in extracted_results if r.get("extracted") and r["extracted"].status == "EXTRACTED"])
        scan.ocr_required_or_failed = len([r for r in extracted_results if r.get("extracted") and r["extracted"].status != "EXTRACTED"])
        scan.ownership_events_found = ownership_events_total
        scan.strategic_positioning_candidates = strategic_candidates_count
        scan.important_signals_found = total_signals
        scan.early_signals_count = db_early
        scan.developing_signals_count = db_dev
        scan.explicit_signals_count = db_expl

        summary_data = {
            "stage_message": "Screening completed successfully.",
            "progress_percent": 100,
            "scan_mode": scan_mode,
            "announcements_retrieved": scan.announcements_found,
            "tier_a_documents": scan.tier_a_documents,
            "tier_b_documents": scan.tier_b_documents,
            "tier_c_metadata_only": scan.tier_c_metadata_only,
            "documents_processed": scan.documents_processed,
            "pdfs_downloaded": scan.pdfs_downloaded,
            "pdfs_extracted": scan.pdfs_extracted,
            "ocr_or_failed": scan.ocr_required_or_failed,
            "ownership_events": ownership_events_total,
            "strategic_candidates": strategic_candidates_count,
            "signals_total": total_signals,
            "early": db_early,
            "developing": db_dev,
            "explicit": db_expl
        }
        scan.summary_json = json.dumps(summary_data)
        session.add(scan)
        session.commit()
        session.refresh(scan)

        print(f"[Pipeline v7] Scan {scan.id} finished successfully. Mode: {scan_mode}, Signals: {total_signals}, Ownership Events: {ownership_events_total}")
        return scan

    except Exception as e:
        print(f"[Pipeline v7] Scan {scan.id} encountered exception: {e}")
        import traceback
        traceback.print_exc()
        scan.status = "FAILED"
        scan.completed_at = datetime.now(timezone.utc)
        scan.summary_json = json.dumps({
            "stage_message": f"Screening failed: {str(e)}",
            "progress_percent": 0,
            "error": str(e)
        })
        session.add(scan)
        session.commit()
        session.refresh(scan)
        raise e
