import re
from typing import Dict, Any, List

# Routineness indicators
ROUTINE_PATTERNS = [
    r"laporan\s+bulanan\s+registrasi\s+pemegang\s+efek",
    r"laporan\s+penggunaan\s+dana\s+hasil\s+penawaran\s+umum",
    r"jadwal\s+pelaksanaan\s+public\s+expose\s+tahunan",
    r"penyampaian\s+laporan\s+keuangan\s+tahunan\s+rutin",
    r"perubahan\s+alamat\s+surat\s+menyurat",
    r"perubahan\s+corporate\s+secretary\s+rutin",
    r"koreksi\s+salah\s+ketik"
]

HIGH_IMPORTANCE_PATTERNS = [
    r"akuisisi|pengambilalihan",
    r"hmetd|rights?\s+issue|penambahan\s+modal",
    r"perubahan\s+pengendali",
    r"divestasi",
    r"merger|penggabungan\s+usaha",
    r"buyback\s+saham|pembelian\s+kembali\s+saham",
    r"dividen\s+(?:spesial|khusus|luar\s+biasa)",
    r"kontrak\s+material",
    r"investor\s+strategis",
    r"gagal\s+bayar|pkpu|pailit",
    r"pembangunan\s+pabrik\s+baru|ekspansi\s+besar"
]

def evaluate_information_importance(
    title: str,
    extracted_text: str,
    detected_action_signals: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Evaluates disclosure content and assigns an Information Importance class:
    - HIGH
    - MEDIUM
    - LOW
    - NO_MATERIAL_SIGNAL
    """
    combined_text = f"{title} {extracted_text}".lower()

    # 1. If corporate action signals detected
    if detected_action_signals:
        explicit_or_dev = any(
            s.get("stage") in ("EXPLICIT", "DEVELOPING") or s.get("strength") == "HIGH"
            for s in detected_action_signals
        )
        if explicit_or_dev:
            return {
                "importance": "HIGH",
                "reason": "Material corporate action or developing precursor identified."
            }
        else:
            return {
                "importance": "MEDIUM",
                "reason": "Early stage indicator or indirect corporate action clue detected."
            }

    # 2. Check for high-importance keywords even if no formal corporate action parsed
    for pat in HIGH_IMPORTANCE_PATTERNS:
        if re.search(pat, combined_text):
            return {
                "importance": "HIGH",
                "reason": "High-materiality corporate or financial disclosure terms detected."
            }

    # 3. Check for routine disclosures
    for pat in ROUTINE_PATTERNS:
        if re.search(pat, combined_text):
            return {
                "importance": "LOW",
                "reason": "Standard periodic compliance or routine administrative filing."
            }

    # 4. If text contains general corporate updates
    if len(extracted_text.strip()) > 100:
        return {
            "importance": "LOW",
            "reason": "General disclosure without high-materiality triggers."
        }

    return {
        "importance": "NO_MATERIAL_SIGNAL",
        "reason": "No material event or precursor signal identified."
    }
