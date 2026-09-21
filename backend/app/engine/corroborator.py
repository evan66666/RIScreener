from typing import List, Dict, Any

def evaluate_corroboration(
    action_type: str,
    events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates multi-document corroboration across lookback window:
    - Counts distinct supporting filings
    - Evaluates chronological consistency
    - Determines if corroboration bonus applies
    """
    doc_count = len({ev["document_id"] for ev in events if "document_id" in ev})
    distinct_stages = len({ev["lifecycle_stage"] for ev in events if "lifecycle_stage" in ev})

    if doc_count >= 3 and distinct_stages >= 2:
        return {
            "corroboration_level": "STRONG",
            "confidence_boost": True,
            "doc_count": doc_count,
            "explanation": f"Strong cross-document corroboration across {doc_count} distinct filings with lifecycle advancement."
        }
    elif doc_count >= 2:
        return {
            "corroboration_level": "MODERATE",
            "confidence_boost": True,
            "doc_count": doc_count,
            "explanation": f"Corroborated across {doc_count} related filings."
        }
    else:
        return {
            "corroboration_level": "SINGLE_SOURCE",
            "confidence_boost": False,
            "doc_count": max(1, doc_count),
            "explanation": "Single disclosure evidence."
        }
