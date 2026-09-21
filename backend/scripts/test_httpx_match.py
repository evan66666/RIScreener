import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import httpx
import json

async def test_agent_and_httpx():
    profile_dir = Path("backend/data/chrome_profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1280, "height": 720}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://www.idx.co.id/id/berita/pengumuman/", timeout=30000)
        
        for _ in range(8):
            await asyncio.sleep(1)
            t = await page.title()
            if "Just a moment" not in t and "Tunggu" not in t:
                break
                
        user_agent = await page.evaluate("navigator.userAgent")
        print("Real Chrome User-Agent:", user_agent)
        
        cookies = await context.cookies()
        cf_cookies = {c["name"]: c["value"] for c in cookies if "idx.co.id" in c.get("domain", "")}
        await context.close()
        
    print(f"Captured {len(cf_cookies)} cookies, cf_clearance present: {'cf_clearance' in cf_cookies}")
    
    # Now test httpx with this exact User-Agent and cookies!
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
        "Referer": "https://www.idx.co.id/id/berita/pengumuman/",
        "Origin": "https://www.idx.co.id",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    
    async with httpx.AsyncClient(timeout=10.0, headers=headers, cookies=cf_cookies) as client:
        resp = await client.get("https://www.idx.co.id/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=10")
        print("httpx status:", resp.status_code)
        if resp.status_code == 200:
            try:
                data = resp.json()
                items = data.get("Items") or data.get("Results") or []
                print(f"HTTPX SUCCESS! Fetched {len(items)} announcements from IDX!")
                for item in items[:5]:
                    print(" ", item.get("KodeEmiten"), "|", item.get("Title") or item.get("JudulPengumuman"))
            except Exception as e:
                print("JSON parse error:", e)
        else:
            print("httpx body snippet:", resp.text[:200])

if __name__ == "__main__":
    asyncio.run(test_agent_and_httpx())
