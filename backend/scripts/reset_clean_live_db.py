import asyncio
import sys
from pathlib import Path
sys.path.insert(0, 'backend')

from app.database import engine, init_db
from sqlmodel import Session, select
from app.models.schema import (
    Company, Announcement, Document, DocumentPage,
    DocumentSignal, Evidence, IssuerActionState, SignalEvent, Scan
)
from app.ingestion.master_companies import IDX_MASTER_COMPANIES
from app.engine.pipeline import execute_screening_pipeline
from datetime import datetime, timedelta

async def reset_to_pure_live():
    print("=" * 60)
    print("  PURGING ALL SAMPLE DATA & INITIALIZING CLEAN LIVE DB")
    print("=" * 60)

    # 1. Initialize tables
    init_db()

    # 2. Clean all data
    with Session(engine) as session:
        print("Wiping all existing tables...")
        for model in [Evidence, DocumentSignal, SignalEvent, IssuerActionState, DocumentPage, Document, Announcement, Scan, Company]:
            for item in session.exec(select(model)).all():
                session.delete(item)
        session.commit()
        print("Database wiped clean.")

        # 3. Populate all master companies
        print(f"Registering {len(IDX_MASTER_COMPANIES)} master IDX companies...")
        for c in IDX_MASTER_COMPANIES:
            comp = Company(
                ticker=c["ticker"],
                name=c["name"],
                sector=c.get("sector")
            )
            session.add(comp)
        session.commit()
        print("Master companies registered successfully.")

        # 4. Clean PDFs directory
        pdf_dir = Path("backend/data/pdfs")
        if pdf_dir.exists():
            for f in pdf_dir.glob("*.pdf"):
                try:
                    f.unlink()
                except Exception:
                    pass
            print("PDF cache directory purged.")

        # 5. Run Live Screening for last 7 days from IDX
        now = datetime.now()
        scan_from = now - timedelta(days=7)
        scan_to = now

        print(f"\nRunning Live IDX Screening for range {scan_from.strftime('%Y-%m-%d')} to {scan_to.strftime('%Y-%m-%d')}...")
        scan = await execute_screening_pipeline(
            session=session,
            scan_from=scan_from.replace(hour=0, minute=0, second=0),
            scan_to=scan_to.replace(hour=23, minute=59, second=59),
            lookback_days=60
        )

        print(f"\nScan completed with Status: {scan.status}")
        print(f"  Announcements Retrieved: {scan.announcements_found}")
        print(f"  Documents Processed:     {scan.documents_processed}")
        print(f"  PDFs Downloaded:         {scan.pdfs_downloaded}")
        print(f"  PDFs Extracted:          {scan.pdfs_extracted}")
        print(f"  Important Signals Found: {scan.important_signals_found}")
        print(f"  Early Signals:           {scan.early_signals_count}")
        print(f"  Developing Signals:      {scan.developing_signals_count}")
        print(f"  Explicit Signals:        {scan.explicit_signals_count}")

        # List all detected live states
        states = session.exec(select(IssuerActionState)).all()
        print(f"\nLive Active Issuer States in Database ({len(states)}):")
        for s in states:
            ticker = s.company.ticker if s.company else "?"
            print(f"  [{s.current_stage:<10}] {ticker:<6} | {s.action_type:<24} | Priority: {s.priority:<6} | Docs: {s.corroborating_docs_count}")

if __name__ == "__main__":
    asyncio.run(reset_to_pure_live())
