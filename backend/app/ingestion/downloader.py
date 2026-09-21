import hashlib
import httpx
import tempfile
import asyncio
import base64
import time
from pathlib import Path
from typing import Tuple, Optional, Any, Dict, List
from app.config import settings

def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def calculate_bytes_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def _batch_download_sync(urls: List[str], output_dir: Path) -> Dict[str, Tuple[bool, str, Optional[str], Optional[Path]]]:
    """Sync worker executed in thread to batch download PDFs inside Chromium."""
    results: Dict[str, Tuple[bool, str, Optional[str], Optional[Path]]] = {}
    if not urls:
        return results

    remote_urls = []
    for u in urls:
        try:
            p = Path(u)
            if p.exists() and p.is_file():
                sha = calculate_sha256(p)
                results[u] = (True, "LOCAL_FILE", sha, p)
                continue
        except Exception:
            pass
        remote_urls.append(u)

    if not remote_urls:
        return results

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        for u in urls:
            results[u] = (False, "PLAYWRIGHT_NOT_INSTALLED", None, None)
        return results

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            profile_dir = settings.data_dir / "chrome_profile"
            profile_dir.mkdir(parents=True, exist_ok=True)

            try:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    channel="chrome",
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 720}
                )
            except Exception:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 720}
                )

            page = ctx.pages[0] if ctx.pages else ctx.new_page()

            try:
                page.goto("https://www.idx.co.id/id/berita/pengumuman/", wait_until="domcontentloaded", timeout=20000)
                import time
                for _ in range(6):
                    time.sleep(0.5)
                    t = page.title()
                    if "Just a moment" not in t and "Tunggu" not in t:
                        break
            except Exception:
                pass

            js_code = """async (urls) => {
                return await Promise.all(urls.map(async (url) => {
                    try {
                        const r = await fetch(url);
                        if (!r.ok) return { url, error: r.status };
                        const blob = await r.blob();
                        return await new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                const b64 = reader.result.split(',')[1];
                                resolve({ url, b64, size: blob.size });
                            };
                            reader.onerror = () => resolve({ url, error: 'BLOB_READ_ERROR' });
                            reader.readAsDataURL(blob);
                        });
                    } catch(e) {
                        return { url, error: e.toString() };
                    }
                }));
            }"""

            res = page.evaluate(js_code, remote_urls)
            ctx.close()

            for item in res:
                url = item.get("url", "")
                if "b64" in item and item["b64"]:
                    content = base64.b64decode(item["b64"])
                    sha256 = hashlib.sha256(content).hexdigest()
                    target_path = output_dir / f"{sha256}.pdf"
                    if not target_path.exists():
                        with open(target_path, "wb") as f:
                            f.write(content)
                    results[url] = (True, "DOWNLOADED", sha256, target_path)
                else:
                    err = item.get("error", "UNKNOWN")
                    results[url] = (False, f"DOWNLOAD_FAILED_{err}", None, None)

    except Exception as e:
        print(f"[Downloader] Batch download error: {e}")
        for u in remote_urls:
            if u not in results:
                results[u] = (False, f"DOWNLOAD_EXCEPTION_{str(e)}", None, None)

    return results

async def download_pdfs_batch(
    urls: List[str],
    output_dir: Path = settings.pdf_dir
) -> Dict[str, Tuple[bool, str, Optional[str], Optional[Path]]]:
    """Asynchronously download a batch of PDFs safely using Chromium context."""
    return await asyncio.to_thread(_batch_download_sync, urls, output_dir)

async def download_pdf_file(
    pdf_url: str,
    output_dir: Path = settings.pdf_dir,
    page: Any = None
) -> Tuple[bool, str, Optional[str], Optional[Path]]:
    """Downloads single PDF safely."""
    if not pdf_url:
        return False, "PDF_UNAVAILABLE", None, None

    if pdf_url.startswith("file://") or Path(pdf_url).exists():
        path_str = pdf_url.replace("file://", "")
        p = Path(path_str)
        if p.exists():
            sha256 = calculate_sha256(p)
            return True, "DOWNLOADED", sha256, p

    res_dict = await download_pdfs_batch([pdf_url], output_dir)
    return res_dict.get(pdf_url, (False, "DOWNLOAD_FAILED", None, None))
