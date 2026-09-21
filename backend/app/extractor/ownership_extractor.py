import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.rules.definitions import (
    DIRECTION_PATTERNS,
    ADMINISTRATIVE_TRIGGERS,
    PLEDGE_EVENT_TYPES,
    INVESTOR_CLASS_MAP,
    INVESTOR_KEYWORD_PATTERNS,
    HSC_PATTERNS,
    FREE_FLOAT_PATTERNS
)

INDONESIAN_MONTHS = {
    "januari": 1, "jan": 1,
    "februari": 2, "feb": 2,
    "maret": 3, "mar": 3,
    "april": 4, "apr": 4,
    "mei": 5, "may": 5,
    "juni": 6, "jun": 6,
    "juli": 7, "jul": 7,
    "agustus": 8, "agu": 8, "agt": 8, "aug": 8,
    "september": 9, "sep": 9,
    "oktober": 10, "okt": 10, "oct": 10,
    "november": 11, "nov": 11,
    "desember": 12, "des": 12, "dec": 12
}


def _parse_date(text: str) -> Optional[datetime]:
    """Helper to parse Indonesian and ISO date formats from text."""
    if not text:
        return None
    cleaned = text.strip().lower()

    # Pattern: 15 Agustus 2026 or 15-Agustus-2026
    m1 = re.search(r"(\d{1,2})[\s\-\/]+([a-z]+)[\s\-\/]+(\d{4})", cleaned)
    if m1:
        d = int(m1.group(1))
        m_str = m1.group(2)
        y = int(m1.group(3))
        m = INDONESIAN_MONTHS.get(m_str)
        if m and 1 <= d <= 31 and 2000 <= y <= 2100:
            try:
                return datetime(y, m, d)
            except ValueError:
                pass

    # Pattern: 15/08/2026 or 15-08-2026
    m2 = re.search(r"(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})", cleaned)
    if m2:
        d = int(m2.group(1))
        m = int(m2.group(2))
        y = int(m2.group(3))
        if 1 <= d <= 31 and 1 <= m <= 12 and 2000 <= y <= 2100:
            try:
                return datetime(y, m, d)
            except ValueError:
                pass

    # Pattern: 2026-08-15
    m3 = re.search(r"(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})", cleaned)
    if m3:
        y = int(m3.group(1))
        m = int(m3.group(2))
        d = int(m3.group(3))
        if 1 <= d <= 31 and 1 <= m <= 12 and 2000 <= y <= 2100:
            try:
                return datetime(y, m, d)
            except ValueError:
                pass

    return None


def _parse_number(text: str) -> Optional[float]:
    """Helper to parse Indonesian formatted numbers (1.500.000, 15,25%)."""
    if not text:
        return None
    cleaned = text.strip().replace(" ", "")
    # Remove Rp or USD if present
    cleaned = re.sub(r"^(?:rp\.?|usd|\$)\s*", "", cleaned, flags=re.IGNORECASE)
    # Check if format is like 1.250.000,50 or 15,25
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    elif "." in cleaned:
        parts = cleaned.split(".")
        if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3 and not parts[1].endswith("0")):
            cleaned = cleaned.replace(".", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_investor_class(raw_class: str, actor_name: str = "", context: str = "") -> str:
    """Normalizes raw class string or actor context to standard v7.2 class."""
    clean_raw = raw_class.strip().lower()
    if clean_raw in INVESTOR_CLASS_MAP:
        return INVESTOR_CLASS_MAP[clean_raw]
    
    combined = f"{raw_class} {actor_name} {context}".lower()
    for pat, norm in INVESTOR_KEYWORD_PATTERNS:
        if re.search(pat, combined):
            return norm
    return "OTHER"


def extract_ownership_facts_from_text(
    full_text: str,
    title: str = "",
    published_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Extracts structured ownership change disclosures from text with v7.2 enhancements:
    - 3 Timestamps: transaction_date, reporting_date, publication_date
    - Share pledge/release event family (POJK 4/2024 compliance)
    - Administrative & affiliate transfer flags
    - Investor classifications & Beneficial Owner / Controller disclosures
    - Market Structure (HSC & Free Float context)
    """
    results = []
    combined = f"{title}\n{full_text}"

    # Check if text is relevant to ownership, director transaction, pledge, or HSC
    ownership_indicator = re.search(
        r"(?:laporan\s+perubahan\s+kepemilikan|laporan\s+transaksi\s+saham|kepemilikan\s+saham|"
        r"transaksi\s+direksi|laporan\s+pengendali|pemegang\s+saham\s+utama|pengalihan\s+saham|"
        r"pemberitahuan\s+pengalihan|gadai\s+saham|penjaminan\s+saham|pelepasan\s+gadai|"
        r"konsentrasi\s+kepemilikan|high\s+shareholding\s+concentration|\bhsc\b|free\s+float|daftar\s+pemegang\s+saham)",
        combined,
        re.IGNORECASE
    )
    if not ownership_indicator and not any(k in title.lower() for k in ["kepemilikan", "transaksi saham", "direksi", "pengalihan", "gadai", "hsc", "float"]):
        return []

    # 1. Determine Direction & Share Pledge status (PRD v7.2 Section 4.5)
    direction = "ACQUIRE"
    pledge_flag = False
    pledge_type = None

    for p_type, patterns in PLEDGE_EVENT_TYPES.items():
        if any(re.search(pat, combined, re.IGNORECASE) for pat in patterns):
            pledge_flag = True
            pledge_type = p_type
            if p_type == "PLEDGE_RELEASED":
                direction = "RELEASE_PLEDGE"
            else:
                direction = "PLEDGE"
            break

    if not pledge_flag:
        for dir_key, patterns in DIRECTION_PATTERNS.items():
            if any(re.search(pat, combined, re.IGNORECASE) for pat in patterns):
                direction = dir_key
                break

    # 2. Check Administrative Context & Affiliate Flags (PRD v7.2 Section 4.6)
    is_admin = any(re.search(pat, combined, re.IGNORECASE) for pat in ADMINISTRATIVE_TRIGGERS)
    is_related_party = bool(re.search(r"\b(?:afiliasi|pihak\s+terafiliasi|hubungan\s+afiliasi|entitas\s+anak|grup\s+usaha)\b", combined, re.IGNORECASE))
    
    if is_admin:
        context_classification = "ADMINISTRATIVE_TRANSFER"
    elif pledge_flag:
        context_classification = "FINANCING_LIQUIDITY_PRESSURE" if direction == "PLEDGE" else "PLEDGE_RELEASE"
    elif direction == "ACQUIRE":
        context_classification = "MARKET_ACQUISITION_CANDIDATE"
    elif direction == "DISPOSE":
        context_classification = "MARKET_DISPOSAL_CANDIDATE"
    elif direction in ("SUBSCRIBE", "EXERCISE", "CONVERT"):
        context_classification = "CORPORATE_ACTION_EFFECT"
    else:
        context_classification = "UNCLEAR"

    # 3. Extract Dates (PRD v7.2 Section 10 - Timing Integrity)
    publication_date = published_date or datetime.utcnow()
    transaction_date = None
    reporting_date = None

    # Search for transaction date: "Tanggal Transaksi: 15 Agustus 2026"
    tx_date_match = re.search(
        r"(?:tanggal\s+transaksi|tanggal\s+pelaksanaan|tanggal\s+perolehan|tanggal\s+penjualan|tanggal\s+gadai)\s*[:=]?\s*([0-9A-Za-z\s\-\/\,]+?)(?:\n|\r|;|\.|\,?\s+tujuan|\,?\s+harga)",
        combined,
        re.IGNORECASE
    )
    if tx_date_match:
        transaction_date = _parse_date(tx_date_match.group(1))

    # Search for reporting date: "Tanggal Laporan / Tanggal Surat / Tanggal Keterbukaan"
    rep_date_match = re.search(
        r"(?:tanggal\s+laporan|tanggal\s+surat|tanggal\s+pemberitahuan)\s*[:=]?\s*([0-9A-Za-z\s\-\/\,]+?)(?:\n|\r|;|\.)",
        combined,
        re.IGNORECASE
    )
    if rep_date_match:
        reporting_date = _parse_date(rep_date_match.group(1))

    # Fallback transaction date if not explicitly matched
    if not transaction_date:
        transaction_date = publication_date

    # 4. Extract Actor Name
    actor_name = ""
    actor_match = re.search(
        r"(?:nama\s+pemegang\s+saham|nama\s+pihak\s+yang\s+melakukan\s+transaksi|nama\s+direktur\/komisaris|nama(?:\s+pelapor)?)\s*[:=]\s*([A-Za-z0-9\.\,\s\(\)\-]+?)(?:\n|\r|;|\.|\,?\s+jabatan)",
        combined,
        re.IGNORECASE
    )
    if actor_match:
        actor_name = actor_match.group(1).strip()
    else:
        by_match = re.search(r"transaksi\s+saham\s+oleh\s+([A-Za-z0-9\.\,\s]+?)(?:\s+pada|\s+sehubungan|\n|\r|$)", title, re.IGNORECASE)
        if by_match:
            actor_name = by_match.group(1).strip()

    if not actor_name or len(actor_name) < 2:
        actor_name = "Disclosed Strategic Holder"

    # 5. Extract Investor Classification & Domicile (PRD v7.2 Section 5)
    raw_investor_class = ""
    role_match = re.search(r"jabatan\s*[:=]?\s*([A-Za-z0-9\s\,\.\-]+?)(?:\n|\r|;|\.)", combined, re.IGNORECASE)
    if role_match:
        raw_investor_class = role_match.group(1).strip()
    else:
        status_match = re.search(r"status\s+pemegang\s+saham\s*[:=]?\s*([A-Za-z0-9\s\,\.\-]+?)(?:\n|\r|;|\.)", combined, re.IGNORECASE)
        if status_match:
            raw_investor_class = status_match.group(1).strip()

    normalized_class = normalize_investor_class(raw_investor_class, actor_name, combined)
    
    # Domicile
    domicile = "DOMESTIC"
    if re.search(r"\b(?:asing|foreign|warga\s+negara\s+asing|wna|overseas)\b", combined, re.IGNORECASE):
        domicile = "FOREIGN"

    # 6. Extract Beneficial Owner / Controller Disclosures (PRD v7.2 Section 6)
    beneficial_owner_name = None
    controller_name = None
    ubo_match = re.search(
        r"(?:pemilik\s+manfaat|ultimate\s+beneficial\s+owner|ubo|pengendali\s+akhir)(?:\s*\([^\)]*\))?\s*[:=]?\s*([A-Za-z0-9\.\,\s\-]+?)(?:\n|\r|;|\.|\,?\s+jumlah|\,?\s+pemegang)",
        combined,
        re.IGNORECASE
    )
    if ubo_match:
        beneficial_owner_name = ubo_match.group(1).strip()

    ctrl_match = re.search(
        r"(?:pengendali\s+(?:perseroan|emiten)|pemegang\s+saham\s+pengendali)(?:\s*\([^\)]*\))?\s*[:=]?\s*([A-Za-z0-9\.\,\s\-]+?)(?:\n|\r|;|\.|\,?\s+jumlah)",
        combined,
        re.IGNORECASE
    )
    if ctrl_match:
        controller_name = ctrl_match.group(1).strip()

    # 7. Extract Shares Before & After
    shares_before = 0.0
    shares_after = 0.0
    delta_shares = 0.0

    before_match = re.search(
        r"(?:sebelum\s+transaksi|sebelumnya|jumlah\s+saham\s+yang\s+dimiliki\s+sebelum)\s*[:=]?\s*([0-9\.\,]+)\s*(?:saham|lembar)?",
        combined,
        re.IGNORECASE
    )
    if before_match:
        val = _parse_number(before_match.group(1))
        if val is not None:
            shares_before = val

    after_match = re.search(
        r"(?:setelah|sesudah)\s+transaksi\s*[:=]?\s*([0-9\.\,]+)\s*(?:saham|lembar)?",
        combined,
        re.IGNORECASE
    )
    if after_match:
        val = _parse_number(after_match.group(1))
        if val is not None:
            shares_after = val

    delta_match = re.search(
        r"(?:jumlah\s+saham\s+yang\s+(?:dibeli|dijual|dialihkan|digadaikan)|jumlah\s+transaksi)\s*[:=]?\s*([0-9\.\,]+)\s*(?:saham|lembar)?",
        combined,
        re.IGNORECASE
    )
    if delta_match:
        val = _parse_number(delta_match.group(1))
        if val is not None:
            delta_shares = val
    elif shares_after and shares_before:
        delta_shares = abs(shares_after - shares_before)

    # 8. Extract Percentages
    pct_before = 0.0
    pct_after = 0.0
    delta_pct = 0.0

    pct_before_match = re.search(
        r"(?:persentase|porsi)\s*(?:kepemilikan)?\s*sebelum\s+transaksi\s*[:=]?\s*([0-9\.\,]+)\s*%",
        combined,
        re.IGNORECASE
    )
    if pct_before_match:
        val = _parse_number(pct_before_match.group(1))
        if val is not None:
            pct_before = val
    else:
        # Fallback: parenthesized percentage after "sebelum transaksi"
        paren_before = re.search(
            r"(?:sebelum\s+transaksi|sebelumnya)[^\n\r%]*?\(([0-9\.\,]+)\s*%\)",
            combined,
            re.IGNORECASE
        )
        if paren_before:
            val = _parse_number(paren_before.group(1))
            if val is not None:
                pct_before = val

    pct_after_match = re.search(
        r"(?:persentase|porsi)\s*(?:kepemilikan)?\s*(?:setelah|sesudah)\s+transaksi\s*[:=]?\s*([0-9\.\,]+)\s*%",
        combined,
        re.IGNORECASE
    )
    if pct_after_match:
        val = _parse_number(pct_after_match.group(1))
        if val is not None:
            pct_after = val
    else:
        # Fallback: parenthesized percentage after "setelah transaksi"
        paren_after = re.search(
            r"(?:setelah|sesudah)\s+transaksi[^\n\r%]*?\(([0-9\.\,]+)\s*%\)",
            combined,
            re.IGNORECASE
        )
        if paren_after:
            val = _parse_number(paren_after.group(1))
            if val is not None:
                pct_after = val

    if pct_after and pct_before:
        delta_pct = round(pct_after - pct_before, 4)
    elif delta_shares and shares_after and pct_after:
        total_shares = shares_after / (pct_after / 100.0)
        delta_pct = round((delta_shares / total_shares) * 100.0, 4) if total_shares > 0 else 0.0

    # 9. Extract Price
    price = None
    price_match = re.search(
        r"(?:harga\s+transaksi|harga\s+pembelian|harga\s+penjualan|harga\s+per\s+saham|harga\s+pelaksanaan)\s*[:=]?\s*(?:rp\.?|usd|\$)?\s*([0-9\.\,]+)",
        combined,
        re.IGNORECASE
    )
    if price_match:
        price_val = _parse_number(price_match.group(1))
        if price_val and price_val > 0:
            price = price_val

    estimated_value = None
    if price and delta_shares:
        estimated_value = price * delta_shares

    # 10. Purpose
    purpose = "INVESTASI"
    purpose_match = re.search(
        r"(?:tujuan\s+transaksi|tujuan\s+kepemilikan)\s*[:=]?\s*([A-Za-z0-9\s\,\.\-]+?)(?:\n|\r|$)",
        combined,
        re.IGNORECASE
    )
    if purpose_match:
        purpose = purpose_match.group(1).strip()

    # 11. Market Structure (HSC & Free Float context)
    hsc_flag = any(re.search(pat, combined, re.IGNORECASE) for pat in HSC_PATTERNS)
    free_float_pct = None

    # Priority match for actual current free float: "porsi saham publik saat ini adalah 8.2%"
    actual_ff_match = re.search(
        r"(?:porsi\s+saham\s+publik|saham\s+publik\s+saat\s+ini|free\s+float\s+saat\s+ini|realisasi\s+free\s+float|porsi\s+masyarakat)\s*(?:adalah|sebesar|[:=])?\s*([0-9\.\,]+)\s*%",
        combined,
        re.IGNORECASE
    )
    if actual_ff_match:
        ff_val = _parse_number(actual_ff_match.group(1))
        if ff_val is not None:
            free_float_pct = ff_val
    else:
        ff_match = re.search(
            r"(?:free\s+float|saham\s+publik|kepemilikan\s+masyarakat)\s*[:=]?\s*([0-9\.\,]+)\s*%",
            combined,
            re.IGNORECASE
        )
        if ff_match:
            ff_val = _parse_number(ff_match.group(1))
            if ff_val is not None:
                free_float_pct = ff_val

    # Construct complete fact record
    fact = {
        "actor_name": actor_name,
        "direction": direction,
        "context_classification": context_classification,
        "shares_before": shares_before,
        "shares_after": shares_after,
        "delta_shares": delta_shares,
        "pct_before": pct_before,
        "pct_after": pct_after,
        "delta_pct": delta_pct,
        "price": price,
        "estimated_value": estimated_value,
        "purpose": purpose,
        "transaction_type": "PLEDGE" if pledge_flag else ("ADMINISTRATIVE" if is_admin else "OPEN_MARKET"),
        "transaction_date": transaction_date,
        "reporting_date": reporting_date,
        "publication_date": publication_date,
        "event_date": publication_date,
        "administrative_flag": is_admin,
        "related_party_flag": is_related_party,
        "pledge_flag": pledge_flag,
        "pledge_type": pledge_type,
        "raw_investor_class": raw_investor_class,
        "normalized_investor_class": normalized_class,
        "domicile": domicile,
        "beneficial_owner_name": beneficial_owner_name,
        "controller_name": controller_name,
        "hsc_flag": hsc_flag,
        "free_float_pct": free_float_pct,
        "confidence": "HIGH" if (delta_shares > 0 or delta_pct != 0 or price or pledge_flag) else "MEDIUM"
    }

    results.append(fact)
    return results
