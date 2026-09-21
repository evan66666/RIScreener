import sys, re
sys.path.insert(0, 'backend')
from app.rules.definitions import ACTION_FAMILIES

ri = ACTION_FAMILIES["RIGHT_ISSUE_HMETD"]
text = "KETERBUKAAN INFORMASI KEBUTUHAN PENDANAAN EKUITAS\n\nPerseroan menyampaikan adanya kebutuhan pendanaan ekspansi untuk mendukung pembiayaan perumahan nasional. Direksi mengkaji penyesuaian struktur permodalan dan penguatan rasio kecukupan modal (CAR)."

print("Testing BBTN doc1 text...")
print("\nEarly terms:")
for pat in ri["early_terms"]:
    m = re.search(pat, text, re.IGNORECASE)
    if m:
        print(f"  MATCH: {pat!r} -> '{m.group(0)}'")
    else:
        print(f"  no: {pat!r}")

print("\nExplicit terms:")
for pat in ri["explicit_terms"]:
    m = re.search(pat, text, re.IGNORECASE)
    if m:
        print(f"  MATCH: {pat!r} -> '{m.group(0)}'")

# Check lifecycle
print("\nLifecycle patterns:")
for lc in ri["lifecycle_stages"]:
    for pat in lc["patterns"]:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            print(f"  MATCH [{lc['stage']}]: {pat!r} -> '{m.group(0)}'")
