from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.rules.definitions import OWNERSHIP_THRESHOLDS

def calculate_disclosed_cost_basis(transactions: List[Dict[str, Any]]) -> Optional[float]:
    """
    Computes weighted average disclosed acquisition price:
    sum(quantity_i * price_i) / sum(quantity_i)
    Only considers acquisitions where quantity and price are explicitly known.
    """
    total_qty = 0.0
    total_value = 0.0

    for tx in transactions:
        qty = tx.get("quantity") or tx.get("delta_shares") or 0.0
        price = tx.get("price")
        direction = tx.get("direction") or tx.get("event_type", "ACQUIRE")
        if direction in ("ACQUIRE", "SUBSCRIBE", "EXERCISE") and price and price > 0 and qty > 0:
            total_qty += qty
            total_value += (qty * price)

    if total_qty > 0 and total_value > 0:
        return round(total_value / total_qty, 2)
    return None


def detect_threshold_crossings(pct_before: float, pct_after: float) -> List[Dict[str, Any]]:
    """
    Detects if an analytical threshold (1%, 3%, 5%, 10%, 20%, 50%) was crossed.
    """
    crossings = []
    before_ratio = pct_before / 100.0 if pct_before > 1.0 else pct_before
    after_ratio = pct_after / 100.0 if pct_after > 1.0 else pct_after

    for th in OWNERSHIP_THRESHOLDS:
        if before_ratio < th <= after_ratio:
            crossings.append({"threshold": th * 100, "direction": "UP"})
        elif before_ratio >= th > after_ratio:
            crossings.append({"threshold": th * 100, "direction": "DOWN"})

    return crossings


def cluster_actor_behavior(
    actor_id: int,
    company_id: int,
    events: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Reconstructs actor positioning behavior across lookback events (PRD v7.2 Patch).
    - Differentiates discrete acquisitions, disposals, pledges, and administrative transfers
    - Detects OWNERSHIP_CONVERGENCE (Section 13)
    - Computes transaction-to-public lag (Section 10 & 11)
    - Strictly avoids false accumulation flags for pledges or pure structural snapshots
    """
    if not events:
        return {
            "actor_id": actor_id,
            "company_id": company_id,
            "behavior_type": "UNKNOWN",
            "transaction_count": 0,
            "total_shares_delta": 0.0,
            "pct_before": 0.0,
            "pct_after": 0.0,
            "delta_pct": 0.0,
            "avg_price": None,
            "threshold_crossings": [],
            "has_pledge": False,
            "is_administrative": False,
            "ownership_convergence": False,
            "avg_lag_days": None,
            "earliest_public_date": None,
            "earliest_tx_date": None
        }

    # Sort chronologically by event_date or publication_date
    sorted_events = sorted(events, key=lambda x: x.get("event_date") or x.get("publication_date") or datetime.utcnow())
    first_ev = sorted_events[0]
    last_ev = sorted_events[-1]

    tx_count = len(sorted_events)
    net_shares_delta = 0.0
    admin_count = 0
    pledge_count = 0
    release_pledge_count = 0
    acquire_count = 0
    dispose_count = 0

    lags = []
    earliest_pub_date = None
    earliest_tx_date = None

    for ev in sorted_events:
        delta_s = ev.get("delta_shares", 0.0)
        direction = ev.get("direction") or ev.get("event_type", "ACQUIRE")
        classification = ev.get("context_classification", "")
        admin_flag = ev.get("administrative_flag", False)
        pledge_flag = ev.get("pledge_flag", False)

        # Timing lag measurement (PRD Section 10 & 11)
        tx_dt = ev.get("transaction_date")
        pub_dt = ev.get("publication_date") or ev.get("event_date")

        if pub_dt:
            if not earliest_pub_date or pub_dt < earliest_pub_date:
                earliest_pub_date = pub_dt
        if tx_dt:
            if not earliest_tx_date or tx_dt < earliest_tx_date:
                earliest_tx_date = tx_dt

        if tx_dt and pub_dt and pub_dt >= tx_dt:
            lag = (pub_dt - tx_dt).days
            lags.append(lag)

        if admin_flag or classification == "ADMINISTRATIVE_TRANSFER":
            admin_count += 1
        elif pledge_flag or direction == "PLEDGE":
            pledge_count += 1
        elif direction == "RELEASE_PLEDGE":
            release_pledge_count += 1
        elif direction in ("ACQUIRE", "SUBSCRIBE", "EXERCISE"):
            net_shares_delta += delta_s
            acquire_count += 1
        elif direction == "DISPOSE":
            net_shares_delta -= delta_s
            dispose_count += 1

    pct_before = first_ev.get("pct_before", 0.0)
    pct_after = last_ev.get("pct_after", 0.0)
    net_delta_pct = round(pct_after - pct_before, 4) if (pct_before or pct_after) else 0.0

    avg_price = calculate_disclosed_cost_basis(sorted_events)
    crossings = detect_threshold_crossings(pct_before, pct_after)

    avg_lag = int(round(sum(lags) / len(lags))) if lags else None

    # Determine behavior classification (PRD Section 15 Anti-False-Positive Rules)
    is_pure_admin = (admin_count > 0 and acquire_count == 0 and dispose_count == 0 and pledge_count == 0)
    is_pure_pledge = (pledge_count > 0 and acquire_count == 0 and dispose_count == 0)
    is_pure_release = (release_pledge_count > 0 and acquire_count == 0 and dispose_count == 0)

    # Ownership convergence check (PRD Section 13)
    # Triggered when multiple independent ownership acquisitions reinforce one another
    ownership_convergence = (acquire_count >= 2 and net_shares_delta > 0 and not is_pure_admin)

    if is_pure_admin:
        behavior_type = "ADMINISTRATIVE_CHANGE"
    elif is_pure_pledge:
        behavior_type = "SHARE_PLEDGE_FINANCING"
    elif is_pure_release:
        behavior_type = "SHARE_PLEDGE_RELEASE"
    elif acquire_count >= 2 and net_shares_delta > 0:
        behavior_type = "ACCUMULATION_CANDIDATE"
    elif dispose_count >= 2 and net_shares_delta < 0:
        behavior_type = "DISTRIBUTION_CANDIDATE"
    elif crossings and any(c["direction"] == "UP" for c in crossings):
        behavior_type = "THRESHOLD_CROSSING"
    elif pct_before == 0 and pct_after > 0:
        behavior_type = "NEW_POSITION"
    elif net_shares_delta > 0:
        behavior_type = "STRATEGIC_POSITIONING_CANDIDATE"
    elif net_shares_delta < 0:
        behavior_type = "POSITION_REDUCTION"
    else:
        behavior_type = "STABLE_LARGE_HOLDER"

    return {
        "actor_id": actor_id,
        "company_id": company_id,
        "behavior_type": behavior_type,
        "transaction_count": tx_count,
        "total_shares_delta": net_shares_delta,
        "pct_before": pct_before,
        "pct_after": pct_after,
        "delta_pct": net_delta_pct,
        "avg_price": avg_price,
        "threshold_crossings": crossings,
        "has_pledge": (pledge_count > 0 or release_pledge_count > 0),
        "is_administrative": (admin_count > 0),
        "ownership_convergence": ownership_convergence,
        "avg_lag_days": avg_lag,
        "first_date": earliest_pub_date or first_ev.get("event_date"),
        "last_date": last_ev.get("event_date"),
        "earliest_public_date": earliest_pub_date,
        "earliest_tx_date": earliest_tx_date
    }
