from app.rules.definitions import ACTION_FAMILIES, TRANSFORMATION_FAMILIES
from app.rules.action_detector import detect_signals_in_document
from app.rules.importance_engine import evaluate_information_importance

def test_all_action_and_transformation_families_exist():
    expected_families = [
        "RIGHT_ISSUE_HMETD",
        "PRIVATE_PLACEMENT",
        "ACQUISITION",
        "DIVESTMENT",
        "MERGER",
        "SPIN_OFF",
        "SHARE_BUYBACK",
        "SPECIAL_DIVIDEND",
        "STOCK_SPLIT",
        "WARRANT",
        "CONVERTIBLE_SECURITIES",
        "MAJOR_EXPANSION",
        "MAJOR_CONTRACT",
        "STRATEGIC_INVESTOR",
        "CHANGE_OF_CONTROL",
        "TENDER_OFFER",
        "MATERIAL_CAPITAL_RESTRUCTURING",
        "OTHER_STRATEGIC_TRANSACTION"
    ]
    assert len(ACTION_FAMILIES) == 18
    for fam in expected_families:
        assert fam in ACTION_FAMILIES
        assert "explicit_terms" in ACTION_FAMILIES[fam]
        assert "early_terms" in ACTION_FAMILIES[fam]
        assert "lifecycle_stages" in ACTION_FAMILIES[fam]
        assert "positive_contexts" in ACTION_FAMILIES[fam]
        assert "negative_contexts" in ACTION_FAMILIES[fam]
        assert "negations" in ACTION_FAMILIES[fam]
    
    assert len(TRANSFORMATION_FAMILIES) == 14

def test_right_issue_precursor_detection():
    title = "Keterbukaan Informasi Rencana Penambahan Modal dan Kebutuhan Pendanaan Ekspansi"
    pages = [{"page_number": 1, "normalized_text": "Perseroan memiliki kebutuhan pendanaan ekspansi dan mengusulkan penambahan modal dasar melalui penerbitan saham baru dengan pembeli siaga.", "raw_text": "Perseroan memiliki kebutuhan pendanaan ekspansi dan mengusulkan penambahan modal dasar melalui penerbitan saham baru dengan pembeli siaga."}]
    signals = detect_signals_in_document(title, pages)
    
    hmetd_sig = next((s for s in signals if s["action_type"] == "RIGHT_ISSUE_HMETD"), None)
    assert hmetd_sig is not None
    assert hmetd_sig["stage"] in ("EARLY", "DEVELOPING")
    assert not hmetd_sig["is_negated"]
    assert len(hmetd_sig["evidence_items"]) > 0

def test_acquisition_explicit_detection():
    title = "Keterbukaan Informasi Pengambilalihan Saham Mayoritas"
    pages = [{"page_number": 1, "normalized_text": "Perseroan telah menyelesaikan penandatanganan CSPA pengambilalihan saham sebesar 70% pada PT Target Energi untuk meningkatkan pangsa pasar.", "raw_text": "Perseroan telah menyelesaikan penandatanganan CSPA pengambilalihan saham sebesar 70% pada PT Target Energi untuk meningkatkan pangsa pasar."}]
    signals = detect_signals_in_document(title, pages)
    
    acq_sig = next((s for s in signals if s["action_type"] == "ACQUISITION"), None)
    assert acq_sig is not None
    assert acq_sig["stage"] == "EXPLICIT"
    assert acq_sig["impact"] == "POSITIVE"

def test_negation_suppression():
    title = "Penjelasan Atas Isu Akuisisi"
    pages = [{"page_number": 1, "normalized_text": "Manajemen membantah kabar dan menegaskan bahwa perseroan tidak memiliki rencana untuk melakukan pengambilalihan saham entitas lain.", "raw_text": "Manajemen membantah kabar dan menegaskan bahwa perseroan tidak memiliki rencana untuk melakukan pengambilalihan saham entitas lain."}]
    signals = detect_signals_in_document(title, pages)
    
    acq_sig = next((s for s in signals if s["action_type"] == "ACQUISITION"), None)
    assert acq_sig is not None
    assert acq_sig["is_negated"] is True

def test_cancellation_detection():
    title = "Pembatalan Rencana Pembelian Kembali Saham"
    pages = [{"page_number": 1, "normalized_text": "Direksi memutuskan membatalkan rencana pelaksanaan pembelian kembali saham (share buyback) karena kondisi pasar global.", "raw_text": "Direksi memutuskan membatalkan rencana pelaksanaan pembelian kembali saham (share buyback) karena kondisi pasar global."}]
    signals = detect_signals_in_document(title, pages)
    
    bb_sig = next((s for s in signals if s["action_type"] == "SHARE_BUYBACK"), None)
    assert bb_sig is not None
    assert bb_sig["is_cancelled"] is True
    assert bb_sig["impact"] == "NEGATIVE"

def test_distress_impact_classification():
    title = "Keterbukaan Informasi Restrukturisasi Utang PKPU"
    pages = [{"page_number": 1, "normalized_text": "Perseroan mengalami masalah likuiditas mendesak dan menghadapi potensi gagal bayar dalam proses penundaan kewajiban pembayaran utang (PKPU).", "raw_text": "Perseroan mengalami masalah likuiditas mendesak dan menghadapi potensi gagal bayar dalam proses penundaan kewajiban pembayaran utang (PKPU)."}]
    signals = detect_signals_in_document(title, pages)
    imp = evaluate_information_importance(title, pages[0]["normalized_text"], signals)
    
    assert imp["importance"] == "HIGH"
