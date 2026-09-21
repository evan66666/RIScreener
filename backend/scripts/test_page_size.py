from playwright.sync_api import sync_playwright
import time
from pathlib import Path

profile_dir = Path('backend/data/chrome_profile')
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(profile_dir),
        channel='chrome',
        headless=False,
        args=['--disable-blink-features=AutomationControlled'],
        viewport={'width': 1280, 'height': 720}
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto('https://www.idx.co.id/id/berita/pengumuman/', wait_until='domcontentloaded')
    time.sleep(2)
    
    for ps in [100, 50, 20]:
        url = f'/primary/NewsAnnouncement/GetAllAnnouncement?indexFrom=1&pageSize={ps}&dateFrom=20260914&dateTo=20260921'
        r = page.evaluate(f'''async () => {{
            try {{
                const res = await fetch('{url}', {{ headers: {{ 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }} }});
                return await res.json();
            }} catch(e) {{
                return {{ error: e.toString() }};
            }}
        }}''')
        items = r.get('Items') or r.get('Results') or []
        print(f"pageSize={ps}: items={len(items)}, total={r.get('ItemCount') or r.get('Total')}")
    context.close()
