"""
Unit tests for IDX Smart Money, Ownership & Corporate Transformation Intelligence PRD v7.3 Patch:
Corporate Action Quality, Strategic Attractiveness & Shareholder Value Assessment
Covers Section 36 Minimum Test Corpus (17 test cases).
"""

import pytest
from app.engine.ca_quality_engine import CorporateActionQualityEngine


@pytest.fixture
def quality_engine():
    return CorporateActionQualityEngine()


def test_case_01_productive_right_issue(quality_engine):
    """Case 1: Productive Right Issue with clear expansion allocation -> ATTRACTIVE"""
    text = (
        "PT Nusantara Tbk merencanakan Penambahan Modal dengan Hak Memesan Efek Terlebih Dahulu (HMETD). "
        "Sekitar 75% dana hasil penawaran akan digunakan untuk belanja modal dan pembangunan pabrik baru, "
        "sisanya untuk modal kerja operasional. Persentase dilusi sebesar 12%. "
        "Harga pelaksanaan sebesar Rp 450 per saham."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    assert result["quality_label"] in ["VERY_ATTRACTIVE", "ATTRACTIVE"]
    assert result["quality_score"] >= 65.0
    assert result["shareholder_value_score"] >= 60.0
    assert "CLEAR_USE_OF_PROCEEDS" in result["positive_drivers"]
    assert "PRODUCTIVE_ASSET" in result["positive_drivers"]
    assert result["opportunity_state"] in ["DEVELOPING_ATTRACTIVE", "EARLY_ATTRACTIVE"]


def test_case_02_strategic_investor_participation(quality_engine):
    """Case 2: Strategic investor participation commitment -> ATTRACTIVE"""
    text = (
        "Dalam rangka Penambahan Modal Tanpa HMETD (Private Placement), perseroan menggandeng "
        "investor strategis global sebagai pemodal strategis. "
        "Dana dialokasikan sebesar 80% untuk ekspansi jaringan logistik nasional. "
        "Persentase dilusi sebesar 8.5%."
    )
    result = quality_engine.evaluate_quality(text, action_type="PRIVATE_PLACEMENT", lifecycle_stage="DEVELOPING")
    
    assert result["quality_label"] in ["VERY_ATTRACTIVE", "ATTRACTIVE"]
    assert "STRATEGIC_INVESTOR" in result["positive_drivers"]
    assert result["recipients"]["has_strategic_investor"] is True
    assert result["dilution_pct"] == 8.5


def test_case_03_operating_asset_acquisition(quality_engine):
    """Case 3: Asset acquisition with commercial contracts -> ATTRACTIVE"""
    text = (
        "Dana hasil Right Issue akan digunakan untuk akuisisi entitas anak yang memiliki "
        "aset produktif pembangkit listrik yang sudah beroperasi secara komersial "
        "dengan kontrak penjualan jangka panjang (power purchase agreement / ppa). "
        "Menghasilkan arus kas positif stabil. Dilusi tercatat 14%."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    assert result["quality_label"] in ["VERY_ATTRACTIVE", "ATTRACTIVE"]
    assert "CONTRACTED_REVENUE" in result["positive_drivers"]
    assert "PRODUCTIVE_ASSET" in result["positive_drivers"]
    assert result["scores_decomposition"]["asset_quality_score"] >= 80.0


def test_case_04_productive_expansion_funding(quality_engine):
    """Case 4: Expansion capex funding with confirmed standby buyer -> ATTRACTIVE"""
    text = (
        "Perseroan akan melakukan PUT I HMETD untuk pembelian peralatan dan mesin baru. "
        "PT Danareksa Sekuritas bertindak sebagai pembeli siaga yang menjamin penyerapan saham sisa. "
        "Dilusi terukur 10%."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    assert result["quality_label"] in ["VERY_ATTRACTIVE", "ATTRACTIVE"]
    assert "SECURED_FINANCING" in result["positive_drivers"]
    assert result["recipients"]["has_standby_buyer"] is True


def test_case_05_deleveraging_strategic_benefit(quality_engine):
    """Case 5: Deleveraging with interest reduction -> ATTRACTIVE / POSITIVE"""
    text = (
        "Penerbitan saham baru HMETD dengan alokasi 85% untuk pelunasan pinjaman bank sindikasi guna "
        "deleveraging dan penurunan beban bunga keuangan secara substansial. "
        "Rasio HMETD 100:15 dengan persentase dilusi 13%."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    assert result["quality_label"] in ["VERY_ATTRACTIVE", "ATTRACTIVE", "NEUTRAL_MIXED"]
    assert "DELEVERAGING_BENEFIT" in result["positive_drivers"]
    assert result["scores_decomposition"]["capital_efficiency_score"] >= 65.0


def test_case_06_emergency_liquidity_distress_right_issue(quality_engine):
    """Case 6: Emergency liquidity / distress financing -> RISKY / DISTRESS"""
    text = (
        "Perseroan menghadapi kondisi keuangan kritis dan tekanan arus kas berat. "
        "Right Issue dilakukan karena kebutuhan likuiditas mendesak dan restrukturisasi utang mendesak "
        "guna mempertahankan kelangsungan usaha yang terancam. Dilusi mencapai 45%."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="EXPLICIT")
    
    assert result["quality_label"] in ["RISKY_DILUTIVE", "UNATTRACTIVE_DISTRESS"]
    assert result["opportunity_state"] == "DISTRESS_RISK"
    assert "DISTRESS_FINANCING" in result["red_flags"]
    assert result["scores_decomposition"]["distress_risk_score"] <= 30.0


def test_case_07_high_dilution_issuance(quality_engine):
    """Case 7: High dilution (> 40%) issuance -> HIGH_DILUTION red flag"""
    text = (
        "Perseroan akan menerbitkan saham baru dalam jumlah besar dengan rasio 1:5. "
        "Persentase dilusi sebesar 48% bagi pemegang saham yang tidak melaksanakan hak. "
        "Dana digunakan untuk modal kerja perseroan."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    assert "HIGH_DILUTION" in result["red_flags"]
    assert result["dilution_pct"] == 48.0
    assert result["scores_decomposition"]["dilution_score"] <= 35.0


def test_case_08_related_party_issuance(quality_engine):
    """Case 8: Related-party settlement without clear minority benefit -> RELATED_PARTY_RISK"""
    text = (
        "Dana hasil Right Issue sekitar 70% akan digunakan untuk penyelesaian utang kepada pihak berelasi "
        "dan transaksi dengan pihak berafiliasi perseroan."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    assert "RELATED_PARTY_RISK" in result["red_flags"]
    assert result["scores_decomposition"]["related_party_risk_score"] <= 40.0


def test_case_09_uncertain_financing_and_execution_conditions(quality_engine):
    """Case 9: Uncertain financing and conditions precedent -> EXECUTION_UNCERTAINTY"""
    text = (
        "Rencana aksi korporasi masih dalam tahap uji tuntas (due diligence) dan tunduk pada persetujuan RUPS, "
        "persetujuan OJK masih dalam proses, dan belum adanya perjanjian definitif dengan pemodal."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="EARLY")
    
    assert "EXECUTION_UNCERTAINTY" in result["red_flags"]
    assert result["scores_decomposition"]["execution_risk_score"] <= 40.0


def test_case_10_forced_asset_disposal(quality_engine):
    """Case 10: Forced asset disposal due to distress -> DISTRESS_RISK"""
    text = (
        "Perseroan melakukan penjualan aset secara terpaksa guna menutup kewajiban jatuh tempo "
        "di tengah kondisi keuangan kritis dan proses penundaan kewajiban pembayaran utang (pkpu)."
    )
    result = quality_engine.evaluate_quality(text, action_type="ASSET_DISPOSAL", lifecycle_stage="EXPLICIT")
    
    assert result["opportunity_state"] == "DISTRESS_RISK"
    assert "DISTRESS_FINANCING" in result["red_flags"]


def test_case_11_strategic_acquisition_with_major_dilution(quality_engine):
    """Case 11: Mixed - productive acquisition but high dilution -> NEUTRAL_MIXED / MIXED"""
    text = (
        "Perseroan melakukan akuisisi aset operasional tambang produktif yang sudah beroperasi komersial. "
        "Namun aksi korporasi ini menyebabkan persentase dilusi sebesar 38% bagi pemegang saham publik."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    # Has both productive driver and dilution red flag
    assert "PRODUCTIVE_ASSET" in result["positive_drivers"]
    assert "HIGH_DILUTION" in result["red_flags"]
    assert result["quality_label"] in ["NEUTRAL_MIXED", "ATTRACTIVE", "RISKY_DILUTIVE"]


def test_case_12_attractive_asset_weak_financing(quality_engine):
    """Case 12: Mixed - attractive asset but funding dependency -> red flag FUNDING_DEPENDENCY"""
    text = (
        "Alokasi dana untuk pembelian unit bisnis produktif. "
        "Namun belum ada pembeli siaga atau investor strategis yang berkomitmen menyerap sisa saham."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="DEVELOPING")
    
    assert "FUNDING_DEPENDENCY" in result["red_flags"]
    assert result["recipients"]["has_standby_buyer"] is False


def test_case_13_strong_investor_high_execution_risk(quality_engine):
    """Case 13: Mixed - strong investor commitment but heavy execution conditions"""
    text = (
        "Investor strategis global telah menandatangani komitmen awal penyertaan modal. "
        "Namun transaksi tunduk pada persetujuan RUPS dan pemenuhan seluruh syarat tangguh (conditions precedent)."
    )
    result = quality_engine.evaluate_quality(text, action_type="PRIVATE_PLACEMENT", lifecycle_stage="DEVELOPING")
    
    assert "STRATEGIC_INVESTOR" in result["positive_drivers"]
    assert "EXECUTION_UNCERTAINTY" in result["red_flags"]


def test_case_14_vague_use_of_proceeds(quality_engine):
    """Case 14: Vague proceeds description -> UNCLEAR_USE_OF_PROCEEDS"""
    text = (
        "Perseroan mengumumkan rencana penambahan modal. "
        "Penggunaan dana akan diumumkan kemudian sesuai pertimbangan manajemen."
    )
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="EARLY")
    
    assert "UNCLEAR_USE_OF_PROCEEDS" in result["red_flags"]
    assert result["use_of_proceeds"] == []


def test_case_15_incomplete_transaction_terms_unclear(quality_engine):
    """Case 15: Purely generic text with missing economics -> QUALITY_UNCLEAR"""
    text = "Pemberitahuan rencana penyelenggaraan Rapat Umum Pemegang Saham Luar Biasa perseroan."
    result = quality_engine.evaluate_quality(text, action_type="CORPORATE_ACTION", lifecycle_stage="EARLY")
    
    assert result["quality_label"] == "QUALITY_UNCLEAR"
    assert result["confidence"] == "LOW"
    assert result["opportunity_state"] in ["EARLY_UNCLEAR", "DEVELOPING_UNCLEAR"]


def test_case_16_three_way_score_independence(quality_engine):
    """Case 16: Assert Likelihood, Quality, and Smart Money remain strictly separate"""
    text = (
        "Keterbukaan informasi definitif prospektus penawaran umum terbatas (Right Issue). "
        "Dana hasil penawaran seluruhnya dialokasikan untuk kebutuhan likuiditas mendesak "
        "dan menutup akumulasi kerugian. Dilusi 42%."
    )
    result = quality_engine.evaluate_quality(
        document_text=text,
        action_type="RIGHTS_ISSUE",
        lifecycle_stage="EXPLICIT",
        likelihood_score=95.0
    )
    
    # Likelihood is very high (95.0, explicit)
    # Quality is low (< 45.0, distress/dilution)
    assert result["likelihood_score"] == 95.0
    assert result["likelihood_stage"] == "EXPLICIT"
    assert result["quality_score"] < 45.0
    assert result["quality_label"] in ["RISKY_DILUTIVE", "UNATTRACTIVE_DISTRESS"]
    # Verify quality does not equal likelihood
    assert result["likelihood_score"] != result["quality_score"]


def test_case_17_anti_hallucination_and_missing_evidence(quality_engine):
    """Case 17: Engine must not invent price forecasts or valuation guarantees"""
    text = "Rencana penambahan modal kerja umum perseroan."
    result = quality_engine.evaluate_quality(text, action_type="RIGHTS_ISSUE", lifecycle_stage="EARLY")
    
    # Does not assert future stock returns or price targets
    assert "target harga" not in result["why_attractive"].lower()
    assert "garansi keuntungan" not in result["why_attractive"].lower()
    assert result["subscription_price"] is None
    assert result["dilution_pct"] is None
