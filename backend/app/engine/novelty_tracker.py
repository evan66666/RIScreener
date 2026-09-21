from typing import List, Dict, Any, Optional
from datetime import datetime

def determine_novelty_class(
    current_signal: Dict[str, Any],
    prior_events: List[Dict[str, Any]]
) -> str:
    """
    Determines novelty classification versus prior disclosures for the same issuer & action:
    - ROUTINE: Identical or repetitive without state progression
    - NEW: First time this topic/action appears for this issuer
    - MATERIAL_CHANGE: Material terms (amount, structure) changed
    - STATE_ADVANCEMENT: Lifecycle advanced (e.g. Funding -> RUPSLB -> HMETD)
    - REVERSAL: Negation or contradiction of previously active signal
    - CONFIRMATION: Execution or formal closure of already known stage
    """
    if not prior_events:
        return "NEW"

    if current_signal.get("is_negated") or current_signal.get("is_cancelled"):
        return "REVERSAL"

    last_event = prior_events[-1]
    last_stage = last_event.get("lifecycle_stage")
    current_stage = current_signal.get("lifecycle_stage")

    if current_stage != last_stage:
        if current_signal.get("stage") == "EXPLICIT":
            return "CONFIRMATION" if last_event.get("signal_type") == "EXPLICIT" else "STATE_ADVANCEMENT"
        return "STATE_ADVANCEMENT"

    return "ROUTINE"

def build_what_changed_summary(events: List[Dict[str, Any]]) -> str:
    """
    Generates a concise bulleted timeline of progression:
    e.g.
    - 14 Aug: Funding requirement mentioned
    - 21 Aug: RUPSLB with capital agenda
    - 28 Aug: Capital structure change disclosed
    """
    if not events:
        return "No prior disclosure history recorded."

    lines = []
    for ev in events:
        date_str = ""
        if isinstance(ev.get("event_date"), datetime):
            date_str = ev["event_date"].strftime("%d %b %Y")
        elif isinstance(ev.get("event_date"), str):
            date_str = ev["event_date"][:10]
        else:
            date_str = "Recent"

        stage_name = ev.get("lifecycle_stage", "").replace("_", " ").title()
        sig_type = ev.get("signal_type", "")
        title_hint = ev.get("title", "")
        
        desc = f"{stage_name}"
        if title_hint:
            desc += f" ({title_hint})"
        lines.append(f"• {date_str}: {desc}")

    return "\n".join(lines)
