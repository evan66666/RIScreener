import sys
from pathlib import Path
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')

from app.database import engine
from sqlmodel import Session, select
from app.models.schema import (
    OwnershipEvent, TransactionEvent, Actor, ActorBehaviorState,
    IssuerIntelligenceState, Company
)

def clean_bogus_data():
    print("=" * 60)
    print("  CLEANING BOGUS / PLACEHOLDER DATA FROM LIVE DATABASE")
    print("=" * 60)

    with Session(engine) as session:
        # 1. Delete 0-share bogus OwnershipEvents
        all_ow = session.exec(select(OwnershipEvent)).all()
        deleted_ow = 0
        for ow in all_ow:
            is_bogus = (
                (ow.shares_before == 0.0 and ow.shares_after == 0.0 and ow.delta_shares == 0.0 and not ow.pledge_flag) or
                (ow.actor and ow.actor.canonical_name == "Disclosed Strategic Holder" and ow.delta_shares == 0.0)
            )
            if is_bogus:
                session.delete(ow)
                deleted_ow += 1
        session.commit()
        print(f"Purged {deleted_ow} bogus 0-share OwnershipEvents.")

        # 2. Delete bogus 0-quantity TransactionEvents
        all_tx = session.exec(select(TransactionEvent)).all()
        deleted_tx = 0
        for tx in all_tx:
            if tx.quantity == 0.0:
                session.delete(tx)
                deleted_tx += 1
        session.commit()
        print(f"Purged {deleted_tx} bogus 0-quantity TransactionEvents.")

        # 3. Clean ActorBehaviorState pointing to Disclosed Strategic Holder with 0 delta
        all_beh = session.exec(select(ActorBehaviorState)).all()
        deleted_beh = 0
        for beh in all_beh:
            if (beh.actor and beh.actor.canonical_name == "Disclosed Strategic Holder") or beh.total_shares_delta == 0.0:
                session.delete(beh)
                deleted_beh += 1
        session.commit()
        print(f"Purged {deleted_beh} bogus ActorBehaviorStates.")

        # 4. Clean IssuerIntelligenceState pointing to bogus actor
        all_intels = session.exec(select(IssuerIntelligenceState)).all()
        cleaned_intels = 0
        for intel in all_intels:
            act = session.get(Actor, intel.primary_actor_id) if intel.primary_actor_id else None
            if act and act.canonical_name == "Disclosed Strategic Holder":
                # Check if there is any remaining real actor for this company
                real_ow = session.exec(
                    select(OwnershipEvent)
                    .where(OwnershipEvent.company_id == intel.company_id)
                ).first()
                if real_ow and real_ow.actor_id and real_ow.actor_id != act.id:
                    intel.primary_actor_id = real_ow.actor_id
                else:
                    intel.primary_actor_id = None
                
                # Clean summary text
                if intel.current_summary and "Disclosed Strategic Holder" in intel.current_summary:
                    comp = intel.company
                    t_str = f"{comp.ticker}: "
                    if intel.primary_action_type:
                        t_str += f"Action: {intel.primary_action_type.replace('_', ' ').title()}"
                    else:
                        t_str += "Keterbukaan Informasi & Pengawasan IDX"
                    intel.current_summary = t_str

                session.add(intel)
                cleaned_intels += 1
        session.commit()
        print(f"Cleaned {cleaned_intels} IssuerIntelligenceStates with bogus actor references.")

        # 5. Remove unused 'Disclosed Strategic Holder' actor
        bogus_actors = session.exec(
            select(Actor).where(Actor.canonical_name == "Disclosed Strategic Holder")
        ).all()
        for b_act in bogus_actors:
            # Check if any remaining events use this actor
            remaining_ow = session.exec(select(OwnershipEvent).where(OwnershipEvent.actor_id == b_act.id)).first()
            if not remaining_ow:
                session.delete(b_act)
                print(f"Deleted orphan placeholder Actor #{b_act.id}.")
        session.commit()

        print("\nDatabase cleanup finished successfully.")

if __name__ == "__main__":
    clean_bogus_data()
