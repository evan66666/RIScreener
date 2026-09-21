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

def reset_all_clean():
    print("=" * 60)
    print("  RESETTING SYSTEM TO CLEAN PRISTINE STATE")
    print("=" * 60)

    # 1. Initialize tables
    init_db()

    # 2. Wipe database records
    with Session(engine) as session:
        print("Clearing all screening data tables...")
        for model in [Evidence, DocumentSignal, SignalEvent, IssuerActionState, DocumentPage, Document, Announcement, Scan, Company]:
            for item in session.exec(select(model)).all():
                session.delete(item)
        session.commit()
        print("Tables cleared.")

        # 3. Re-seed master companies only
        print(f"Registering {len(IDX_MASTER_COMPANIES)} master IDX companies...")
        for c in IDX_MASTER_COMPANIES:
            comp = Company(
                ticker=c["ticker"],
                name=c["name"],
                sector=c.get("sector")
            )
            session.add(comp)
        session.commit()
        print("Master companies ready.")

    # 4. Clean all PDFs in backend/data/pdfs/
    pdf_dir = Path("backend/data/pdfs")
    if pdf_dir.exists():
        pdf_count = 0
        for f in pdf_dir.glob("*.pdf"):
            try:
                f.unlink()
                pdf_count += 1
            except Exception:
                pass
        print(f"Deleted {pdf_count} PDF files from {pdf_dir}.")

    print("\nSUCCESS! The system is now 100% clean and ready.")
    print("No PDFs will be downloaded until you click 'RUN SCREENING' in the frontend.")

if __name__ == "__main__":
    reset_all_clean()
