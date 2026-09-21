import asyncio
import sys
sys.path.insert(0, 'backend')

from app.ingestion.idx_client import _try_playwright_fetch
from datetime import datetime, timedelta
from app.ingestion.master_companies import IDX_MASTER_COMPANIES

master_set = {c['ticker'] for c in IDX_MASTER_COMPANIES}

async def main():
    items = await _try_playwright_fetch(datetime.now() - timedelta(days=7), datetime.now())
    print(f"Total raw announcements from IDX: {len(items)}")
    
    routine_pats = [
        "nilai aktiva bersih",
        "unit penyertaan",
        "registrasi pemegang efek",
        "kurs valuta asing",
        "bukti iklan",
        "laporan harian",
    ]

    focused = []
    for i in items:
        t = i["title"].lower()
        ticker = i["ticker"]
        # Skip routine mutual fund / ETF / daily reports
        if any(p in t for p in routine_pats):
            continue
        if ticker.startswith("R-") or (ticker.startswith("X") and ticker not in master_set):
            continue
        focused.append(i)

    print(f"Focused Keterbukaan Informasi count: {len(focused)} (from {len(items)} raw)")
    print("\nSample 25 Focused Keterbukaan Informasi Disclosures:")
    for i in focused[:25]:
        print(f"  {i['ticker']:<6} | {i['published_at'].strftime('%Y-%m-%d')} | {i['title'][:70]}")

if __name__ == "__main__":
    asyncio.run(main())
