from datetime import datetime, timedelta
from app.engine.lifecycle_manager import determine_issuer_action_stage
from app.engine.corroborator import evaluate_corroboration
from app.engine.novelty_tracker import determine_novelty_class
from app.engine.ranker import calculate_priority_score, get_priority_label

def test_single_precursor_is_early():
    now = datetime.now()
    events = [
        {
            "document_id": 1,
            "event_date": now - timedelta(days=20),
            "lifecycle_stage": "FUNDING_NEED",
            "signal_type": "PRECURSOR",
            "contribution": "NEW"
        }
    ]
    res = determine_issuer_action_stage(events, 60)
    assert res["stage"] == "EARLY"
    assert res["state_status"] == "ACTIVE"

def test_multiple_precursors_advance_to_developing():
    now = datetime.now()
    events = [
        {
            "document_id": 1,
            "event_date": now - timedelta(days=25),
            "lifecycle_stage": "FUNDING_NEED",
            "signal_type": "PRECURSOR",
            "contribution": "NEW"
        },
        {
            "document_id": 2,
            "event_date": now - timedelta(days=12),
            "lifecycle_stage": "RUPSLB_AGENDA",
            "signal_type": "PRECURSOR",
            "contribution": "STATE_ADVANCEMENT"
        },
        {
            "document_id": 3,
            "event_date": now - timedelta(days=2),
            "lifecycle_stage": "NEW_SHARES_PLANNED",
            "signal_type": "PRECURSOR",
            "contribution": "STATE_ADVANCEMENT"
        }
    ]
    res = determine_issuer_action_stage(events, 60)
    assert res["stage"] == "DEVELOPING"
    assert res["state_status"] == "ACTIVE"

def test_explicit_signal_moves_to_explicit():
    now = datetime.now()
    events = [
        {
            "document_id": 1,
            "event_date": now - timedelta(days=10),
            "lifecycle_stage": "RUPSLB_AGENDA",
            "signal_type": "PRECURSOR",
            "contribution": "NEW"
        },
        {
            "document_id": 2,
            "event_date": now,
            "lifecycle_stage": "HMETD_DECLARED",
            "signal_type": "EXPLICIT",
            "contribution": "CONFIRMATION"
        }
    ]
    res = determine_issuer_action_stage(events, 60)
    assert res["stage"] == "EXPLICIT"

def test_priority_ranking_hierarchy():
    # Developing + Positive should outrank Explicit + Positive and Neutral items
    dev_pos_score = calculate_priority_score("DEVELOPING", "POSITIVE", "HIGH", 3, "ACTIVE")
    early_pos_score = calculate_priority_score("EARLY", "POSITIVE", "HIGH", 1, "ACTIVE")
    expl_pos_score = calculate_priority_score("EXPLICIT", "POSITIVE", "HIGH", 2, "ACTIVE")
    neutral_score = calculate_priority_score("EARLY", "NEUTRAL", "LOW", 1, "ACTIVE")

    assert dev_pos_score > early_pos_score
    assert get_priority_label(dev_pos_score) == "HIGH"
    assert dev_pos_score > neutral_score
