from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from app.models.schema import (
    Announcement, Company, Document, DocumentPage,
    DocumentSignal, Evidence, IssuerActionState, SignalEvent
)
from app.ingestion.master_companies import IDX_MASTER_COMPANIES

async def run_historical_bootstrap(session: Session, lookback_days: int = 60, force: bool = False) -> bool:
    """
    Mandatory first-run bootstrap:
    Registers all master IDX listed companies so live ticker mapping works seamlessly.
    No mock or sample corpus is injected.
    """
    # 1. Populate all master companies
    existing_tickers = {c.ticker for c in session.exec(select(Company)).all()}
    added = 0
    for master in IDX_MASTER_COMPANIES:
        if master["ticker"] not in existing_tickers:
            company = Company(
                ticker=master["ticker"],
                name=master["name"],
                sector=master["sector"]
            )
            session.add(company)
            added += 1
    session.commit()

    if force:
        # Clean any existing records for fresh start
        for model_cls in [Evidence, DocumentSignal, SignalEvent, IssuerActionState, DocumentPage, Document, Announcement]:
            for row in session.exec(select(model_cls)).all():
                session.delete(row)
        session.commit()

    return added > 0
