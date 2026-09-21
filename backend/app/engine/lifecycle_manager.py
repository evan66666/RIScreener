from typing import List, Dict, Any
from datetime import datetime, timedelta

def determine_issuer_action_stage(
    events: List[Dict[str, Any]],
    lookback_days: int = 60
) -> Dict[str, Any]:
    """
    Computes overall state and stage for an issuer + corporate action family:
    Stages:
    - EARLY: 1 precursor signal
    - DEVELOPING: >= 2 related precursor signals advancing lifecycle
    - EXPLICIT: Formal announcement detected
    Statuses:
    - ACTIVE
    - CONTRADICTED
    - SUPERSEDED
    - EXPIRED
    """
    if not events:
        return {
            "stage": "EARLY",
            "state_status": "EXPIRED",
            "strength": "LOW",
            "confidence": "LOW",
            "why_flagged": "No active signals."
        }

    # Sort events chronologically
    sorted_events = sorted(events, key=lambda x: x["event_date"])
    latest_event = sorted_events[-1]

    # Check for cancellation or contradiction in latest event
    if latest_event.get("contribution") in ("REVERSAL", "CONTRADICTION") or latest_event.get("is_negated"):
        return {
            "stage": "EARLY",
            "state_status": "CONTRADICTED",
            "strength": "LOW",
            "confidence": "HIGH",
            "why_flagged": "Signal actively contradicted or denied by issuer in recent filing."
        }

    if latest_event.get("is_cancelled"):
        return {
            "stage": "EARLY",
            "state_status": "SUPERSEDED",
            "strength": "LOW",
            "confidence": "HIGH",
            "why_flagged": "Corporate action plan explicitly cancelled or terminated."
        }

    # Check for EXPLICIT signal
    has_explicit = any(e.get("signal_type") == "EXPLICIT" for e in sorted_events)
    if has_explicit:
        return {
            "stage": "EXPLICIT",
            "state_status": "ACTIVE",
            "strength": "HIGH",
            "confidence": "HIGH",
            "why_flagged": "Formal corporate action announcement disclosed."
        }

    # Count distinct precursors and stages
    distinct_stages = {e.get("lifecycle_stage") for e in sorted_events if e.get("lifecycle_stage")}
    precursor_events = [e for e in sorted_events if e.get("signal_type") in ("PRECURSOR", "EARLY")]

    if len(precursor_events) >= 2 or len(distinct_stages) >= 2:
        return {
            "stage": "DEVELOPING",
            "state_status": "ACTIVE",
            "strength": "HIGH",
            "confidence": "HIGH" if len(precursor_events) >= 3 else "MEDIUM",
            "why_flagged": f"{len(precursor_events)} related precursor disclosures advanced the action lifecycle."
        }
    else:
        return {
            "stage": "EARLY",
            "state_status": "ACTIVE",
            "strength": "MEDIUM",
            "confidence": "MEDIUM",
            "why_flagged": "Early precursor evidence detected; awaiting further progression."
        }
