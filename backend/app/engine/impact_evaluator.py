from typing import List, Dict, Any

def evaluate_economic_impact(
    action_type: str,
    stage: str,
    positive_flags: bool,
    distress_flags: bool,
    is_negated: bool,
    is_cancelled: bool
) -> str:
    """
    Evaluates economic impact:
    - POSITIVE: Favorable business/expansion/synergy/accretive rationale
    - NEUTRAL: Routine or balanced without obvious directional bias
    - NEGATIVE: Distress, forced asset sale, debt default, or cancellation
    - MIXED: Coexistence of positive expansion + high dilution/debt
    - UNCLEAR: Insufficient context
    - NO_SIGNAL: Negated or no actionable information
    """
    if is_negated:
        return "NO_SIGNAL"

    if is_cancelled or distress_flags:
        return "NEGATIVE"

    if positive_flags and not distress_flags:
        return "POSITIVE"

    if positive_flags and distress_flags:
        return "MIXED"

    if stage in ("DEVELOPING", "EXPLICIT"):
        return "POSITIVE" if action_type in ("SHARE_BUYBACK", "SPECIAL_DIVIDEND", "MAJOR_CONTRACT", "MAJOR_EXPANSION") else "UNCLEAR"

    return "UNCLEAR"
