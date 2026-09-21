from typing import Dict, Any

def calculate_priority_score(
    stage: str,
    impact: str,
    importance: str,
    corroboration_docs_count: int,
    state_status: str
) -> int:
    """
    Computes deterministic ranking score based on research usefulness hierarchy (Section 21.2):
    1. Developing + Positive -> Highest Early-Opportunity value
    2. Early + Positive
    3. Explicit + Positive
    4. Developing + Mixed/Unclear
    5. Neutral / Low / Contradicted
    """
    if state_status in ("CONTRADICTED", "SUPERSEDED", "EXPIRED"):
        return 10

    score = 0

    # Base Stage + Impact Matrix
    if stage == "DEVELOPING" and impact == "POSITIVE":
        score = 100
    elif stage == "EARLY" and impact == "POSITIVE":
        score = 85
    elif stage == "EXPLICIT" and impact == "POSITIVE":
        score = 75
    elif stage == "DEVELOPING" and impact in ("MIXED", "UNCLEAR"):
        score = 65
    elif stage == "EXPLICIT" and impact in ("MIXED", "UNCLEAR"):
        score = 55
    elif stage == "EARLY" and impact in ("MIXED", "UNCLEAR"):
        score = 45
    elif impact == "NEGATIVE":
        score = 35
    else:
        score = 25

    # Importance boost
    if importance == "HIGH":
        score += 15
    elif importance == "MEDIUM":
        score += 5

    # Corroboration boost
    score += min(15, corroboration_docs_count * 5)

    return score

def get_priority_label(score: int) -> str:
    if score >= 80:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    return "LOW"
