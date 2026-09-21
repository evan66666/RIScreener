"""
Live test: fetch IDX announcements using Playwright (real Chromium browser).
This bypasses Cloudflare bot protection by running a real browser session.
Run: python backend/scripts/test_playwright_fetch.py
"""
import asyncio
import sys
sys.path.insert(0, 'backend')

from datetime import datetime, timedelta
from app.ingestion.idx_client import _try_playwright_fetch, _try_httpx_fetch

async def main():
    now = datetime.now()
    date_to = now
    date_from = now - timedelta(days=7)

    print("=" * 60)
    print("  IDX LIVE FETCH TEST")
    print(f"  Range: {date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}")
    print("=" * 60)

    print("\n[1] Trying httpx (fast path / stored cookies)...")
    results = await _try_httpx_fetch(date_from, date_to)
    if results:
        print(f"  SUCCESS! Got {len(results)} announcements via httpx")
        for r in results[:3]:
            print(f"    {r['ticker']} | {r['published_at'].strftime('%Y-%m-%d')} | {r['title'][:60]}")
    else:
        print("  httpx: No results (Cloudflare blocking headless requests)")

    print("\n[2] Trying Playwright (real browser, bypasses Cloudflare)...")
    results = await _try_playwright_fetch(date_from, date_to)
    if results:
        print(f"  SUCCESS! Got {len(results)} live IDX announcements via Playwright")
        for r in results[:5]:
            print(f"    {r['ticker']} | {r['published_at'].strftime('%Y-%m-%d')} | {r['title'][:70]}")
    else:
        print("  Playwright: No results returned from IDX")
        print("  (Note: IDX may restrict JSON API access even from real browsers)")
        print("  System will use local sample corpus as demo data source.")

    print("\nDone.")

asyncio.run(main())
