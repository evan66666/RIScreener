import asyncio
from playwright.async_api import async_playwright

async def click_turnstile():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()
        
        print("Navigating to IDX...")
        await page.goto("https://www.idx.co.id/id/berita/pengumuman/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        print("Locating Turnstile iframe...")
        ts_iframe = page.frame_locator("iframe[src*='challenges.cloudflare.com']")
        
        # Try clicking the checkbox inside the Turnstile iframe
        try:
            cb = ts_iframe.locator("input[type='checkbox'], span.mark, div#challenge-stage, body")
            await cb.first.click(timeout=5000)
            print("Clicked Turnstile element!")
        except Exception as e:
            print("Click error:", e)
            
        for i in range(10):
            await asyncio.sleep(1)
            title = await page.title()
            print(f"After click +{i+1}s: {title}")
            if "Just a moment" not in title and "Tunggu" not in title:
                print("SUCCESSFULLY BYPASSED CLOUDFLARE!")
                cookies = await context.cookies()
                for c in cookies:
                    print("Cookie:", c["name"])
                break
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(click_turnstile())
