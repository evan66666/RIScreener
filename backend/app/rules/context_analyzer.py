import re
from typing import Dict, Any, List, Tuple
from app.rules.definitions import (
    GLOBAL_NEGATIONS, GLOBAL_CANCELLATIONS, GLOBAL_DISTRESS, GLOBAL_UNCERTAINTY
)

def search_patterns(text: str, patterns: List[str]) -> List[Tuple[str, int, int]]:
    """Finds all occurrences of patterns in text, returning (matched_text, start_pos, end_pos)."""
    matches = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            matches.append((m.group(0), m.start(), m.end()))
    return matches

def check_negation_in_context(sentence: str, custom_negations: List[str] = None) -> bool:
    """Checks if the sentence contains negation patterns."""
    patterns = GLOBAL_NEGATIONS + (custom_negations or [])
    for pat in patterns:
        if re.search(pat, sentence, re.IGNORECASE):
            return True
    return False

def check_cancellation_in_context(sentence: str, custom_cancellations: List[str] = None) -> bool:
    """Checks if the sentence contains cancellation/supersession patterns."""
    patterns = GLOBAL_CANCELLATIONS + (custom_cancellations or [])
    for pat in patterns:
        if re.search(pat, sentence, re.IGNORECASE):
            return True
    return False

def check_distress_in_context(text: str, custom_distress: List[str] = None) -> bool:
    """Checks if the context is associated with distress/liquidity emergency."""
    patterns = GLOBAL_DISTRESS + (custom_distress or [])
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def check_uncertainty_in_context(sentence: str, custom_uncertainties: List[str] = None) -> bool:
    """Checks if the statement is merely speculative/hypothetical."""
    patterns = GLOBAL_UNCERTAINTY + (custom_uncertainties or [])
    for pat in patterns:
        if re.search(pat, sentence, re.IGNORECASE):
            return True
    return False
