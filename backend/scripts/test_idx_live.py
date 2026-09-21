"""
Test live IDX API connectivity and discover working endpoints.
Run: python backend/scripts/test_idx_live.py
"""
import asyncio
import httpx
import json
from datetime import datetime, timedelta

async def test_idx_endpoints():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
        "Referer": "https://www.idx.co.id/id/berita/pengumuman/",
        "Origin": "https://www.idx.co.id",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    today = datetime.now().strftime("%Y%m%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

    # List of candidate endpoints to test
    endpoints = [
        # Main announcement API
        {
            "name": "IDX Announcement API (Primary)",
            "url": "https://www.idx.co.id/primary/NewsAnnouncement/GetAllAnnouncement",
            "params": {"indexFrom": 1, "pageSize": 10, "dateFrom": week_ago, "dateTo": today}
        },
        # E-Reporting API
        {
            "name": "IDX E-Reporting Announcement",
            "url": "https://efts.idx.co.id/FEEDS/SahamIDX",
            "params": {}
        },
        # IDX API v2
        {
            "name": "IDX API v2 Announcement",
            "url": "https://www.idx.co.id/api/announcement",
            "params": {"lang": "id", "start": "0", "length": "10"}
        },
        # IDX News
        {
            "name": "IDX IDXNet News",
            "url": "https://www.idx.co.id/umbraco/Surface/ListedCompany/GetLatestFundamentalReport",
            "params": {}
        },
        # IDX KSEI / OJK style
        {
            "name": "IDX Keterbukaan Informasi",
            "url": "https://efts.idx.co.id/primary/NewsAnnouncement/GetAllAnnouncement",
            "params": {"indexFrom": 1, "pageSize": 10, "dateFrom": week_ago, "dateTo": today}
        },
    ]

    print("=" * 65)
    print("  IDX API LIVE CONNECTIVITY TEST")
    print(f"  Date Range: {week_ago} to {today}")
    print("=" * 65)

    async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
        for ep in endpoints:
            try:
                resp = await client.get(ep["url"], params=ep["params"])
                ct = resp.headers.get("content-type", "")
                print(f"\n[{ep['name']}]")
                print(f"  Status: {resp.status_code}")
                print(f"  Content-Type: {ct[:60]}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        if isinstance(data, dict):
                            keys = list(data.keys())[:8]
                            print(f"  JSON Keys: {keys}")
                            total = data.get("Total") or data.get("total") or data.get("Count") or "?"
                            results = data.get("Results") or data.get("results") or data.get("replies") or []
                            print(f"  Total: {total}, Result items: {len(results)}")
                            if results and len(results) > 0:
                                first = results[0]
                                print(f"  First item keys: {list(first.keys())[:10]}")
                                print(f"  Sample ticker: {first.get('KodeEmiten') or first.get('ticker') or '?'}")
                                print(f"  Sample title: {str(first.get('JudulPengumuman') or first.get('title') or '?')[:80]}")
                        elif isinstance(data, list) and data:
                            print(f"  List with {len(data)} items, first keys: {list(data[0].keys())[:10]}")
                        else:
                            print(f"  Body (first 200 chars): {str(data)[:200]}")
                    except Exception:
                        print(f"  Raw body (200 chars): {resp.text[:200]}")
                else:
                    print(f"  Response: {resp.text[:150]}")
            except httpx.ConnectError as e:
                print(f"\n[{ep['name']}]")
                print(f"  ERROR: Connection refused / DNS failure: {e}")
            except httpx.TimeoutException:
                print(f"\n[{ep['name']}]")
                print(f"  ERROR: Timeout")
            except Exception as e:
                print(f"\n[{ep['name']}]")
                print(f"  ERROR: {type(e).__name__}: {e}")

asyncio.run(test_idx_endpoints())
