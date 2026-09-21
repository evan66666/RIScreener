import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.rules.definitions import TRANSFORMATION_FAMILIES, TRANSFORMATION_LIFECYCLE_STAGES

# Strategic asset catalyst families (Section 5.4)
ASSET_CATALYSTS = {
    "MINING_MINERAL": [r"tambang\s+(?:emas|nikel|batu\s+bara|tembaga|bauksit)", r"konsesi\s+tambang", r"iup\s+operasi\s+produksi", r"smelter"],
    "ENERGY_PROJECT": [r"energi\s+terbarukan", r"plts", r"pltu", r"geotermal", r"panas\s+bumi", r"transisi\s+energi"],
    "DATA_CENTER_AI": [r"data\s+center", r"pusat\s+data", r"infrastruktur\s+cloud", r"kecerdasan\s+buatan", r"komputasi"],
    "LANDBANK_PROPERTY": [r"landbank", r"lahan\s+seluas\s+\d+", r"kota\s+mandiri", r"kawasan\s+industri", r"tanah\s+matang"],
    "INFRASTRUCTURE": [r"jalan\s+tol", r"pelabuhan", r"bandara", r"fasilitas\s+logistik", r"terminal\s+lng"]
}

def extract_transformation_signals(
    full_text: str,
    title: str = "",
    published_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Extracts corporate transformation events, asset/project catalysts, and lifecycle stage.
    """
    signals = []
    combined = f"{title}\n{full_text}"

    for trans_key, trans_def in TRANSFORMATION_FAMILIES.items():
        matched_trigger = None
        for pattern in trans_def.get("triggers", []):
            m = re.search(pattern, combined, re.IGNORECASE)
            if m:
                matched_trigger = m.group(0)
                break

        if matched_trigger:
            # Determine lifecycle stage
            stage = "AGREEMENT"
            for stage_item in TRANSFORMATION_LIFECYCLE_STAGES:
                if any(re.search(p, combined, re.IGNORECASE) for p in stage_item["patterns"]):
                    stage = stage_item["stage"]
                    break

            # Check asset catalysts
            identified_catalysts = []
            for cat_key, cat_patterns in ASSET_CATALYSTS.items():
                if any(re.search(p, combined, re.IGNORECASE) for p in cat_patterns):
                    identified_catalysts.append(cat_key)

            signals.append({
                "transformation_type": trans_key,
                "name": trans_def["name"],
                "trigger": matched_trigger,
                "stage": stage,
                "asset_catalysts": identified_catalysts,
                "event_date": published_date or datetime.utcnow(),
                "confidence": "HIGH" if identified_catalysts else "MEDIUM"
            })

    return signals
