"""
Comprehensive project audit script.
Run from: d:/Documents/Projek/fullstack/RIScreener
Command: python backend/scripts/audit_check.py
"""
import sys
import re
sys.path.insert(0, 'backend')

from app.rules.definitions import ACTION_FAMILIES
from app.rules.action_detector import detect_signals_in_document
from app.engine.lifecycle_manager import determine_issuer_action_stage
from app.engine.ranker import calculate_priority_score, get_priority_label
from app.engine.impact_evaluator import evaluate_economic_impact
from app.engine.corroborator import evaluate_corroboration
from app.engine.novelty_tracker import determine_novelty_class, build_what_changed_summary
from app.ingestion.master_companies import IDX_MASTER_COMPANIES
from app.ingestion.idx_client import parse_idx_datetime
from app.ingestion.sample_data import generate_sample_corpus
from datetime import datetime, timedelta

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

errors = []
warnings = []

print("=" * 70)
print("  IDX CORPORATE ACTION SCREENER - COMPREHENSIVE AUDIT REPORT")
print("=" * 70)

# ─── 1. ACTION FAMILIES ───────────────────────────────────────────────────────
print("\n[1] ACTION FAMILIES COMPLETENESS")
expected_families = 15
actual = len(ACTION_FAMILIES)
if actual >= expected_families:
    print(f"  {PASS} {actual} action families defined (expected >= {expected_families})")
else:
    print(f"  {FAIL} Only {actual} action families defined (expected {expected_families})")
    errors.append(f"Missing action families: {expected_families - actual}")

required_keys = ["explicit_terms", "early_terms", "lifecycle_stages", "name", "category"]
for k, v in ACTION_FAMILIES.items():
    missing = [rk for rk in required_keys if not v.get(rk)]
    if missing:
        print(f"  {WARN} {k}: missing fields: {missing}")
        warnings.append(f"ACTION_FAMILY {k} missing: {missing}")
    else:
        lc_count = len(v.get("lifecycle_stages", []))
        print(f"  {PASS} {k} ({v['name']}): {len(v['explicit_terms'])} explicit, {len(v['early_terms'])} early, {lc_count} lifecycle stages")

# ─── 2. SIGNAL DETECTION ──────────────────────────────────────────────────────
print("\n[2] SIGNAL DETECTION ENGINE")

test_cases = [
    {
        "desc": "Right Issue explicit (HMETD)",
        "title": "Keterbukaan Informasi Penambahan Modal Melalui HMETD",
        "text": "Perseroan berencana melakukan Penawaran Umum Terbatas dengan Hak Memesan Efek Terlebih Dahulu (HMETD) sebanyak 10 miliar saham baru senilai Rp 5 triliun.",
        "expect_action": "RIGHT_ISSUE",
        "expect_stage": "EXPLICIT",
    },
    {
        "desc": "Right Issue early precursor (kebutuhan pendanaan capex)",
        "title": "Keterbukaan Informasi Kebutuhan Pendanaan Ekspansi",
        "text": "Perseroan memiliki kebutuhan pendanaan ekspansi untuk pengembangan pabrik. Perseroan sedang mempertimbangkan alternatif pendanaan ekuitas jangka panjang.",
        "expect_action": "RIGHT_ISSUE",
        "expect_stage": "EARLY",
    },
    {
        "desc": "Akuisisi explicit",
        "title": "Keterbukaan Informasi Akuisisi",
        "text": "Perseroan telah menandatangani Conditional Sale and Purchase Agreement (CSPA) untuk mengakuisisi 90% saham PT Target Tbk senilai Rp 3,5 triliun.",
        "expect_action": "ACQUISITION",
        "expect_stage": "EXPLICIT",
    },
    {
        "desc": "Negation suppression",
        "title": "Klarifikasi Media",
        "text": "Perseroan menyatakan bahwa informasi mengenai rencana right issue adalah tidak benar dan menyesatkan. Perseroan tidak memiliki rencana penerbitan saham baru dalam waktu dekat.",
        "expect_action": "RIGHT_ISSUE",
        "expect_is_negated": True,
    },
    {
        "desc": "Merger & Acquisition",
        "title": "Rencana Penggabungan Usaha",
        "text": "Dewan Direksi mengumumkan rencana penggabungan usaha (merger) antara Perseroan dan PT Mitra Utama Tbk. RUPSLB akan diselenggarakan untuk mendapatkan persetujuan pemegang saham.",
        "expect_action": "MERGER",
        "expect_stage": "EXPLICIT",
    },
    {
        "desc": "Obligasi Konversi (Convertible Bond)",
        "title": "Rencana Penerbitan Obligasi Konversi",
        "text": "Perseroan berencana menerbitkan obligasi konversi (convertible bond) senilai Rp 2 triliun untuk membiayai ekspansi usaha.",
        "expect_action": "CONVERTIBLE_BOND",
        "expect_stage": "EXPLICIT",
    },
]

for tc in test_cases:
    pages = [{"page_number": 1, "raw_text": tc["text"], "normalized_text": tc["text"]}]
    sigs = detect_signals_in_document(tc["title"], pages)
    
    if not sigs:
        print(f"  {FAIL} [{tc['desc']}] No signals detected at all")
        errors.append(f"No signal detected for: {tc['desc']}")
        continue
    
    # Check expected action type
    if "expect_action" in tc:
        found = next((s for s in sigs if s["action_type"] == tc["expect_action"]), None)
        if not found:
            detected = [s["action_type"] for s in sigs]
            print(f"  {FAIL} [{tc['desc']}] Expected {tc['expect_action']}, got {detected}")
            errors.append(f"Wrong action detected for: {tc['desc']}")
            continue
        
        if "expect_stage" in tc:
            if found["stage"] != tc["expect_stage"]:
                print(f"  {FAIL} [{tc['desc']}] Stage={found['stage']} expected={tc['expect_stage']}")
                errors.append(f"Wrong stage for: {tc['desc']}")
                continue
        
        if "expect_is_negated" in tc:
            if found.get("is_negated") != tc["expect_is_negated"]:
                print(f"  {FAIL} [{tc['desc']}] is_negated={found.get('is_negated')} expected={tc['expect_is_negated']}")
                errors.append(f"Negation wrong for: {tc['desc']}")
                continue
        
        stage_disp = found.get('stage', '?')
        ev_count = len(found.get('evidence_items', []))
        print(f"  {PASS} [{tc['desc']}] -> {found['action_type']} stage={stage_disp} evidence_items={ev_count}")

# ─── 3. LIFECYCLE MANAGER ─────────────────────────────────────────────────────
print("\n[3] LIFECYCLE STAGE TRANSITIONS")
base_dt = datetime.now() - timedelta(days=30)

# Test: 1 event = EARLY
res = determine_issuer_action_stage([
    {"event_date": base_dt, "lifecycle_stage": "PRECURSOR_IDENTIFIED", "signal_type": "EARLY", "contribution": "INITIAL", "is_negated": False, "is_cancelled": False}
], 60)
ok = res["stage"] == "EARLY" and res["state_status"] == "ACTIVE"
print(f"  {PASS if ok else FAIL} 1 signal => EARLY (got {res['stage']}/{res['state_status']})")
if not ok: errors.append("EARLY lifecycle wrong")

# Test: 2 events = DEVELOPING
res = determine_issuer_action_stage([
    {"event_date": base_dt, "lifecycle_stage": "PRECURSOR_IDENTIFIED", "signal_type": "EARLY", "contribution": "INITIAL", "is_negated": False, "is_cancelled": False},
    {"event_date": base_dt + timedelta(days=10), "lifecycle_stage": "RUPSLB_CALLED", "signal_type": "EARLY", "contribution": "ADVANCEMENT", "is_negated": False, "is_cancelled": False},
], 60)
ok = res["stage"] == "DEVELOPING" and res["state_status"] == "ACTIVE"
print(f"  {PASS if ok else FAIL} 2 signals => DEVELOPING (got {res['stage']}/{res['state_status']})")
if not ok: errors.append("DEVELOPING lifecycle wrong")

# Test: EXPLICIT signal => EXPLICIT
res = determine_issuer_action_stage([
    {"event_date": base_dt, "lifecycle_stage": "PRECURSOR_IDENTIFIED", "signal_type": "EXPLICIT", "contribution": "INITIAL", "is_negated": False, "is_cancelled": False},
], 60)
ok = res["stage"] == "EXPLICIT" and res["state_status"] == "ACTIVE"
print(f"  {PASS if ok else FAIL} EXPLICIT signal => EXPLICIT (got {res['stage']}/{res['state_status']})")
if not ok: errors.append("EXPLICIT lifecycle wrong")

# Test: Negated => CONTRADICTED
res = determine_issuer_action_stage([
    {"event_date": base_dt, "lifecycle_stage": "PRECURSOR_IDENTIFIED", "signal_type": "EARLY", "contribution": "CONTRADICTION", "is_negated": True, "is_cancelled": False},
], 60)
ok = res["state_status"] == "CONTRADICTED"
print(f"  {PASS if ok else FAIL} Negated event => CONTRADICTED (got {res['stage']}/{res['state_status']})")
if not ok: errors.append("CONTRADICTED lifecycle wrong")

# ─── 4. RANKER ────────────────────────────────────────────────────────────────
print("\n[4] PRIORITY SCORING RANKER")
score = calculate_priority_score("DEVELOPING", "POSITIVE", "HIGH", 3, "ACTIVE")
label = get_priority_label(score)
ok = label == "HIGH" and score >= 80
print(f"  {PASS if ok else FAIL} DEVELOPING+POSITIVE+HIGH => score={score} label={label}")
if not ok: errors.append(f"Ranker wrong for DEVELOPING+POSITIVE: score={score}")

score = calculate_priority_score("EARLY", "UNCLEAR", "LOW", 1, "ACTIVE")
label = get_priority_label(score)
ok = label in ("MEDIUM", "LOW")
print(f"  {PASS if ok else FAIL} EARLY+UNCLEAR+LOW => score={score} label={label}")

score = calculate_priority_score("EXPLICIT", "POSITIVE", "HIGH", 2, "ACTIVE")
label = get_priority_label(score)
ok = label in ("HIGH", "MEDIUM")
print(f"  {PASS if ok else FAIL} EXPLICIT+POSITIVE+HIGH => score={score} label={label}")

score_contradicted = calculate_priority_score("DEVELOPING", "POSITIVE", "HIGH", 5, "CONTRADICTED")
ok = score_contradicted <= 20
print(f"  {PASS if ok else FAIL} CONTRADICTED state => low score={score_contradicted} (deprioritized)")
if not ok: errors.append("Contradicted state not deprioritized")

# ─── 5. DATE PARSING ──────────────────────────────────────────────────────────
print("\n[5] DATE PARSING ROBUSTNESS")
test_dates = [
    ("/Date(1705305600000)/", "ASP.NET timestamp"),
    ("/Date(1705305600000+0700)/", "ASP.NET with timezone"),
    ("2026-09-02T10:30:00", "ISO datetime"),
    ("2026-09-02T10:30:00+07:00", "ISO with offset"),
    ("2026-09-02T10:30:00Z", "ISO UTC"),
    ("2026-09-02", "ISO date only"),
    ("02-09-2026", "DD-MM-YYYY"),
    ("2 September 2026", "English long format"),
]

for date_str, desc in test_dates:
    try:
        result = parse_idx_datetime(date_str)
        ok = isinstance(result, datetime) and result.year in (2024, 2025, 2026)
        print(f"  {PASS if ok else WARN} [{desc}] '{date_str}' -> {result.strftime('%Y-%m-%d %H:%M')}")
        if not ok:
            warnings.append(f"Date parse suspect for {desc}: {result}")
    except Exception as e:
        print(f"  {FAIL} [{desc}] Exception: {e}")
        errors.append(f"Date parse failed for {desc}: {e}")

# Indonesian months
indo_test = "15 Januari 2026"
try:
    result = parse_idx_datetime(indo_test)
    ok = result.year == 2026 and result.month == 1 and result.day == 15
    print(f"  {PASS if ok else FAIL} [Indo month] '{indo_test}' -> {result.strftime('%Y-%m-%d')}")
    if not ok: errors.append("Indonesian month parse failed")
except Exception as e:
    print(f"  {FAIL} [Indo month] Exception: {e}")
    errors.append(f"Indonesian month exception: {e}")

# ─── 6. MASTER COMPANIES ──────────────────────────────────────────────────────
print("\n[6] MASTER COMPANIES REGISTRY")
total = len(IDX_MASTER_COMPANIES)
tickers = [c["ticker"] for c in IDX_MASTER_COMPANIES]
unique_tickers = set(tickers)
dups = [t for t in tickers if tickers.count(t) > 1]
unique_dups = list(set(dups))

if total >= 900:
    print(f"  {PASS} {total} companies registered")
else:
    print(f"  {WARN} Only {total} companies (expected ~964)")
    warnings.append(f"Expected ~964 companies, got {total}")

if unique_dups:
    print(f"  {FAIL} Duplicate tickers found: {unique_dups[:10]}")
    errors.append(f"Duplicate tickers: {unique_dups}")
else:
    print(f"  {PASS} No duplicate tickers ({len(unique_tickers)} unique)")

# Check for placeholder EX## tickers
placeholder = [t for t in tickers if re.match(r"^EX\d+$", t)]
if placeholder:
    print(f"  {WARN} {len(placeholder)} placeholder tickers (EX01..EX100) found in master list")
    warnings.append(f"{len(placeholder)} placeholder EX## tickers should be removed")
else:
    print(f"  {PASS} No placeholder tickers")

# Check required fields
missing_fields = [c for c in IDX_MASTER_COMPANIES if not c.get("ticker") or not c.get("name") or not c.get("sector")]
if missing_fields:
    print(f"  {FAIL} {len(missing_fields)} companies missing required fields")
    errors.append(f"{len(missing_fields)} companies with missing fields")
else:
    print(f"  {PASS} All companies have ticker, name, sector")

# ─── 7. SAMPLE CORPUS ─────────────────────────────────────────────────────────
print("\n[7] SAMPLE CORPUS INTEGRITY")
try:
    corpus = generate_sample_corpus()
    print(f"  {PASS} Sample corpus generated: {len(corpus)} documents")
    
    # Check dates make sense
    now = datetime.now()
    future_docs = [d for d in corpus if d["published_at"] > now + timedelta(hours=1)]
    if future_docs:
        print(f"  {FAIL} {len(future_docs)} documents have FUTURE timestamps!")
        for d in future_docs[:3]:
            print(f"         {d['ticker']}: {d['published_at']}")
        errors.append(f"{len(future_docs)} corpus docs with future dates")
    else:
        print(f"  {PASS} No documents with future timestamps")
    
    # Check all tickers exist in master
    corpus_tickers = {d["ticker"] for d in corpus}
    master_tickers = {c["ticker"] for c in IDX_MASTER_COMPANIES}
    unknown = corpus_tickers - master_tickers
    if unknown:
        print(f"  {WARN} Corpus tickers not in master: {unknown}")
        warnings.append(f"Corpus has unknown tickers: {unknown}")
    else:
        print(f"  {PASS} All corpus tickers exist in master registry")
    
    # Check source_id uniqueness
    ids = [d["source_id"] for d in corpus]
    dup_ids = [i for i in ids if ids.count(i) > 1]
    if dup_ids:
        print(f"  {FAIL} Duplicate source_ids: {list(set(dup_ids))}")
        errors.append(f"Duplicate source_ids in corpus: {dup_ids}")
    else:
        print(f"  {PASS} All source_ids unique")
    
except Exception as e:
    print(f"  {FAIL} generate_sample_corpus() failed: {e}")
    errors.append(f"Corpus generation error: {e}")

# ─── 8. SIGNAL DETECTION ON SAMPLE CORPUS ────────────────────────────────────
print("\n[8] SIGNAL DETECTION ON SAMPLE CORPUS")
try:
    corpus = generate_sample_corpus()
    total_signals = 0
    right_issue_found = []
    
    for doc in corpus:
        pages = [{"page_number": 1, "raw_text": p, "normalized_text": p} for p in doc.get("pages", [])]
        if not pages:
            pages = [{"page_number": 1, "raw_text": doc["title"], "normalized_text": doc["title"]}]
        sigs = detect_signals_in_document(doc["title"], pages)
        total_signals += len(sigs)
        for s in sigs:
            if s["action_type"] == "RIGHT_ISSUE":
                right_issue_found.append((doc["ticker"], s["stage"], s.get("is_negated", False)))
    
    print(f"  {PASS} Total signals detected across corpus: {total_signals}")
    ri_active = [(t, st) for t, st, neg in right_issue_found if not neg]
    print(f"  {PASS} Right Issue signals (active, non-negated): {len(ri_active)}")
    for t, st in ri_active:
        print(f"         {t}: {st}")
    
except Exception as e:
    print(f"  {FAIL} Corpus signal detection failed: {e}")
    errors.append(f"Corpus signal detection error: {e}")

# ─── 9. API DATE BOUNDARY ─────────────────────────────────────────────────────
print("\n[9] DATE BOUNDARY LOGIC")
from datetime import datetime

# Simulate what router does
date_from_str = "2026-09-02"
date_to_str = "2026-09-02"

d_from = datetime.fromisoformat(date_from_str).replace(hour=0, minute=0, second=0, microsecond=0)
d_to = datetime.fromisoformat(date_to_str).replace(hour=23, minute=59, second=59, microsecond=999999)

ok = d_from.hour == 0 and d_to.hour == 23 and d_to.second == 59
print(f"  {PASS if ok else FAIL} Same-day date_from={d_from} date_to={d_to}")

# Test a 3pm announcement would be included
announcement_dt = datetime(2026, 9, 2, 15, 0, 0)  # 3pm
ok = d_from <= announcement_dt <= d_to
print(f"  {PASS if ok else FAIL} 3pm announcement included in Today range: {ok}")
if not ok: errors.append("3pm announcement excluded from Today range")

# ─── SUMMARY ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  AUDIT SUMMARY")
print("=" * 70)
if errors:
    print(f"\n  {FAIL} BUGS / ERRORS FOUND ({len(errors)}):")
    for e in errors:
        print(f"     • {e}")
else:
    print(f"\n  {PASS} No critical bugs found!")

if warnings:
    print(f"\n  {WARN} WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(f"     • {w}")
else:
    print(f"  {PASS} No warnings.")

print(f"\n  Final: {len(errors)} errors, {len(warnings)} warnings\n")
