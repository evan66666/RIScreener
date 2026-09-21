import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import json

async def test_headful():
    print("Testing with real Chrome headful...")
    profile_dir = Path("backend/data/chrome_profile")
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                ],
                viewport={"width": 1280, "height": 720}
            )
        except Exception as e:
            print("Failed to launch Chrome:", e)
            return

        page = context.pages[0] if context.pages else await context.new_page()
        
        print("Navigating to IDX...")
        try:
            await page.goto("https://www.idx.co.id/id/berita/pengumuman/", timeout=30000)
            print("Loaded page. Title:", await page.title())
            
            for i in range(10):
                await asyncio.sleep(1)
                title = await page.title()
                print(f"Sec {i+1}: {title}")
                if "Just a moment" not in title and "Tunggu" not in title:
                    print("SUCCESSFULLY PASSED!")
                    
                    # Try fetch API
                    res = await page.evaluate('''async () => {
                        const r = await fetch("/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=5", {
                            headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }
                        });
                        return await r.json();
                    }''')
                    items = res.get("Items") or res.get("Results") or []
                    print(f"FETCHED {len(items)} REAL ANNOUNCEMENTS!")
                    if items:
                        print("Sample item:", items[0].get("Title") or items[0].get("JudulPengumuman"))
                    
                    cookies = await context.cookies()
                    cf_cookies = {c["name"]: c["value"] for c in cookies if "idx.co.id" in c.get("domain", "")}
                    with open("backend/data/idx_cookies.json", "w") as f:
                        json.dump(cf_cookies, f)
                    print("Saved cookies to backend/data/idx_cookies.json")
                    break
        except Exception as e:
            print("Error during navigation/fetch:", e)
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(test_headful())
