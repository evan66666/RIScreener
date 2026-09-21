import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import json

async def fetch_live_idx(page_size: int = 50):
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
        
        print("Navigating to IDX...")
        await page.goto("https://www.idx.co.id/id/berita/pengumuman/", wait_until="domcontentloaded", timeout=30000)
        
        for _ in range(8):
            await asyncio.sleep(1)
            t = await page.title()
            if "Just a moment" not in t and "Tunggu" not in t:
                break
                
        print("Page title:", await page.title())
        
        res = await page.evaluate(f'''async () => {{
            try {{
                const r = await fetch("/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize={page_size}", {{
                    headers: {{
                        "Accept": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    }}
                }});
                return await r.json();
            }} catch(e) {{
                return {{ error: e.toString() }};
            }}
        }}''')
        
        items = res.get("Items") or res.get("Results") or []
        print(f"TOTAL REAL ANNOUNCEMENTS FETCHED FROM IDX: {len(items)}")
        for idx, item in enumerate(items[:15]):
            ticker = item.get("KodeEmiten") or item.get("Code") or "?"
            title = item.get("JudulPengumuman") or item.get("Title") or "?"
            date_val = item.get("TanggalPengumuman") or item.get("PublishDate") or "?"
            print(f"  {idx+1:2d}. [{ticker:<6}] {date_val} | {title[:70]}")
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(fetch_live_idx(50))
