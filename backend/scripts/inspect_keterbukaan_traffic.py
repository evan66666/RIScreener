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
        
        calls = []
        page.on("request", lambda r: calls.append((r.url, r.method, r.post_data)))
        page.on("response", lambda r: print("RESPONSE:", r.status, r.url[:120]))

        print("Visiting https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/ ...")
        await page.goto("https://www.idx.co.id/id/perusahaan-tercatat/keterbukaan-informasi/", wait_until="networkidle", timeout=30000)
        
        # Check inputs, buttons, tables
        elements = await page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll("input, select, button")).map(el => ({
                tag: el.tagName,
                id: el.id,
                type: el.type,
                name: el.name,
                text: (el.innerText || el.value || el.placeholder || "").trim(),
                className: el.className
            }));
            return items;
        }''')
        print("Interactive elements count:", len(elements))
        for item in elements:
            print("  ", item)

        # Click search
        print("\nClicking Cari / Terapkan button...")
        btn = page.locator("button:has-text('Cari'), button:has-text('Terapkan'), button:has-text('Search')")
        if await btn.count() > 0:
            await btn.first.click()
            await asyncio.sleep(4)

        print("\nAll API calls intercepted:")
        for url, method, post_data in calls:
            if "primary" in url or "api" in url:
                print(f"[{method}] {url}")
                if post_data:
                    print("  POST data:", post_data)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
