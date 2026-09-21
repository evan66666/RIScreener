import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )
        page = await context.new_page()
        
        print("1. Visiting Pengumuman page...")
        await page.goto("https://www.idx.co.id/id/berita/pengumuman/", wait_until="domcontentloaded")
        await asyncio.sleep(2.0)
        
        # Test how GetAllAnnouncement is called on Pengumuman page
        res = await page.evaluate('''async () => {
            const r = await fetch("/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=5&dateFrom=20260901&dateTo=20260902", {
                headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }
            });
            return await r.json();
        }''')
        print("Sample item keys from GetAllAnnouncement:", list(res.get("Items", [{}])[0].keys()) if res.get("Items") else "No items")
        if res.get("Items"):
            for item in res["Items"][:5]:
                print("  Type/Category:", item.get("AnnouncementType"), "| Sub:", item.get("SubCategory"), "| Judul:", item.get("Title") or item.get("JudulPengumuman"))

        print("\n2. Visiting Keterbukaan Informasi page if exists...")
        try:
            await page.goto("https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/", wait_until="networkidle", timeout=15000)
            print("Current URL:", page.url)
        except Exception as e:
            print("Navigation note:", e)

        # Check all distinct announcement categories and types from the API
        print("\n3. Testing distinct types in GetAllAnnouncement...")
        res_types = await page.evaluate('''async () => {
            const r = await fetch("/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=100&dateFrom=20260825&dateTo=20260902", {
                headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }
            });
            const data = await r.json();
            const items = data.Items || data.Results || [];
            const types = new Set(items.map(i => i.AnnouncementType || i.JenisPengumuman || i.category));
            return Array.from(types);
        }''')
        print("Distinct AnnouncementTypes found:", res_types)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
