import asyncio
import sys
from pathlib import Path
sys.path.insert(0, 'backend')

from app.database import engine, init_db
from sqlmodel import Session, select
from app.models.schema import (
    Company, Actor, ActorAlias, ActorRelationship,
    InvestorClassification, MarketStructureSnapshot,
    Announcement, Document, DocumentPage,
    OwnershipSnapshot, OwnershipEvent, TransactionEvent,
    CorporateActionEvent, DocumentSignal, Evidence,
    ActorBehaviorState, IssuerActionState, SignalEvent,
    CorporateActionAssessment, IssuerIntelligenceState, Scan
)
from app.ingestion.master_companies import IDX_MASTER_COMPANIES
from app.engine.pipeline import execute_screening_pipeline
from datetime import datetime, timedelta

async def purge_and_run_live():
    print("=" * 65)
    print("  PURGING ALL SAMPLE DATA & PREPARING 100% REAL IDX SYSTEM")
    print("=" * 65)

    # 1. Initialize tables if needed
    init_db()

    # 2. Delete all records from every table
    all_models = [
        Evidence, DocumentSignal, SignalEvent, CorporateActionAssessment,
        IssuerIntelligenceState, IssuerActionState, ActorBehaviorState,
        TransactionEvent, OwnershipEvent, OwnershipSnapshot,
        MarketStructureSnapshot, InvestorClassification, ActorRelationship,
        ActorAlias, Actor, DocumentPage, Document, Announcement, Scan, Company
    ]

    with Session(engine) as session:
        print("\n[1/4] Purging all database records...")
        for model in all_models:
            deleted_count = 0
            for item in session.exec(select(model)).all():
                session.delete(item)
                deleted_count += 1
            if deleted_count > 0:
                print(f"  - Cleared {deleted_count} rows from {model.__tablename__}")
        session.commit()
        print("  Database completely clean.")

        # 3. Populate master IDX companies
        print(f"\n[2/4] Registering {len(IDX_MASTER_COMPANIES)} master IDX listed companies...")
        for c in IDX_MASTER_COMPANIES:
            comp = Company(
                ticker=c["ticker"],
                name=c["name"],
                sector=c.get("sector")
            )
            session.add(comp)
        session.commit()
        print("  Master listed companies registered.")

    # 4. Clean all sample PDFs from data/pdfs/
    print("\n[3/4] Purging sample PDF files from backend/data/pdfs/...")
    pdf_dir = Path("backend/data/pdfs")
    if pdf_dir.exists():
        deleted_pdfs = 0
        for f in pdf_dir.glob("*.pdf"):
            try:
                f.unlink()
                deleted_pdfs += 1
            except Exception:
                pass
        print(f"  Purged {deleted_pdfs} PDF files.")

    # 5. Execute live screening from IDX
    print("\n[4/4] Executing Live Screening from IDX (real keterbukaan informasi)...")
    now = datetime.now()
    scan_from = now - timedelta(days=7)
    scan_to = now

    with Session(engine) as session:
        scan = await execute_screening_pipeline(
            session=session,
            scan_from=scan_from.replace(hour=0, minute=0, second=0, microsecond=0),
            scan_to=scan_to.replace(hour=23, minute=59, second=59, microsecond=999999),
            lookback_days=60,
            scan_mode="smart"
        )

        print("\n" + "=" * 65)
        print("  LIVE IDX SCREENING COMPLETED SUCCESSFULLY")
        print("=" * 65)
        print(f"  Status:                  {scan.status}")
        print(f"  Announcements Retrieved: {scan.announcements_found}")
        print(f"  Documents Processed:     {scan.documents_processed}")
        print(f"  PDFs Downloaded:         {scan.pdfs_downloaded}")
        print(f"  PDFs Extracted:          {scan.pdfs_extracted}")
        print(f"  Ownership Events:        {scan.ownership_events_found}")
        print(f"  Strategic Candidates:    {scan.strategic_positioning_candidates}")
        print(f"  Total Signals:           {scan.important_signals_found}")
        print(f"  Early Signals:           {scan.early_signals_count}")
        print(f"  Developing Signals:      {scan.developing_signals_count}")
        print(f"  Explicit Signals:        {scan.explicit_signals_count}")

        # Summary of real companies detected
        detected_states = session.exec(select(IssuerActionState)).all()
        print(f"\nReal IDX Issuer Action Signals in Database ({len(detected_states)}):")
        for s in detected_states:
            ticker = s.company.ticker if s.company else "?"
            print(f"  [{s.current_stage:<10}] {ticker:<6} | {s.action_type:<24} | Impact: {s.current_impact:<8} | Priority: {s.priority}")

        intel_states = session.exec(select(IssuerIntelligenceState)).all()
        print(f"\nReal IDX Smart Money / Strategic Intelligence ({len(intel_states)}):")
        for st in intel_states:
            comp = session.get(Company, st.company_id)
            ticker = comp.ticker if comp else "?"
            print(f"  [{st.overall_priority:<9}] {ticker:<6} | SM Score: {st.smart_money_score:2d} | CA Score: {st.corporate_action_score:2d} | Behavior: {st.primary_behavior or 'N/A'}")

if __name__ == "__main__":
    asyncio.run(purge_and_run_live())
