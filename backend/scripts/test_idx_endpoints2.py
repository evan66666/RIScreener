"""
Live IDX endpoint discovery - testing all known IDX API variants.
"""
import asyncio
import httpx

async def test_all():
    # Test headers with a Cloudflare-bypass approach
    # IDX uses Cloudflare; we need a proper session cookie approach.
    
    # Strategy 1: IDX API with proper cookies
    headers_v1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://www.idx.co.id/id/berita/pengumuman/",
        "Origin": "https://www.idx.co.id",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    # Strategy 2: IDXNet portal API (different subdomain)
    headers_v2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://idxnet.idx.co.id/",
    }

    endpoints = [
        # IDX primary with session simulation
        ("IDX with session", "GET", "https://www.idx.co.id/primary/NewsAnnouncement/GetAllAnnouncement",
         {"indexFrom": "1", "pageSize": "5", "dateFrom": "20260826", "dateTo": "20260902"}, headers_v1),
        
        # IDXNet API (known to work for listed companies)
        ("IDXNet Listed Companies", "GET", "https://www.idx.co.id/primary/ListedCompany/GetCompanyProfiles",
         {"start": "0", "length": "10", "code": ""}, headers_v1),
        
        # OJK SIPEDAS - regulator source
        ("OJK Disclosure", "GET", "https://efts.idx.co.id/FEEDS/DisclosureAnnouncement",
         {}, headers_v2),
        
        # IDX CORS proxy via CDN
        ("IDX via CORS", "GET", "https://cors.bridged.cc/https://www.idx.co.id/primary/NewsAnnouncement/GetAllAnnouncement",
         {"indexFrom": "1", "pageSize": "5", "dateFrom": "20260826", "dateTo": "20260902"}, headers_v1),
        
        # KSEI Investor Area - public disclosures
        ("KSEI AKSes", "GET", "https://akses.ksei.co.id/api/v1/securities/disclosure",
         {}, headers_v2),
        
        # Directly test if idx.co.id resolves
        ("IDX Homepage", "GET", "https://www.idx.co.id/", {}, headers_v1),
    ]

    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        for name, method, url, params, hdrs in endpoints:
            try:
                r = await client.request(method, url, params=params, headers=hdrs)
                preview = r.text[:120].replace("\n", " ")
                print(f"[{name}] {r.status_code} | {r.headers.get('content-type','?')[:40]} | {preview}")
            except Exception as e:
                print(f"[{name}] ERROR: {type(e).__name__}: {str(e)[:80]}")

asyncio.run(test_all())
