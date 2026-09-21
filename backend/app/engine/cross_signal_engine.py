from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from app.rules.definitions import (
    PENALTY_ADMINISTRATIVE_TRANSFER,
    SIGNAL_OWNERSHIP_CONVERGENCE,
    SIGNAL_VERY_HIGH_ALIGNMENT,
    MINIMUM_FREE_FLOAT_PCT
)


def calculate_strategic_actor_score(
    actor_type: str = "SIGNIFICANT_HOLDER",
    domicile: str = "DOMESTIC",
    has_relationships: bool = False
) -> int:
    """Computes Strategic Actor Score (0-100) per PRD Section 5 & 21."""
    score = 40
    norm_type = actor_type.upper()
    if norm_type == "CONTROLLER":
        score = 90
    elif norm_type in ("DIRECTOR", "COMMISSIONER"):
        score = 80
    elif norm_type == "STRATEGIC_INVESTOR":
        score = 85
    elif norm_type == "FUND":
        score = 75
    elif norm_type in ("PENSION", "INSURANCE", "BANK"):
        score = 70
    elif norm_type in ("INSTITUTION", "CORPORATE"):
        score = 65
    elif norm_type == "SIGNIFICANT_HOLDER":
        score = 55
    elif norm_type == "GOVERNMENT_RELATED":
        score = 80

    if has_relationships:
        score += 5

    return min(100, max(0, score))


def calculate_ownership_behavior_score(
    behavior_cluster: Dict[str, Any]
) -> int:
    """
    Computes Ownership Behavior Score (0-100) per PRD Section 12, 15, & 21.
    Strictly penalizes administrative transfers and treats share pledges as financing context.
    """
    behavior_type = behavior_cluster.get("behavior_type", "")
    if behavior_type == "ADMINISTRATIVE_CHANGE" or behavior_cluster.get("is_administrative"):
        return max(5, 20 - PENALTY_ADMINISTRATIVE_TRANSFER // 2)

    if behavior_type in ("SHARE_PLEDGE_FINANCING", "SHARE_PLEDGE_RELEASE"):
        return 30  # Financing context, not a standalone accumulation signal

    score = 20
    # 1. Behavior Base
    if behavior_type == "ACCUMULATION_CANDIDATE":
        score += 40
    elif behavior_type in ("STRATEGIC_POSITIONING_CANDIDATE", "NEW_POSITION", "THRESHOLD_CROSSING"):
        score += 30
    elif behavior_type == "DISTRIBUTION_CANDIDATE":
        score += 20
    elif behavior_type == "POSITION_REDUCTION":
        score += 15
    else:
        score += 10

    # 2. Repeated activity bonus
    tx_count = behavior_cluster.get("transaction_count", 0)
    if tx_count >= 3:
        score += 15
    elif tx_count == 2:
        score += 8

    # 3. Materiality / Size
    delta_s = abs(behavior_cluster.get("total_shares_delta", 0.0))
    delta_p = abs(behavior_cluster.get("delta_pct", 0.0))
    if delta_s > 50_000_000 or delta_p >= 1.0:
        score += 10
    elif delta_s > 10_000_000 or delta_p >= 0.5:
        score += 5

    # 4. Disclosed cost basis bonus
    if behavior_cluster.get("avg_price"):
        score += 5

    # 5. Ownership convergence bonus (PRD Section 13)
    if behavior_cluster.get("ownership_convergence"):
        score += 10

    return min(100, max(0, score))


def calculate_concentration_context_score(
    hsc_flag: bool = False,
    free_float_pct: Optional[float] = None
) -> int:
    """
    Computes Concentration Context Score (0-100) per PRD Section 8, 9, & 21.
    Context signal reflecting supply scarcity, not an accumulation signal itself.
    """
    score = 30
    if hsc_flag:
        score += 35

    if free_float_pct is not None:
        if free_float_pct < MINIMUM_FREE_FLOAT_PCT:
            score += 25
        elif free_float_pct < 20.0:
            score += 15

    return min(100, max(0, score))


def calculate_corporate_transformation_score(
    transformations: List[Dict[str, Any]]
) -> int:
    """Computes Corporate Transformation Score (0-100)."""
    if not transformations:
        return 0

    score = 0
    for t in transformations:
        t_type = t.get("transformation_type", "")
        if t_type in ("CHANGE_OF_CONTROL", "NEW_CONTROLLING_GROUP"):
            score = max(score, 45)
        elif t_type in ("ASSET_INJECTION", "PROJECT_INJECTION", "STRATEGIC_ASSET_ACQUISITION"):
            score = max(score, 40)
        elif t_type in ("PRINCIPAL_BUSINESS_CHANGE", "NEW_STRATEGIC_INDUSTRY", "STRATEGIC_PARTNERSHIP"):
            score = max(score, 35)
        elif t_type == "MAJOR_FINANCING_RECAPITALIZATION":
            score = max(score, 30)
        else:
            score = max(score, 20)

        # Asset catalyst bonus
        if t.get("asset_catalysts"):
            score += 15

        # Lifecycle advancement
        if t.get("stage") in ("AGREEMENT", "APPROVAL", "EXECUTION", "COMPLETED"):
            score += 10

    return min(100, max(0, score))


def calculate_corporate_action_prep_score(
    action_states: List[Dict[str, Any]]
) -> int:
    """Computes Corporate Action Preparation Score (0-100)."""
    if not action_states:
        return 0

    score = 0
    for a in action_states:
        stage = a.get("stage", "")
        impact = a.get("impact", "")
        status = a.get("state_status", "ACTIVE")

        if status in ("CONTRADICTED", "CANCELLED"):
            continue

        if stage == "DEVELOPING":
            sub_score = 45
        elif stage == "EXPLICIT":
            sub_score = 40
        elif stage == "EARLY":
            sub_score = 25
        else:
            sub_score = 15

        if impact == "POSITIVE":
            sub_score += 15
        elif impact in ("MIXED", "UNCLEAR"):
            sub_score += 5

        doc_count = a.get("corroborating_docs_count", 1)
        sub_score += min(15, doc_count * 5)

        score = max(score, sub_score)

    return min(100, max(0, score))


def calculate_market_anomaly_score(
    is_volatility: bool = False,
    is_uma: bool = False
) -> int:
    """Computes Market Anomaly Score (0-100)."""
    score = 15
    if is_volatility:
        score += 35
    if is_uma:
        score += 30
    return min(100, max(0, score))


def calculate_evidence_quality_score(
    doc_count: int = 1,
    has_exact_price: bool = False,
    has_exact_shares: bool = True
) -> int:
    """Computes Evidence Quality Score (0-100)."""
    score = 50
    score += min(25, (doc_count - 1) * 8)
    if has_exact_price:
        score += 15
    if has_exact_shares:
        score += 10
    return min(100, max(0, score))


def calculate_lead_time_quality_score(
    lag_days: Optional[int] = None,
    lead_days: Optional[int] = None
) -> int:
    """
    Computes Lead-Time Quality Score (0-100) per PRD Section 10 & 11.
    Rewards early public observability and low transaction-to-publication latency.
    """
    score = 50
    # POJK 4/2024 compliance bonus: <= 5 days lag is disciplined reporting
    if lag_days is not None:
        if lag_days <= 5:
            score += 20
        elif lag_days <= 10:
            score += 10
        elif lag_days > 20:
            score -= 15

    if lead_days is not None and lead_days > 0:
        if lead_days >= 30:
            score += 30
        elif lead_days >= 14:
            score += 20
        elif lead_days >= 5:
            score += 10

    return min(100, max(0, score))


def calculate_alignment_score(
    pos_or_actor_score: int,
    trans_or_beh_score: int,
    action_or_trans_score: int,
    action_score: Optional[int] = None
) -> int:
    """
    Computes Alignment Score (0-100) measuring cross-layer convergence.
    Supports both 3-argument (pos_score, trans_score, action_score) and
    4-argument (actor_score, behavior_score, trans_score, action_score) signatures.
    """
    if action_score is not None:
        actor_score = pos_or_actor_score
        behavior_score = trans_or_beh_score
        trans_score = action_or_trans_score
        act_score = action_score
        layers_active = 0
        if actor_score >= 60 and behavior_score >= 40:
            layers_active += 1
        if trans_score >= 25:
            layers_active += 1
        if act_score >= 25:
            layers_active += 1
    else:
        pos_score = pos_or_actor_score
        trans_score = trans_or_beh_score
        act_score = action_or_trans_score
        layers_active = 0
        if pos_score >= 35:
            layers_active += 1
        if trans_score >= 25:
            layers_active += 1
        if act_score >= 25:
            layers_active += 1

    if layers_active == 3:
        return 95
    elif layers_active == 2:
        return 70
    elif layers_active == 1:
        return 35
    return 10


def calculate_decomposed_smart_money_score(
    strategic_actor_score: int,
    ownership_behavior_score: int,
    concentration_score: int,
    corporate_transformation_score: int,
    corporate_action_score: int,
    market_anomaly_score: int,
    evidence_quality_score: int,
    lead_time_quality_score: int,
    corroboration_docs_count: int = 1
) -> Tuple[int, str, Dict[str, int]]:
    """
    Computes composite Smart Money Priority Score and decomposed visible components
    per PRD v7.2 Section 21.
    """
    align_score = calculate_alignment_score(
        strategic_actor_score,
        ownership_behavior_score,
        corporate_transformation_score,
        corporate_action_score
    )

    # Weighted composition
    raw_score = (
        0.25 * strategic_actor_score +
        0.25 * ownership_behavior_score +
        0.15 * corporate_action_score +
        0.15 * corporate_transformation_score +
        0.10 * align_score +
        0.05 * concentration_score +
        0.05 * evidence_quality_score
    )

    # Corroboration bonus
    raw_score += min(8, max(0, (corroboration_docs_count - 1) * 2))

    final_score = int(min(100, max(0, round(raw_score))))

    # Determine Priority Band
    # PRD Section 14: Highest priority alignment occurs when Actor + Action Prep + Transformation + Temporal converge
    if (strategic_actor_score >= 75 and ownership_behavior_score >= 65 and
        corporate_action_score >= 50 and corporate_transformation_score >= 40):
        overall_priority = "VERY_HIGH"
    elif final_score >= 80:
        overall_priority = "VERY_HIGH"
    elif final_score >= 65:
        overall_priority = "HIGH"
    elif final_score >= 50:
        overall_priority = "MEDIUM"
    elif final_score >= 30:
        overall_priority = "LOW"
    else:
        overall_priority = "WATCH"

    decomposed = {
        "strategic_actor_score": strategic_actor_score,
        "ownership_behavior_score": ownership_behavior_score,
        "concentration_score": concentration_score,
        "corporate_transformation_score": corporate_transformation_score,
        "corporate_action_score": corporate_action_score,
        "market_anomaly_score": market_anomaly_score,
        "evidence_quality_score": evidence_quality_score,
        "lead_time_quality_score": lead_time_quality_score,
        "alignment_score": align_score,
        "smart_money_score": final_score
    }

    return final_score, overall_priority, decomposed


def calculate_lead_time_metrics(
    earliest_public_date: Optional[datetime],
    earliest_positioning_date: Optional[datetime],
    first_alignment_date: Optional[datetime],
    explicit_ca_date: Optional[datetime],
    transaction_date: Optional[datetime]
) -> Dict[str, Optional[int]]:
    """
    Calculates the 4 distinct lead-time measurements mandated by PRD v7.2 Section 11:
    A. transaction_to_public_lag_days = publication_date - transaction_date
    B. first_public_lead_days = explicit_date - earliest_public_evidence_date
    C. first_alignment_lead_days = explicit_date - first_date_multiple_layers_aligned
    D. first_positioning_lead_days = explicit_date - earliest_public_strategic_positioning_evidence
    """
    lag_days = None
    first_pub_lead = None
    first_align_lead = None
    first_pos_lead = None

    if transaction_date and earliest_public_date and earliest_public_date >= transaction_date:
        lag_days = (earliest_public_date - transaction_date).days

    if explicit_ca_date:
        if earliest_public_date and explicit_ca_date >= earliest_public_date:
            first_pub_lead = (explicit_ca_date - earliest_public_date).days

        if first_alignment_date and explicit_ca_date >= first_alignment_date:
            first_align_lead = (explicit_ca_date - first_alignment_date).days

        if earliest_positioning_date and explicit_ca_date >= earliest_positioning_date:
            first_pos_lead = (explicit_ca_date - earliest_positioning_date).days

    return {
        "transaction_to_public_lag_days": lag_days,
        "first_public_lead_days": first_pub_lead,
        "first_alignment_lead_days": first_align_lead,
        "first_positioning_lead_days": first_pos_lead
    }


def calculate_strategic_positioning_score(
    behavior_cluster: Dict[str, Any],
    actor_type: str = "SIGNIFICANT_HOLDER"
) -> int:
    """Backwards-compatible wrapper computing combined positioning score (0-100)."""
    behavior_type = behavior_cluster.get("behavior_type", "")
    if behavior_type == "ADMINISTRATIVE_CHANGE" or behavior_cluster.get("is_administrative"):
        return 15

    act_s = calculate_strategic_actor_score(actor_type)
    beh_s = calculate_ownership_behavior_score(behavior_cluster)
    combined = (act_s + beh_s) // 2
    if behavior_cluster.get("avg_price"):
        combined += 8
    return min(100, max(0, combined))


def calculate_composite_smart_money_score(
    pos_score: int,
    trans_score: int,
    action_score: int,
    alignment_score: int,
    corroboration_docs_count: int = 1
) -> Tuple[int, str]:
    """Backwards-compatible wrapper for v7.0 scoring calculation."""
    raw = 0.35 * pos_score + 0.25 * action_score + 0.20 * trans_score + 0.20 * alignment_score
    raw += min(10, max(0, (corroboration_docs_count - 1) * 3))
    score = int(min(100, max(0, round(raw))))
    if score >= 80:
        band = "VERY_HIGH"
    elif score >= 65:
        band = "HIGH"
    elif score >= 50:
        band = "MEDIUM"
    elif score >= 30:
        band = "LOW"
    else:
        band = "WATCH"
    return score, band
