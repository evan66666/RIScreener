import asyncio
import sys
sys.path.insert(0, 'backend')

from app.database import engine
from sqlmodel import Session, select
from app.ingestion.bootstrap import run_historical_bootstrap
from app.models.schema import IssuerActionState
from app.engine.pipeline import execute_screening_pipeline
from datetime import datetime

async def main():
    with Session(engine) as session:
        print("Starting clean re-bootstrap...")
        await run_historical_bootstrap(session, lookback_days=60, force=True)
        print("Re-bootstrap complete.")
        
        # Run 1 screening scan to generate latest Scan summary record
        now = datetime.now()
        scan = await execute_screening_pipeline(
            session=session,
            scan_from=now.replace(hour=0, minute=0, second=0),
            scan_to=now.replace(hour=23, minute=59, second=59),
            lookback_days=60
        )
        print(f"Scan completed: id={scan.id}, early={scan.early_signals_count}, dev={scan.developing_signals_count}, explicit={scan.explicit_signals_count}")

        states = session.exec(select(IssuerActionState)).all()
        print(f"\nTotal IssuerActionStates: {len(states)}")
        stages = {}
        for s in states:
            ticker = s.company.ticker if s.company else "?"
            print(f"  {ticker:<6} {s.action_type:<24} Stage: {s.current_stage:<12} Priority: {s.priority:<8} Docs: {s.corroborating_docs_count}")
            stages[s.current_stage] = stages.get(s.current_stage, 0) + 1
        print("\nStage Summary:", stages)

if __name__ == "__main__":
    asyncio.run(main())
