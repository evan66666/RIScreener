import pytest
from app.engine.cross_signal_engine import (
    calculate_strategic_positioning_score,
    calculate_corporate_transformation_score,
    calculate_corporate_action_prep_score,
    calculate_alignment_score,
    calculate_composite_smart_money_score
)

def test_strategic_positioning_score():
    cluster = {
        "behavior_type": "ACCUMULATION_CANDIDATE",
        "transaction_count": 3,
        "total_shares_delta": 70_000_000,
        "delta_pct": 1.2,
        "avg_price": 165.0
    }
    score = calculate_strategic_positioning_score(cluster, actor_type="CONTROLLER")
    # Base 35 + Controller 25 + tx>=3 (20) + delta_s>50M (12) + price (8) = 100
    assert score >= 80

    # Administrative change should have very low score
    admin_cluster = {
        "behavior_type": "ADMINISTRATIVE_CHANGE",
        "transaction_count": 1,
        "total_shares_delta": 50_000_000,
        "delta_pct": 1.0
    }
    admin_score = calculate_strategic_positioning_score(admin_cluster, actor_type="SIGNIFICANT_HOLDER")
    assert admin_score <= 20

def test_corporate_transformation_score():
    transformations = [
        {
            "transformation_type": "ASSET_INJECTION",
            "stage": "AGREEMENT",
            "asset_catalysts": ["MINING_MINERAL", "ENERGY_PROJECT"]
        }
    ]
    score = calculate_corporate_transformation_score(transformations)
    assert score >= 60

def test_corporate_action_prep_score():
    action_states = [
        {
            "action_type": "RIGHT_ISSUE_HMETD",
            "stage": "DEVELOPING",
            "impact": "POSITIVE",
            "corroborating_docs_count": 2,
            "state_status": "ACTIVE"
        }
    ]
    score = calculate_corporate_action_prep_score(action_states)
    assert score >= 65

def test_composite_smart_money_priority_bands():
    # Case of strong convergence (Pattern A):
    # High positioning + High action prep + Transformation catalyst + Alignment
    pos_score = 85
    trans_score = 70
    action_score = 80
    align_score = calculate_alignment_score(pos_score, trans_score, action_score)
    assert align_score >= 90

    final_score, band = calculate_composite_smart_money_score(
        pos_score=pos_score,
        trans_score=trans_score,
        action_score=action_score,
        alignment_score=align_score,
        corroboration_docs_count=3
    )

    assert final_score >= 80
    assert band == "VERY_HIGH"
