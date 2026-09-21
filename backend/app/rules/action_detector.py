import re
from typing import List, Dict, Any
from app.rules.definitions import ACTION_FAMILIES
from app.rules.context_analyzer import (
    check_negation_in_context,
    check_cancellation_in_context,
    check_distress_in_context,
    check_uncertainty_in_context
)

def extract_excerpt_around(text: str, start_idx: int, end_idx: int, max_len: int = 240) -> str:
    """Extracts a readable context excerpt around the match index."""
    half = max_len // 2
    left = max(0, start_idx - half)
    right = min(len(text), end_idx + half)
    
    # Try to snap to space boundary
    if left > 0:
        space_pos = text.find(" ", left)
        if space_pos != -1 and space_pos < start_idx:
            left = space_pos + 1
    if right < len(text):
        space_pos = text.rfind(" ", start_idx, right)
        if space_pos != -1 and space_pos > end_idx:
            right = space_pos

    excerpt = text[left:right].strip()
    if left > 0:
        excerpt = "..." + excerpt
    if right < len(text):
        excerpt = excerpt + "..."
    return excerpt

def detect_signals_in_document(
    title: str,
    pages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Screens document pages and title against all 15 action families.
    Returns list of detected signals with page-aware evidence.
    """
    signals = []

    # If document has no pages, screen title as single page 1
    doc_pages = pages if pages else [{"page_number": 1, "raw_text": title, "normalized_text": title}]

    for action_key, rules in ACTION_FAMILIES.items():
        explicit_matches = []
        early_matches = []
        lifecycle_matches = []
        positive_contexts_found = []
        distress_contexts_found = []
        negations_found = []
        cancellations_found = []
        uncertainties_found = []

        for p in doc_pages:
            page_num = p["page_number"]
            norm_text = p.get("normalized_text", "")
            raw_text = p.get("raw_text", norm_text)
            
            # 1. Search explicit terms
            for pat in rules["explicit_terms"]:
                for m in re.finditer(pat, norm_text, re.IGNORECASE):
                    excerpt = extract_excerpt_around(raw_text, m.start(), m.end())
                    is_neg = check_negation_in_context(excerpt, rules.get("negations"))
                    is_canc = check_cancellation_in_context(excerpt, rules.get("cancellations"))
                    is_dist = check_distress_in_context(excerpt, rules.get("negative_contexts"))
                    is_unc = check_uncertainty_in_context(excerpt, rules.get("uncertainties"))

                    explicit_matches.append({
                        "page_number": page_num,
                        "matched_text": m.group(0),
                        "excerpt": excerpt,
                        "is_negated": is_neg,
                        "is_cancelled": is_canc,
                        "is_distress": is_dist,
                        "is_uncertain": is_unc
                    })

            # 2. Search early/precursor terms
            for pat in rules["early_terms"]:
                for m in re.finditer(pat, norm_text, re.IGNORECASE):
                    excerpt = extract_excerpt_around(raw_text, m.start(), m.end())
                    is_neg = check_negation_in_context(excerpt, rules.get("negations"))
                    is_canc = check_cancellation_in_context(excerpt, rules.get("cancellations"))
                    is_dist = check_distress_in_context(excerpt, rules.get("negative_contexts"))
                    is_unc = check_uncertainty_in_context(excerpt, rules.get("uncertainties"))

                    early_matches.append({
                        "page_number": page_num,
                        "matched_text": m.group(0),
                        "excerpt": excerpt,
                        "is_negated": is_neg,
                        "is_cancelled": is_canc,
                        "is_distress": is_dist,
                        "is_uncertain": is_unc
                    })

            # 3. Check lifecycle stages
            for stage_info in rules.get("lifecycle_stages", []):
                for pat in stage_info["patterns"]:
                    for m in re.finditer(pat, norm_text, re.IGNORECASE):
                        excerpt = extract_excerpt_around(raw_text, m.start(), m.end())
                        lifecycle_matches.append({
                            "page_number": page_num,
                            "stage": stage_info["stage"],
                            "stage_name": stage_info["name"],
                            "matched_text": m.group(0),
                            "excerpt": excerpt
                        })

            # 4. Check positive contexts
            for pat in rules.get("positive_contexts", []):
                for m in re.finditer(pat, norm_text, re.IGNORECASE):
                    positive_contexts_found.append({
                        "page_number": page_num,
                        "excerpt": extract_excerpt_around(raw_text, m.start(), m.end())
                    })

        # Evaluate matches for this action family
        all_matches = explicit_matches + early_matches
        if not all_matches and not lifecycle_matches:
            continue

        # Check if entire signal is negated or cancelled
        valid_explicit = [m for m in explicit_matches if not m["is_negated"] and not m["is_cancelled"]]
        valid_early = [m for m in early_matches if not m["is_negated"] and not m["is_cancelled"]]
        is_negated = len(valid_explicit) == 0 and len(valid_early) == 0 and any(m["is_negated"] for m in all_matches)
        is_cancelled = any(m["is_cancelled"] for m in all_matches)
        is_distress = any(m["is_distress"] for m in all_matches)

        if is_negated:
            stage = "EARLY"
            impact = "NEUTRAL"
            strength = "LOW"
            confidence = "HIGH"
            reason = f"Explicit denial or negative clarification regarding {rules['name']}."
        elif is_cancelled:
            stage = "EARLY"
            impact = "NEGATIVE"
            strength = "MEDIUM"
            confidence = "HIGH"
            reason = f"Cancellation or termination of {rules['name']} announced."
        elif valid_explicit:
            stage = "EXPLICIT"
            strength = "HIGH"
            confidence = "HIGH"
            impact = "NEGATIVE" if is_distress else ("POSITIVE" if positive_contexts_found else "POSITIVE")
            reason = f"Explicit formal disclosure of {rules['name']}."
        elif valid_early or lifecycle_matches:
            stage = "EARLY"
            strength = "MEDIUM"
            confidence = "MEDIUM" if not any(m.get("is_uncertain") for m in early_matches) else "LOW"
            impact = "NEGATIVE" if is_distress else ("POSITIVE" if positive_contexts_found else "UNCLEAR")
            reason = f"Early precursor or lifecycle indicator detected for {rules['name']}."
        else:
            continue

        # Build evidence items
        evidence_items = []
        for m in (valid_explicit or explicit_matches):
            evidence_items.append({
                "page_number": m["page_number"],
                "excerpt": m["excerpt"],
                "evidence_type": "EXPLICIT"
            })
        for m in (valid_early or early_matches):
            evidence_items.append({
                "page_number": m["page_number"],
                "excerpt": m["excerpt"],
                "evidence_type": "PRECURSOR"
            })
        for lc in lifecycle_matches[:2]:
            evidence_items.append({
                "page_number": lc["page_number"],
                "excerpt": lc["excerpt"],
                "evidence_type": f"LIFECYCLE_{lc['stage']}"
            })
        for pos in positive_contexts_found[:2]:
            evidence_items.append({
                "page_number": pos["page_number"],
                "excerpt": pos["excerpt"],
                "evidence_type": "POSITIVE_CONTEXT"
            })

        latest_lifecycle_stage = lifecycle_matches[-1]["stage"] if lifecycle_matches else (
            "EXPLICIT_DECLARED" if stage == "EXPLICIT" else "PRECURSOR_IDENTIFIED"
        )

        signals.append({
            "action_type": action_key,
            "action_name": rules["name"],
            "category": rules.get("category", "GENERAL"),
            "stage": stage,
            "impact": impact,
            "strength": strength,
            "confidence": confidence,
            "lifecycle_stage": latest_lifecycle_stage,
            "reason": reason,
            "is_negated": is_negated,
            "is_cancelled": is_cancelled,
            "is_distress": is_distress,
            "evidence_items": evidence_items
        })

    return signals
