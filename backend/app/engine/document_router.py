import re
from typing import Dict, Any, Tuple
from app.ingestion.idx_client import is_impossible_ca_announcement, IMPOSSIBLE_CA_EXCLUSION_PATTERNS


def is_impossible_corporate_action(title: str, category: str = "") -> bool:
    """
    Checks whether a document announcement cannot possibly contain a corporate action
    per PRD v5 Section 3 & 10 (such as ad proof receipts, daily FX, non-stock debt/funds).
    """
    return is_impossible_ca_announcement(title, category)


TIER_A_KEYWORDS = [
    r"laporan\s+kepemilikan\s+saham",
    r"perubahan\s+kepemilikan\s+saham",
    r"transaksi\s+saham\s+oleh\s+direksi",
    r"laporan\s+pengendali",
    r"kepemilikan\s+efek\s+(?:5%|1%|>1%)",
    r"daftar\s+pemegang\s+saham\s+(?:di\s+atas|>)\s*1%",
    r"daftar\s+pemegang\s+saham",
    r"pengambilalihan",
    r"akuisisi",
    r"divestasi",
    r"change\s+of\s+control",
    r"perubahan\s+pengendali",
    r"tender\s+offer",
    r"penawaran\s+tender",
    r"hmetd",
    r"hak\s+memesan\s+efek\s+terlebih\s+dahulu",
    r"pmthmetd",
    r"tanpa\s+hmetd",
    r"private\s+placement",
    r"investor\s+strategis",
    r"strategic\s+investor",
    r"gadai\s+saham",
    r"penjaminan\s+saham",
    r"pelepasan\s+gadai",
    r"release\s+pledge",
    r"pencabutan\s+jaminan",
    r"konsentrasi\s+kepemilikan",
    r"high\s+shareholding\s+concentration",
    r"\bhsc\b",
    r"free\s+float",
    r"volatilitas\s+transaksi",
    r"unusual\s+market\s+activity",
    r"\buma\b"
]

TIER_B_KEYWORDS = [
    r"rupslb",
    r"rapat\s+umum\s+pemegang\s+saham\s+luar\s+biasa",
    r"penambahan\s+modal",
    r"modal\s+dasar",
    r"fasilitas\s+kredit\s+sindikasi",
    r"perjanjian\s+pembiayaan",
    r"kemitraan\s+strategis",
    r"joint\s+venture",
    r"ekspansi\s+usaha",
    r"kontrak\s+material",
    r"perolehan\s+kontrak",
    r"struktur\s+permodalan"
]

TIER_C_ROUTINE_KEYWORDS = [
    r"laporan\s+keuangan",
    r"financial\s+statement",
    r"jadwal\s+dividen\s+rutin",
    r"public\s+expose\s+insidentil",
    r"paparan\s+publik",
    r"perubahan\s+sekretaris\s+perusahaan",
    r"jadwal\s+pembayaran\s+bunga\s+obligasi",
    r"surat\s+tanggapan\s+permintaan\s+penjelasan\s+bursa"
]

def classify_document_priority(
    title: str,
    category: str = "",
    scan_mode: str = "smart",
    route_code: str = ""
) -> Tuple[str, bool]:
    """
    Classifies a document announcement into Tier A, B, C, or D.
    Returns (tier, should_deep_extract).
    
    PRD v7.2 Section 3:
    - OWN-05, OWN-01, OWN-KP, and MKT-VOL routes are deep-process eligible
      when title/category is consistent with ownership data or public ownership datasets.
    - If scan_mode == 'full_audit', all supported non-routine documents are deep extracted.
    """
    combined = f"{title} {category}".lower()

    # Route-code awareness (PRD v7.2 Section 3)
    if route_code in ("OWN-05", "OWN-KP"):
        return "TIER_A", True
    elif route_code == "OWN-01":
        # Deep-process eligible when consistent with ownership data or dedicated public ownership
        if any(k in combined for k in ["kepemilikan", "pemegang saham", "ownership", "1%", "saham", "investor"]):
            return "TIER_A", True
    elif route_code == "MKT-VOL":
        return "TIER_A", True

    # Full audit mode escalates all eligible documents
    if scan_mode == "full_audit":
        if any(re.search(pat, combined) for pat in TIER_A_KEYWORDS):
            return "TIER_A", True
        if any(re.search(pat, combined) for pat in TIER_B_KEYWORDS):
            return "TIER_B", True
        return "TIER_C", True

    # Smart Scan mode:
    # 1. Check Tier A (Mandatory deep extract)
    if any(re.search(pat, combined) for pat in TIER_A_KEYWORDS):
        return "TIER_A", True

    # 2. Check Tier B (Triggered deep extract)
    if any(re.search(pat, combined) for pat in TIER_B_KEYWORDS):
        return "TIER_B", True

    # 3. Check Tier C (Lightweight metadata scan)
    if any(re.search(pat, combined) for pat in TIER_C_ROUTINE_KEYWORDS):
        return "TIER_C", False

    # Default to Tier C metadata-only unless triggered
    return "TIER_C", False
