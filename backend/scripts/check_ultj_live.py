import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import json

async def check_ultj_on_idx():
    profile_dir = Path("backend/data/chrome_profile")
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
        await page.goto("https://www.idx.co.id/id/berita/pengumuman/", timeout=30000)
        
        for i in range(12):
            await asyncio.sleep(1)
            title = await page.title()
            if "Just a moment" not in title and "Tunggu" not in title and "Attention" not in title:
                print(f"PASSED CF on sec {i+1}")
                break
        
        print("Current page title:", await page.title())
        
        # Test 1: Query announcements specifically with kodeEmiten=ULTJ
        res_ultj = await page.evaluate('''async () => {
            const r = await fetch("/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=50&kodeEmiten=ULTJ", {
                headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }
            });
            return await r.json();
        }''')
        
        items = res_ultj.get("Items") or res_ultj.get("Results") or []
        print(f"Total items for kodeEmiten=ULTJ: {len(items)}, ItemCount: {res_ultj.get('ItemCount')}")
        for item in items[:15]:
            tgl = item.get("TanggalPengumuman") or item.get("PublishDate")
            kd = item.get("KodeEmiten")
            jd = item.get("JudulPengumuman")
            print(f"[{tgl}] {kd} - {jd}")

        # Test 2: Query announcements specifically with keyword=ULTJ
        res_kw = await page.evaluate('''async () => {
            const r = await fetch("/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=50&keyword=ULTJ", {
                headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }
            });
            return await r.json();
        }''')
        items_kw = res_kw.get("Items") or res_kw.get("Results") or []
        print(f"Total items for keyword=ULTJ: {len(items_kw)}, ItemCount: {res_kw.get('ItemCount')}")
        for item in items_kw[:15]:
            tgl = item.get("TanggalPengumuman") or item.get("PublishDate")
            kd = item.get("KodeEmiten")
            jd = item.get("JudulPengumuman")
            print(f"[{tgl}] {kd} - {jd}")

        # Update cookies
        cookies = await context.cookies()
        cf_cookies = {c["name"]: c["value"] for c in cookies if "idx.co.id" in c.get("domain", "")}
        with open("backend/data/idx_cookies.json", "w") as f:
            json.dump(cf_cookies, f)

        await context.close()

if __name__ == "__main__":
    asyncio.run(check_ultj_on_idx())
