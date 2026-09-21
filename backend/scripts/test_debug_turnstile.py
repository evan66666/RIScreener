import asyncio
from playwright.async_api import async_playwright

async def inspect_turnstile():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        
        await page.goto("https://www.idx.co.id/id/berita/pengumuman/", wait_until="domcontentloaded")
        
        for sec in range(12):
            await asyncio.sleep(1)
            title = await page.title()
            print(f"Sec {sec+1}: Title = {title}")
            frames = page.frames
            print(f"  Frames: {[f.url for f in frames]}")
            if "Pengumuman" in title and "Tunggu" not in title and "Just a moment" not in title:
                print("PASSED CLOUDFLARE!")
                cookies = await context.cookies()
                for c in cookies:
                    print("Cookie:", c["name"])
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_turnstile())
