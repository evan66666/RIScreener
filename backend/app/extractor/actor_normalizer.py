import re
from datetime import datetime
from typing import Tuple, Optional
from sqlmodel import Session, select
from app.models.schema import Actor, ActorAlias, ActorRelationship, InvestorClassification
LEGAL_AFFIXES = [
    r"^pt[\.\s]+",
    r"\s+pt[\.\s]*$",
    r"\s+tbk[\.\s]*$",
    r"\s+\(persero\)[\.\s]*$",
    r"\s+ltd[\.\s]*$",
    r"\s+limited[\.\s]*$",
    r"\s+pte[\.\s]+ltd[\.\s]*$",
    r"\s+inc[\.\s]*$",
    r"\s+corp[\.\s]*$",
    r"\s+corporation[\.\s]*$",
    r"\s+sdn[\.\s]+bhd[\.\s]*$",
    r"\s+bhd[\.\s]*$",
    r"\s+holding[\.\s]*$",
    r"\s+holdings[\.\s]*$"
]

def generate_normalized_key(name: str) -> str:
    """
    Produces a canonical matching key by normalizing case, punctuation,
    and common legal company prefixes/suffixes.
    """
    if not name:
        return ""
    
    clean = name.strip().lower()
    clean = re.sub(r"[,\.\(\)\-\_\\\/]+", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()

    changed = True
    while changed:
        before = clean
        for pattern in LEGAL_AFFIXES:
            clean = re.sub(pattern, " ", clean, flags=re.IGNORECASE).strip()
        clean = re.sub(r"\s+", " ", clean).strip()
        changed = (before != clean)

    return clean or name.strip().lower()


def classify_actor_role(raw_name: str, context_text: str = "") -> str:
    """
    Classifies actor into taxonomy:
    CONTROLLER, DIRECTOR, COMMISSIONER, STRATEGIC_INVESTOR, INSTITUTION, CORPORATE, SIGNIFICANT_HOLDER, GOVERNMENT, OTHER
    """
    combined = f"{raw_name} {context_text}".lower()

    if re.search(r"\b(?:pengendali|pemegang\s+saham\s+pengendali|psp|controlling\s+shareholder)\b", combined):
        return "CONTROLLER"
    if re.search(r"\b(?:direktur\s+utama|direktur|director|managing\s+director)\b", combined):
        return "DIRECTOR"
    if re.search(r"\b(?:komisaris\s+utama|komisaris|commissioner)\b", combined):
        return "COMMISSIONER"
    if re.search(r"\b(?:investor\s+strategis|strategic\s+investor|anchor\s+investor)\b", combined):
        return "STRATEGIC_INVESTOR"
    if re.search(r"\b(?:reksadana|fund|asset\s+management|investama|sekuritas|capital|investment|pension|dplk)\b", combined):
        return "INSTITUTION"
    if re.search(r"\b(?:pemerintah|republik\s+indonesia|kementerian|bumn)\b", combined):
        return "GOVERNMENT"
    if re.search(r"\b(?:pt|tbk|ltd|inc|corp|holding|bhd)\b", raw_name.lower()):
        return "CORPORATE"
    
    return "SIGNIFICANT_HOLDER"


def resolve_or_create_actor(
    session: Session,
    raw_name: str,
    context_text: str = "",
    role_hint: Optional[str] = None,
    domicile: Optional[str] = None,
    beneficial_owner_name: Optional[str] = None,
    controller_name: Optional[str] = None,
    raw_class: Optional[str] = None,
    normalized_class: Optional[str] = None,
    source_doc_id: Optional[int] = None
) -> Tuple[Actor, bool]:
    """
    Finds existing actor by normalized key or alias; otherwise creates a new canonical Actor.
    Stores investor classification and links disclosed beneficial owners / controllers.
    """
    raw_clean = raw_name.strip()
    norm_key = generate_normalized_key(raw_clean)

    if not norm_key:
        norm_key = "unknown_actor"

    is_created = False

    # 1. Search by exact normalized_key
    actor = session.exec(select(Actor).where(Actor.normalized_key == norm_key)).first()
    if not actor:
        # 2. Search by alias
        alias_match = session.exec(select(ActorAlias).where(ActorAlias.alias == raw_clean)).first()
        if alias_match and alias_match.actor:
            actor = alias_match.actor
        else:
            # 3. Create new Actor
            role = role_hint or classify_actor_role(raw_clean, context_text)
            actor = Actor(
                canonical_name=raw_clean,
                raw_name=raw_clean,
                actor_type=role,
                domicile=domicile or "DOMESTIC",
                normalized_key=norm_key,
                confidence="HIGH"
            )
            session.add(actor)
            session.commit()
            session.refresh(actor)
            is_created = True

            alias = ActorAlias(actor_id=actor.id, alias=raw_clean, source="PRIMARY", confidence="EXACT")
            session.add(alias)
            session.commit()
    else:
        # Existing actor, check if raw_clean is an alias
        existing_alias = session.exec(
            select(ActorAlias)
            .where(ActorAlias.actor_id == actor.id)
            .where(ActorAlias.alias == raw_clean)
        ).first()
        if not existing_alias:
            alias = ActorAlias(actor_id=actor.id, alias=raw_clean, source="DISCLOSURE", confidence="HIGH")
            session.add(alias)
            session.commit()

        if domicile and not actor.domicile:
            actor.domicile = domicile
            session.add(actor)
            session.commit()

    # Record Investor Classification if provided
    if raw_class or normalized_class:
        norm_c = normalized_class or "OTHER"
        existing_ic = session.exec(
            select(InvestorClassification)
            .where(InvestorClassification.actor_id == actor.id)
            .where(InvestorClassification.normalized_class == norm_c)
        ).first()
        if not existing_ic:
            ic = InvestorClassification(
                actor_id=actor.id,
                raw_class=raw_class or "",
                normalized_class=norm_c,
                source="DISCLOSURE",
                observed_at=datetime.utcnow(),
                confidence="HIGH"
            )
            session.add(ic)
            session.commit()

    # Link Beneficial Owner if disclosed (PRD Section 6)
    if beneficial_owner_name and beneficial_owner_name.strip() and beneficial_owner_name.strip().lower() != raw_clean.lower():
        ubo_clean = beneficial_owner_name.strip()
        ubo_key = generate_normalized_key(ubo_clean)
        ubo_actor = session.exec(select(Actor).where(Actor.normalized_key == ubo_key)).first()
        if not ubo_actor:
            ubo_actor = Actor(
                canonical_name=ubo_clean,
                raw_name=ubo_clean,
                actor_type="BENEFICIAL_OWNER",
                normalized_key=ubo_key,
                confidence="HIGH"
            )
            session.add(ubo_actor)
            session.commit()
            session.refresh(ubo_actor)

        # Update actor's beneficial_owner_id
        if not actor.beneficial_owner_id:
            actor.beneficial_owner_id = ubo_actor.id
            session.add(actor)
            session.commit()

        # Record relationship
        existing_rel = session.exec(
            select(ActorRelationship)
            .where(ActorRelationship.actor_id == actor.id)
            .where(ActorRelationship.related_actor_id == ubo_actor.id)
        ).first()
        if not existing_rel:
            rel = ActorRelationship(
                actor_id=actor.id,
                related_actor_id=ubo_actor.id,
                relationship_type="ULTIMATE_BENEFICIARY",
                beneficial_owner_id=ubo_actor.id,
                source_document_id=source_doc_id,
                confidence="HIGH"
            )
            session.add(rel)
            session.commit()

    # Link Controller if disclosed (PRD Section 6)
    if controller_name and controller_name.strip() and controller_name.strip().lower() != raw_clean.lower():
        ctrl_clean = controller_name.strip()
        ctrl_key = generate_normalized_key(ctrl_clean)
        ctrl_actor = session.exec(select(Actor).where(Actor.normalized_key == ctrl_key)).first()
        if not ctrl_actor:
            ctrl_actor = Actor(
                canonical_name=ctrl_clean,
                raw_name=ctrl_clean,
                actor_type="CONTROLLER",
                normalized_key=ctrl_key,
                confidence="HIGH"
            )
            session.add(ctrl_actor)
            session.commit()
            session.refresh(ctrl_actor)

        if not actor.controller_id:
            actor.controller_id = ctrl_actor.id
            session.add(actor)
            session.commit()

        existing_ctrl_rel = session.exec(
            select(ActorRelationship)
            .where(ActorRelationship.actor_id == actor.id)
            .where(ActorRelationship.related_actor_id == ctrl_actor.id)
        ).first()
        if not existing_ctrl_rel:
            rel = ActorRelationship(
                actor_id=actor.id,
                related_actor_id=ctrl_actor.id,
                relationship_type="CONTROLS",
                controller_id=ctrl_actor.id,
                source_document_id=source_doc_id,
                confidence="HIGH"
            )
            session.add(rel)
            session.commit()

    return actor, is_created
