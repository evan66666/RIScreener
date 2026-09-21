"""
Deep investigation of IDX API - capture actual network requests from browser
to discover the correct API calls, headers, and tokens.
"""
import asyncio
import json
import sys
sys.path.insert(0, 'backend')

from datetime import datetime, timedelta

async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright not installed")
        return

    now = datetime.now()
    date_from = (now - timedelta(days=7)).strftime("%Y%m%d")
    date_to = now.strftime("%Y%m%d")

    captured = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            locale="id-ID",
        )
        
        page = await context.new_page()
        
        # Intercept all network requests/responses
        async def capture_response(response):
            url = response.url
            if ("idx.co.id" in url and 
                response.status == 200 and
                any(kw in url.lower() for kw in ["announcement", "news", "disclosure", "keterbukaan", "pengumuman"])):
                try:
                    body = await response.json()
                    captured.append({
                        "url": url,
                        "status": response.status,
                        "body_keys": list(body.keys()) if isinstance(body, dict) else "list",
                        "count": len(body.get("Results", body.get("results", body if isinstance(body, list) else []))),
                        "sample": str(body)[:300]
                    })
                    print(f"  CAPTURED JSON: {url}")
                    print(f"  Keys: {list(body.keys()) if isinstance(body, dict) else 'list'}")
                    if isinstance(body, dict):
                        items = body.get("Results") or body.get("results") or body.get("replies") or []
                        if items and len(items) > 0:
                            first = items[0]
                            print(f"  First item: {str(first)[:200]}")
                except Exception:
                    ct = response.headers.get("content-type", "")
                    if "json" in ct:
                        print(f"  JSON URL (failed parse): {url}")
        
        page.on("response", capture_response)
        
        print("Opening IDX announcement page...")
        try:
            await page.goto("https://www.idx.co.id/id/berita/pengumuman/", 
                          wait_until="networkidle", timeout=30000)
            print("Page loaded, waiting for API calls...")
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Page load error: {e}")
        
        print(f"\nCaptured {len(captured)} JSON API calls")
        
        if not captured:
            # Try scrolling to trigger lazy loading
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
            except Exception:
                pass
            print(f"After scroll: {len(captured)} JSON API calls")
        
        # Get page cookies for future use
        cookies = await context.cookies()
        idx_cookies = {c["name"]: c["value"] for c in cookies if "idx" in c.get("domain", "").lower()}
        print(f"\nIDX cookies captured: {list(idx_cookies.keys())[:10]}")
        
        # Save cookies
        from app.config import settings
        cookie_file = settings.data_dir / "idx_cookies.json"
        with open(cookie_file, "w") as f:
            json.dump(idx_cookies, f)
        print(f"Cookies saved to {cookie_file}")
        
        # Try fetching the API directly from within the browser page context (same origin)
        print("\nTrying in-page fetch (same-origin)...")
        try:
            result = await page.evaluate(f"""
                async () => {{
                    try {{
                        const resp = await fetch('/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=10&dateFrom={date_from}&dateTo={date_to}', {{
                            headers: {{
                                'Accept': 'application/json',
                                'X-Requested-With': 'XMLHttpRequest'
                            }}
                        }});
                        const data = await resp.json();
                        return {{ status: resp.status, data: data }};
                    }} catch(e) {{
                        return {{ error: e.toString() }};
                    }}
                }}
            """)
            print(f"In-page fetch result: {json.dumps(result)[:400]}")
        except Exception as e:
            print(f"In-page fetch error: {e}")
        
        await browser.close()

asyncio.run(main())
