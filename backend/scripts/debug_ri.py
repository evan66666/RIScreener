"""
Verify Right Issue detection on actual sample corpus pages.
"""
import sys
sys.path.insert(0, 'backend')

from app.rules.action_detector import detect_signals_in_document
from app.ingestion.sample_data import generate_sample_corpus

corpus = generate_sample_corpus()

print(f"Corpus has {len(corpus)} docs")
for doc in corpus:
    pages_raw = doc.get("pages", [])
    # pages in corpus are strings, not dicts - build proper page dicts
    page_dicts = [{"page_number": i+1, "raw_text": p, "normalized_text": p} for i, p in enumerate(pages_raw)]
    sigs = detect_signals_in_document(doc["title"], page_dicts)
    ri_sigs = [s for s in sigs if s["action_type"] == "RIGHT_ISSUE_HMETD"]
    if ri_sigs:
        for s in ri_sigs:
            print(f"  {doc['ticker']} [{s['stage']}] negated={s.get('is_negated')} evid={len(s.get('evidence_items', []))}")
    elif doc.get("ticker") in ["BRMS", "BBTN", "PANI", "BBYB", "WIKA"]:
        # Expected RI issuers
        all_found = [s["action_type"] for s in sigs]
        print(f"  {doc['ticker']} NO RI detected, got: {all_found}, title='{doc['title'][:60]}'")
        if page_dicts:
            print(f"    page1 text: {page_dicts[0]['raw_text'][:120]}")
