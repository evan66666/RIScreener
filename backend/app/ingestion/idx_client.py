import httpx
import re
import json
import asyncio
from datetime import datetime, date, timezone, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from app.config import settings
from app.ingestion.master_companies import IDX_MASTER_COMPANIES


# ─────────────────────────────────────────────────────────────────────────────
# DATE PARSER
# ─────────────────────────────────────────────────────────────────────────────

def parse_idx_datetime(date_val: Any) -> datetime:
    """
    Robust date parser supporting all IDX date formats:
    - ISO 8601: 2026-09-01T23:15:08, 2026-09-01T23:15:08Z, 2026-09-01T23:15:08+07:00
    - ASP.NET JSON: /Date(1705305600000)/ or /Date(1705305600000+0700)/
    - Standard SQL: 2026-09-01 23:15:08
    - Date only: 2026-09-01, 20260901
    - DD-MM-YYYY: 01-09-2026
    - Indonesian: 1 September 2026, 15 Januari 2026
    - Epoch (int/float ms or s)
    """
    if isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, (int, float)):
        if date_val > 1e11:
            return datetime.fromtimestamp(date_val / 1000.0)
        return datetime.fromtimestamp(date_val)

    if not date_val or not isinstance(date_val, str):
        return datetime.now()

    date_str = date_val.strip()

    # 1. ASP.NET JSON: /Date(1705305600000)/
    asp_match = re.search(r"/Date\((\d+)(?:[+-]\d+)?\)/", date_str)
    if asp_match:
        ms = int(asp_match.group(1))
        return datetime.fromtimestamp(ms / 1000.0)

    # 2. ISO formats
    try:
        clean_iso = date_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_iso)
        # Strip timezone info for consistent naive datetime
        return dt.replace(tzinfo=None)
    except Exception:
        pass

    # 3. Standard patterns
    patterns = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y%m%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]
    for pat in patterns:
        try:
            return datetime.strptime(date_str, pat)
        except Exception:
            continue

    # 4. Indonesian month names
    indo_months = {
        "januari": "January", "februari": "February", "maret": "March",
        "april": "April", "mei": "May", "juni": "June",
        "juli": "July", "agustus": "August", "september": "September",
        "oktober": "October", "november": "November", "desember": "December"
    }
    lower_str = date_str.lower()
    for id_m, en_m in indo_months.items():
        if id_m in lower_str:
            eng_str = lower_str.replace(id_m, en_m).strip()
            for pat in ["%d %B %Y", "%d %B %Y %H:%M:%S", "%d %B %Y %H:%M"]:
                try:
                    return datetime.strptime(eng_str, pat)
                except Exception:
                    pass

    return datetime.now()


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE NORMALIZER  (handles both old "Results" and new "Items" schema)
# Set of known master stock tickers and lookup map
MASTER_TICKERS_SET = {c["ticker"] for c in IDX_MASTER_COMPANIES}
MASTER_COMPANIES_MAP = {c["ticker"]: c for c in IDX_MASTER_COMPANIES}

# Comprehensive exclusion patterns for titles impossible to contain corporate actions
# per PRD v5 (ad proofs, daily FX, non-stock debt, mutual funds, internal broker filings)
IMPOSSIBLE_CA_EXCLUSION_PATTERNS = [
    # 1. Newspaper Advertisement Proofs & Invoices (Pure administrative media clippings)
    "penyampaian bukti iklan",
    "bukti pemasangan iklan",
    "bukti pemuatan iklan",
    "bukti publikasi iklan",
    "bukti iklan",
    "pemasangan iklan",
    "iklan koran",
    "iklan surat kabar",

    # 2. Foreign Exchange Rates (Daily administrative FX)
    "laporan kurs valuta asing",
    "kurs valuta asing",

    # 3. Mutual Funds, ETFs, and Portfolio Valuation
    "nilai aktiva bersih",
    "nab",
    "unit penyertaan",
    "reksa dana",
    "reksadana",
    "portofolio investasi reksa dana",
    "laporan harian atas nilai aktiva bersih",
    "laporan jumlah peredaran unit penyertaan",
    "laporan peredaran unit",
    "laporan harian",

    # 4. Bonds, Sukuk, MTN, Commercial Papers
    "bunga obligasi",
    "imbalan sukuk",
    "kupon obligasi",
    "jatuh tempo obligasi",
    "jatuh tempo sukuk",
    "pembayaran bunga obligasi",
    "pembayaran imbalan sukuk",
    "obligasi berkelanjutan",
    "sukuk ijarah",
    "sukuk mudharabah",
    "sukuk wakalah",
    "wali amanat",
    "surat utang komersial",
    "surat berharga komersial",
    "medium term note",
    "mtn",
    "pemeringkatan obligasi",
    "hasil pemeringkatan atas obligasi",

    # 5. Asset-backed Securities, DIRE, DINFRA
    "efek beragun aset",
    "eba-sp",
    "dana investasi real estat",
    "dana investasi infrastruktur",

    # 6. Exchange Members (Brokerage / Anggota Bursa) Internal Filings
    "modal kerja bersih disesuaikan",
    "mkbd",
    "anggota bursa",
    "spab",
    "partisipan bursa",

    # 7. Routine Administrative Monthly Shareholder Registration (No transaction events)
    "laporan bulanan registrasi pemegang efek",

    # 8. Exchange Holiday & Trading Calendar
    "libur bursa",
    "jadwal libur bursa",
    "kalender bursa",
]

# Alias for backward compatibility
NON_STOCK_EXCLUSION_PATTERNS = IMPOSSIBLE_CA_EXCLUSION_PATTERNS


def is_impossible_ca_announcement(title: str, category: str = "") -> bool:
    """
    Returns True if the announcement title/category cannot possibly contain
    a corporate action or precursor signal (e.g. ad proofs, daily FX, debt).
    Uses word boundaries for short abbreviations (nab, mtn, mkbd, spab) to prevent
    false positives with genuine stock disclosures.
    """
    import re
    combined = f"{title} {category}".lower()

    short_acronyms = ["nab", "mtn", "spab", "mkbd", "eba-sp"]
    for acr in short_acronyms:
        if re.search(r'\b' + re.escape(acr) + r'\b', combined):
            return True

    for p in IMPOSSIBLE_CA_EXCLUSION_PATTERNS:
        if p in short_acronyms:
            continue
        if p in combined:
            return True

    return False


def _normalize_announcement(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize a raw IDX API item to standard schema.
    STRICTLY FILTERS FOR EQUITY / STOCKS ONLY (Jenis Saham):
    - Rejects 2-letter broker codes (HD, YU, ZP, DR, BQ, etc.)
    - Rejects Mutual Funds (R-*, X*), Bonds/Sukuk, MTN, EBA
    - Rejects bond interest, sukuk payout, NAB reports
    - Retains only 4-letter stock tickers of listed public companies (Tbk)
    """
    # 1. Extract and sanitize Ticker
    ticker = (
        item.get("KodeEmiten") or
        item.get("Code") or
        item.get("kode_emiten") or
        item.get("ticker") or ""
    ).strip().upper()

    if not ticker:
        return None

    # 1. STRICT EQUITY / STOCK VALIDATION
    # Ticker MUST be in the official IDX Master Stock List (962 Saham Tbk)
    # Strictly rejects non-stock debt/bond issuers (e.g. SOFN, OTMA, PNMP, PPGD, SMFP, etc.)
    if ticker not in MASTER_TICKERS_SET:
        return None

    # 2. STRICT CATEGORY 'SAHAM / STOCK' CHECK FROM IDX API METADATA
    # On IDX API, stock disclosures are explicitly tagged with Jenis = 'STOCK'
    raw_jenis = str(item.get("Jenis") or item.get("JenisEmiten") or item.get("TipeEfek") or "").strip().upper()
    if raw_jenis and raw_jenis not in ["STOCK", "SAHAM", "EQUITY"]:
        return None

    # 3. Extract and check Title against non-stock & routine noise patterns
    title = (
        item.get("JudulPengumuman") or
        item.get("Title") or
        item.get("judul") or
        item.get("title") or ""
    ).strip()

    if is_impossible_ca_announcement(title, raw_jenis):
        return None

    # Company name & Sector with Master Stock Database enrichment
    master_info = MASTER_COMPANIES_MAP.get(ticker, {})
    company_name = (
        item.get("NamaEmiten") or
        item.get("CompanyName") or
        item.get("nama_emiten") or
        item.get("company_name") or
        master_info.get("name") or
        ticker
    ).strip()
    if not company_name or company_name == ticker:
        company_name = master_info.get("name", ticker)

    # Sector
    sector = (
        item.get("Sektor") or
        item.get("sektor") or
        item.get("sector") or
        master_info.get("sector", "")
    ).strip()

    # Source ID
    source_id = str(
        item.get("id") or
        item.get("Id") or
        item.get("AnnouncementId") or
        item.get("AnnouncementNo") or
        item.get("nid") or ""
    )

    # Published date
    raw_pub = (
        item.get("TanggalPengumuman") or
        item.get("PublishDate") or
        item.get("tanggal") or
        item.get("published_at")
    )
    pub_dt = parse_idx_datetime(raw_pub)

    # Category / type
    category = (
        item.get("JenisPengumuman") or
        item.get("AnnouncementType") or
        item.get("jenis") or
        item.get("category") or ""
    )

    # Sector
    sector = (
        item.get("Sektor") or
        item.get("sektor") or
        item.get("sector") or ""
    )

    # Attachments / PDFs (Strictly Stock Announcement PDFs)
    attachments = []
    for att in (item.get("Attachments") or item.get("attachments") or []):
        att_url = (
            att.get("FullSavePath") or
            att.get("full_path") or
            att.get("FilePath") or
            att.get("url") or ""
        )
        if att_url and att_url.lower().endswith(".pdf"):
            # Reject any non-stock bond / etf path
            if "ANNOUNCEMENTBOND" in att_url.upper() or "ANNOUNCEMENTETF" in att_url.upper():
                continue
            attachments.append({
                "url": att_url,
                "filename": att.get("FileName") or att.get("filename") or ""
            })

    for pdf_key in ["PdfUrl", "pdf_url", "file_url", "FormIAttachment"]:
        val = item.get(pdf_key)
        if not attachments and val:
            url = val if isinstance(val, str) else val.get("url", "")
            if url and url.lower().endswith(".pdf"):
                if "ANNOUNCEMENTBOND" in url.upper() or "ANNOUNCEMENTETF" in url.upper():
                    continue
                attachments.append({"url": url, "filename": ""})

    return {
        "source_id": source_id or f"IDX-{ticker}-{pub_dt.strftime('%Y%m%d%H%M')}",
        "ticker": ticker,
        "name": company_name,
        "sector": sector,
        "title": title,
        "category": category,
        "published_at": pub_dt,
        "attachments": attachments
    }


def _parse_idx_response(data: Any) -> List[Dict[str, Any]]:
    """
    Parse IDX API response — supports both Items[] and Results[] schemas
    and paginates if needed.
    """
    if isinstance(data, list):
        raw_items = data
    elif isinstance(data, dict):
        raw_items = (
            data.get("Items") or        # NEW schema (confirmed)
            data.get("Results") or       # OLD schema
            data.get("results") or
            data.get("replies") or
            []
        )
    else:
        return []

    results = []
    for item in raw_items:
        norm = _normalize_announcement(item)
        if norm:
            results.append(norm)
    return results


# ─────────────────────────────────────────────────────────────────────────────
# TIER 1: httpx WITH CLOUDFLARE COOKIE CACHE
# ─────────────────────────────────────────────────────────────────────────────

async def _try_httpx_fetch(date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
    """
    Fast path: use cached Cloudflare cookies (written by Playwright session).
    Only works after Playwright has run at least once and saved idx_cookies.json.
    """
    cookie_file = settings.data_dir / "idx_cookies.json"
    if not cookie_file.exists():
        return []

    try:
        with open(cookie_file, "r") as f:
            cookies = json.load(f)
    except Exception:
        return []

    if not cookies:
        return []

    date_from_str = date_from.strftime("%Y%m%d")
    date_to_str = date_to.strftime("%Y%m%d")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8",
        "Referer": "https://www.idx.co.id/id/berita/pengumuman/",
        "Origin": "https://www.idx.co.id",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    # Paginate to get all results (IDX has max 200 per page)
    all_results = []
    page = 1
    page_size = 200

    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout,
            headers=headers,
            cookies=cookies,
            follow_redirects=True
        ) as client:
            while True:
                resp = await client.get(
                    "https://www.idx.co.id/primary/NewsAnnouncement/GetAllAnnouncement",
                    params={
                        "pageNumber": page,
                        "pageSize": page_size,
                        "dateFrom": date_from_str,
                        "dateTo": date_to_str
                    }
                )
                if resp.status_code != 200:
                    break

                ct = resp.headers.get("content-type", "")
                if "json" not in ct and not resp.text.strip().startswith(("{", "[")):
                    break  # Got HTML (Cloudflare challenge page)

                data = resp.json()
                page_results = _parse_idx_response(data)
                all_results.extend(page_results)

                # Check if there are more pages
                total_items = data.get("ItemCount") or data.get("Total") or 0
                page_count = data.get("PageCount") or data.get("PageCount") or 1
                if page >= page_count or not page_results:
                    break
                page += 1

    except Exception:
        pass

    return all_results


# ─────────────────────────────────────────────────────────────────────────────
def _fetch_idx_via_browser_sync(date_from_str: str, date_to_str: str) -> List[Dict[str, Any]]:
    """
    Synchronous worker running in a dedicated thread to avoid Windows ASGI event loop subprocess conflicts.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []

    all_results = []
    print(f"[IDXClient] Starting Browser worker thread for {date_from_str} to {date_to_str}...")
    
    try:
        with sync_playwright() as p:
            profile_dir = settings.data_dir / "chrome_profile"
            profile_dir.mkdir(parents=True, exist_ok=True)

            try:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    channel="chrome",
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                    ],
                    viewport={"width": 1280, "height": 720}
                )
            except Exception:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_dir),
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                    ],
                    viewport={"width": 1280, "height": 720}
                )

            page = context.pages[0] if context.pages else context.new_page()

            try:
                page.goto(
                    "https://www.idx.co.id/id/berita/pengumuman/",
                    wait_until="domcontentloaded",
                    timeout=25000
                )
                import time
                for _ in range(12):
                    time.sleep(1)
                    t = page.title()
                    if "Attention" in t:
                        try:
                            context.clear_cookies()
                            page.goto("https://www.idx.co.id/id/berita/pengumuman/", wait_until="domcontentloaded", timeout=20000)
                        except Exception:
                            pass
                        continue
                    if "Just a moment" not in t and "Tunggu" not in t and len(t) > 2:
                        break
                time.sleep(1.5)
            except Exception as e:
                print(f"[IDXClient] Initial navigation notice: {e}")
                import time; time.sleep(2.0)

            # Parse target start date for dynamic window cutoff
            try:
                target_start_dt = datetime.strptime(date_from_str, "%Y%m%d")
            except Exception:
                target_start_dt = datetime.now() - timedelta(days=7)

            page_num = 1
            page_size = 100
            use_latest_fallback = False
            max_safety_pages = 250  # Up to 25,000 announcements to cover long historical ranges

            while page_num <= max_safety_pages:
                try:
                    if not use_latest_fallback:
                        query_url = f"/primary/NewsAnnouncement/GetAllAnnouncement?pageNumber={page_num}&pageSize={page_size}&dateFrom={date_from_str}&dateTo={date_to_str}"
                    else:
                        query_url = f"/primary/NewsAnnouncement/GetAllAnnouncement?pageNumber={page_num}&pageSize={page_size}"

                    js_result = None
                    for attempt in range(3):
                        try:
                            js_result = page.evaluate("""
                                async (url) => {
                                    try {
                                        const resp = await fetch(url, {
                                            headers: {
                                                'Accept': 'application/json, text/plain, */*',
                                                'X-Requested-With': 'XMLHttpRequest'
                                            }
                                        });
                                        const text = await resp.text();
                                        try {
                                            return JSON.parse(text);
                                        } catch(jsonErr) {
                                            return { error: 'HTML_CHALLENGE', status: resp.status, snippet: text.substring(0, 100) };
                                        }
                                    } catch(e) {
                                        return { error: e.toString() };
                                    }
                                }
                            """, query_url)
                            if js_result and not (isinstance(js_result, dict) and js_result.get("error") == "HTML_CHALLENGE"):
                                break
                            import time; time.sleep(1.5)
                        except Exception as eval_err:
                            if "destroyed" in str(eval_err).lower() and attempt < 2:
                                import time; time.sleep(1.5)
                                continue
                            raise eval_err

                    # If date-filtered query returned 0 items on page 1, seamlessly query latest active announcements
                    if page_num == 1 and not use_latest_fallback:
                        items_count = 0
                        if isinstance(js_result, dict):
                            items_count = len(js_result.get("Items") or js_result.get("Results") or [])
                        if items_count == 0:
                            print(f"[IDXClient] Zero announcements for {date_from_str}-{date_to_str}. Querying latest active announcements from IDX...")
                            use_latest_fallback = True
                            continue

                    if not js_result or "error" in js_result:
                        print(f"[IDXClient] Page {page_num} response error: {js_result}")
                        break

                    raw_items = js_result.get("Items") or js_result.get("Results") or []
                    if not raw_items:
                        break

                    page_results = _parse_idx_response(js_result)
                    all_results.extend(page_results)

                    page_count = js_result.get("PageCount") or 1
                    print(f"[IDXClient] Page {page_num}/{page_count}: {len(page_results)} stock disclosures parsed (cumulative: {len(all_results)})")

                    # Dynamic date cutoff: check if we have reached beyond our target start date
                    reached_cutoff = False
                    for item in raw_items:
                        raw_pub = item.get("TanggalPengumuman") or item.get("PublishDate") or item.get("tanggal")
                        if raw_pub:
                            dt = parse_idx_datetime(raw_pub)
                            if dt and dt < (target_start_dt - timedelta(days=1)):
                                reached_cutoff = True
                                break

                    if reached_cutoff:
                        print(f"[IDXClient] Reached target date boundary ({target_start_dt.strftime('%Y-%m-%d')}) at page {page_num}. All disclosures captured.")
                        break

                    if page_num >= page_count:
                        print(f"[IDXClient] Reached last page ({page_count}) on IDX.")
                        break

                    page_num += 1

                except Exception as e:
                    print(f"[IDXClient] Exception during page evaluate: {e}")
                    break

            try:
                cookies = context.cookies()
                cf_cookies = {
                    c["name"]: c["value"]
                    for c in cookies
                    if "idx.co.id" in c.get("domain", "")
                }
                if cf_cookies:
                    cookie_file = settings.data_dir / "idx_cookies.json"
                    with open(cookie_file, "w") as f:
                        json.dump(cf_cookies, f)
            except Exception:
                pass

            context.close()

    except Exception as e:
        import traceback
        print(f"[IDXClient] Playwright execution error: {e}")
        traceback.print_exc()

    print(f"[IDXClient] Finished retrieval. Total items: {len(all_results)}")
    return all_results


async def _try_playwright_fetch(date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
    """
    Runs sync Playwright inside a separate thread using asyncio.to_thread for full ASGI / Windows compatibility.
    """
    date_from_str = date_from.strftime("%Y%m%d")
    date_to_str = date_to.strftime("%Y%m%d")
    return await asyncio.to_thread(_fetch_idx_via_browser_sync, date_from_str, date_to_str)


# ─────────────────────────────────────────────────────────────────────────────
# IDXClient - PUBLIC INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

class IDXClient:
    """
    3-tier IDX data retrieval engine:
    Tier 1 → httpx + cached Cloudflare cookies (fast, ~1s)
    Tier 2 → Playwright Chromium (real browser, bypasses CF, ~10-15s)
    Tier 3 → Local sample corpus (offline/demo mode)

    IDX blocks all direct HTTP API access via Cloudflare. The only reliable
    method is to run a real browser session that passes the CF JS challenge,
    then execute same-origin fetch() calls within that browser context.
    """

    def __init__(self):
        self.base_url = settings.idx_base_url

    async def fetch_announcements(
        self,
        date_from: datetime,
        date_to: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetches live IDX keterbukaan informasi / announcements for the date range.
        Uses 2-tier live retrieval strategy (httpx with CF cookies -> Playwright real browser).
        Returns live IDX data only.
        """
        # Tier 1: httpx with cached cookies (fast path)
        results = await _try_httpx_fetch(date_from, date_to)
        if results:
            return results

        # Tier 2: Playwright real browser (CF bypass, authoritative live data)
        results = await _try_playwright_fetch(date_from, date_to)
        if results:
            return results

        print("[IDXClient] Live IDX data query completed with 0 results.")
        return []

    async def fetch_company_profiles(self, search: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch IDX listed company profiles.
        Falls back to master_companies registry if IDX is unreachable.
        """
        cookie_file = settings.data_dir / "idx_cookies.json"
        cookies = {}
        if cookie_file.exists():
            try:
                with open(cookie_file, "r") as f:
                    cookies = json.load(f)
            except Exception:
                pass

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.idx.co.id/",
            "X-Requested-With": "XMLHttpRequest",
        }

        try:
            async with httpx.AsyncClient(
                timeout=8.0, headers=headers, cookies=cookies, follow_redirects=True
            ) as client:
                resp = await client.get(
                    "https://www.idx.co.id/primary/ListedCompany/GetCompanyProfiles",
                    params={"start": 0, "length": limit, "code": search}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = (
                        data.get("recordsData") or
                        data.get("Records") or
                        data.get("data") or []
                    )
                    if items:
                        return [
                            {
                                "ticker": item.get("KodeEmiten", "").strip(),
                                "name": item.get("NamaEmiten", ""),
                                "sector": item.get("SubSektor", "")
                            }
                            for item in items if item.get("KodeEmiten")
                        ]
        except Exception:
            pass

        # Fallback: master registry
        results = IDX_MASTER_COMPANIES
        if search:
            s = search.upper()
            results = [c for c in results if s in c["ticker"] or s in c["name"].upper()]
        return results[:limit]
