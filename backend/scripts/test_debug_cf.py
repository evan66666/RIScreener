import asyncio
from playwright.async_api import async_playwright

async def test_idx():
    async with async_playwright() as p:
        # Try launching real Chrome
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
            locale="id-ID",
        )
        page = await context.new_page()
        
        print("Navigating to IDX...")
        try:
            resp = await page.goto("https://www.idx.co.id/id/berita/pengumuman/", wait_until="domcontentloaded", timeout=20000)
            print("Status:", resp.status if resp else "No response")
            print("Title:", await page.title())
            await asyncio.sleep(3)
            print("Title after 3s:", await page.title())
            
            # Check content
            content = await page.content()
            print("Has Cloudflare Turnstile:", "cf-turnstile" in content or "Just a moment" in content)
            print("URL:", page.url)
            
            # Check if GetAllAnnouncement can be fetched
            res = await page.evaluate('''async () => {
                try {
                    const r = await fetch("/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize=5", {
                        headers: { "Accept": "application/json", "X-Requested-With": "XMLHttpRequest" }
                    });
                    const t = await r.text();
                    return { status: r.status, text: t.substring(0, 200) };
                } catch(e) {
                    return { error: e.toString() };
                }
            }''')
            print("API result:", res)
            
            cookies = await context.cookies()
            print("Cookies count:", len(cookies))
            for c in cookies:
                print("Cookie:", c["name"], c["domain"])
                
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_idx())
