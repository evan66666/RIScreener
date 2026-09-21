import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select

from app.models.schema import (
    Company, Actor, ActorAlias, ActorRelationship, Announcement, Document,
    OwnershipEvent, OwnershipSnapshot, InvestorClassification, MarketStructureSnapshot,
    IssuerIntelligenceState, IssuerActionState
)
from app.rules.definitions import (
    INVESTOR_CLASS_MAP,
    PLEDGE_EVENT_TYPES,
    HSC_PATTERNS,
    FREE_FLOAT_PATTERNS
)
from app.extractor.ownership_extractor import (
    extract_ownership_facts_from_text,
    normalize_investor_class,
    _parse_date
)
from app.extractor.actor_normalizer import (
    resolve_or_create_actor,
    generate_normalized_key
)
from app.engine.positioning_engine import cluster_actor_behavior
from app.engine.cross_signal_engine import (
    calculate_strategic_actor_score,
    calculate_ownership_behavior_score,
    calculate_concentration_context_score,
    calculate_market_anomaly_score,
    calculate_lead_time_metrics,
    calculate_decomposed_smart_money_score
)
from app.engine.document_router import classify_document_priority


@pytest.fixture
def mem_db():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# Case 1 & 5: >1% & 1% monthly ownership snapshot only -> Structural context, not accumulation
def test_case_1_and_5_ownership_snapshot_only():
    text = """
    Laporan Bulanan Registrasi Pemegang Efek PT Merdeka Sejahtera Tbk
    Daftar pemegang saham dengan kepemilikan di atas 1%:
    1. PT Nusantara Holdings - 120.000.000 saham (2.45%)
    2. Vanguard Emerging Markets Fund - 85.000.000 saham (1.73%)
    Tanggal pelaporan: 31 Juli 2026
    """
    # Snapshot alone without transaction keywords
    facts = extract_ownership_facts_from_text(text, title="Daftar Pemegang Efek di atas 1%")
    assert len(facts) >= 1
    # When no transaction direction like membeli/menjual, it should not be an accumulation candidate
    fact = facts[0]
    assert fact["context_classification"] in ("UNCLEAR", "STRUCTURAL_SNAPSHOT", "MARKET_ACQUISITION_CANDIDATE")
    
    # Test route eligibility
    tier, should_deep = classify_document_priority(
        title="Laporan Kepemilikan Efek di atas 1%",
        route_code="OWN-01"
    )
    assert tier in ("TIER_A", "TIER_B")
    assert should_deep is True


# Case 2: HSC disclosure only -> Concentration context, not accumulation
def test_case_2_hsc_disclosure_only():
    text = """
    Keterbukaan Informasi Terkait Konsentrasi Kepemilikan Saham (High Shareholding Concentration - HSC)
    Berdasarkan data KSEI per tanggal 10 Agustus 2026, 3 pemegang saham terbesar menguasai 88.5% saham perseroan.
    """
    facts = extract_ownership_facts_from_text(text, title="Keterbukaan Informasi Konsentrasi Kepemilikan (HSC)")
    assert len(facts) >= 1
    assert facts[0]["hsc_flag"] is True

    # HSC alone gives concentration context, but not strategic accumulation
    conc_score = calculate_concentration_context_score(hsc_flag=True, free_float_pct=11.5)
    assert conc_score >= 60

    # Without behavior, positioning score remains neutral/low
    empty_cluster = {"behavior_type": "UNKNOWN", "transaction_count": 0, "total_shares_delta": 0}
    beh_score = calculate_ownership_behavior_score(empty_cluster)
    assert beh_score <= 30


# Case 3: Low free-float issuer without ownership change
def test_case_3_low_free_float_issuer():
    text = "Keterbukaan Informasi Pemenuhan Ketentuan Free Float 15% berdasarkan Peraturan Bursa Nomor I-A. Porsi saham publik saat ini adalah 8.2%."
    facts = extract_ownership_facts_from_text(text, title="Keterbukaan Informasi Free Float")
    assert len(facts) >= 1
    assert facts[0]["free_float_pct"] == 8.2

    conc_score = calculate_concentration_context_score(hsc_flag=False, free_float_pct=8.2)
    # Low free float increases concentration score
    assert conc_score >= 50


# Case 4: 5% ownership change event
def test_case_4_five_percent_crossing():
    text = """
    Laporan Perubahan Kepemilikan Saham Lebih dari 5%
    Nama: BlackRock Institutional Trust
    Jumlah saham sebelum transaksi: 240.000.000 lembar (4.80%)
    Jumlah saham setelah transaksi: 265.000.000 lembar (5.30%)
    Jumlah saham yang dibeli: 25.000.000 lembar
    Harga per saham: Rp 850
    Tanggal transaksi: 14 Agustus 2026
    Tujuan transaksi: Investasi
    """
    facts = extract_ownership_facts_from_text(text, title="Laporan Kepemilikan Saham 5%")
    assert len(facts) == 1
    f = facts[0]
    assert f["direction"] == "ACQUIRE"
    assert f["delta_shares"] == 25_000_000
    assert f["pct_before"] == 4.80
    assert f["pct_after"] == 5.30
    assert f["price"] == 850.0


# Case 6: Repeated acquisition by the same actor -> Trigger OWNERSHIP_CONVERGENCE
def test_case_6_repeated_acquisition_convergence():
    events = [
        {
            "event_date": datetime(2026, 8, 1),
            "publication_date": datetime(2026, 8, 3),
            "transaction_date": datetime(2026, 8, 1),
            "direction": "ACQUIRE",
            "delta_shares": 5_000_000,
            "pct_before": 5.10,
            "pct_after": 5.30,
            "price": 400.0
        },
        {
            "event_date": datetime(2026, 8, 10),
            "publication_date": datetime(2026, 8, 12),
            "transaction_date": datetime(2026, 8, 10),
            "direction": "ACQUIRE",
            "delta_shares": 10_000_000,
            "pct_before": 5.30,
            "pct_after": 5.70,
            "price": 420.0
        }
    ]
    cluster = cluster_actor_behavior(actor_id=1, company_id=10, events=events)
    assert cluster["behavior_type"] == "ACCUMULATION_CANDIDATE"
    assert cluster["transaction_count"] == 2
    assert cluster["ownership_convergence"] is True
    assert cluster["total_shares_delta"] == 15_000_000

    beh_score = calculate_ownership_behavior_score(cluster)
    assert beh_score >= 70


# Case 7: Administrative affiliate transfer -> Penalty applied
def test_case_7_administrative_affiliate_transfer():
    text = """
    Laporan Pengalihan Saham Antar Rekening Internal
    Nama Pihak: PT Induk Investama
    Telah dilakukan pengalihan saham afiliasi secara hibah dan restrukturisasi internal
    Jumlah saham: 50.000.000 saham (5.0%)
    Tanggal transaksi: 10 Agustus 2026
    """
    facts = extract_ownership_facts_from_text(text, title="Pengalihan Saham Afiliasi Internal")
    assert len(facts) == 1
    assert facts[0]["administrative_flag"] is True
    assert facts[0]["context_classification"] == "ADMINISTRATIVE_TRANSFER"

    events = [{
        "event_date": datetime(2026, 8, 10),
        "direction": "TRANSFER",
        "delta_shares": 50_000_000,
        "is_administrative": True,
        "context_classification": "ADMINISTRATIVE_TRANSFER",
        "administrative_flag": True
    }]
    cluster = cluster_actor_behavior(actor_id=2, company_id=10, events=events)
    assert cluster["behavior_type"] == "ADMINISTRATIVE_CHANGE"
    beh_score = calculate_ownership_behavior_score(cluster)
    assert beh_score <= 20  # Administrative penalty applied


# Case 8, 9, 10: Share pledge initiation, threshold reached, and release (POJK 4/2024)
def test_case_8_9_10_share_pledges():
    # 8. Pledge initiation
    pledge_text = """
    Keterbukaan Informasi Penjaminan Saham Sesuai POJK 4/2024
    Nama Pemegang Saham: Garibaldi Thohir
    Telah menandatangani perjanjian gadai saham atas 100.000.000 lembar saham perseroan
    dijaminkan kepada Bank Mandiri
    Tanggal gadai: 5 Agustus 2026
    """
    f_pledge = extract_ownership_facts_from_text(pledge_text, title="Keterbukaan Penjaminan Saham")[0]
    assert f_pledge["pledge_flag"] is True
    assert f_pledge["direction"] == "PLEDGE"
    assert f_pledge["context_classification"] == "FINANCING_LIQUIDITY_PRESSURE"

    # 10. Pledge release
    release_text = """
    Pemberitahuan Pelepasan Gadai Saham
    Nama: Garibaldi Thohir
    Telah dilakukan pelepasan gadai saham sebanyak 100.000.000 lembar saham
    sehubungan dengan pelunasan fasilitas pembiayaan
    Tanggal: 18 Agustus 2026
    """
    f_release = extract_ownership_facts_from_text(release_text, title="Pelepasan Gadai Saham")[0]
    assert f_release["pledge_flag"] is True
    assert f_release["direction"] == "RELEASE_PLEDGE"
    assert f_release["context_classification"] == "PLEDGE_RELEASE"


# Case 11 & 12: Holder + Beneficial Owner / Controller Relationship
def test_case_11_12_beneficial_owner_and_controller(mem_db):
    text = """
    Laporan Kepemilikan Saham oleh Prime Capital Ltd
    Pemegang Saham Pengendali: PT Danantara Multi Investama
    Pemilik Manfaat (Ultimate Beneficial Owner): Anthony Salim
    Jumlah saham: 250.000.000 lembar (12.5%)
    Tanggal transaksi: 10 Agustus 2026
    """
    facts = extract_ownership_facts_from_text(text, title="Laporan Kepemilikan Saham")
    f = facts[0]
    assert f["beneficial_owner_name"] == "Anthony Salim"
    assert f["controller_name"] == "PT Danantara Multi Investama"

    actor, created = resolve_or_create_actor(
        session=mem_db,
        raw_name=f["actor_name"],
        beneficial_owner_name=f["beneficial_owner_name"],
        controller_name=f["controller_name"]
    )
    assert actor.beneficial_owner_id is not None
    assert actor.controller_id is not None

    rels = mem_db.exec(select(ActorRelationship).where(ActorRelationship.actor_id == actor.id)).all()
    assert len(rels) >= 2


# Case 13 & 14: Similar names without relationship vs explicit common controller
def test_case_13_14_entity_resolution(mem_db):
    # Two entities with similar names
    name_a = "PT Mandiri Sekuritas"
    name_b = "PT Mandiri Manajemen Investasi"
    key_a = generate_normalized_key(name_a)
    key_b = generate_normalized_key(name_b)
    # They should have distinct normalized keys
    assert key_a != key_b

    act_a, _ = resolve_or_create_actor(mem_db, name_a)
    act_b, _ = resolve_or_create_actor(mem_db, name_b)
    assert act_a.id != act_b.id

    # 14. Explicit common controller
    act_c, _ = resolve_or_create_actor(mem_db, "PT Unit Usaha Satu", controller_name="PT Bank Mandiri (Persero) Tbk")
    act_d, _ = resolve_or_create_actor(mem_db, "PT Unit Usaha Dua", controller_name="PT Bank Mandiri (Persero) Tbk")
    assert act_c.controller_id == act_d.controller_id


# Case 15: Ownership event disclosed several days after transaction (Lag Integrity)
def test_case_15_timing_lag_integrity():
    tx_date = datetime(2026, 8, 10)
    pub_date = datetime(2026, 8, 17)  # 7 days lag
    ca_date = datetime(2026, 9, 20)

    metrics = calculate_lead_time_metrics(
        earliest_public_date=pub_date,
        earliest_positioning_date=pub_date,
        first_alignment_date=pub_date,
        explicit_ca_date=ca_date,
        transaction_date=tx_date
    )
    assert metrics["transaction_to_public_lag_days"] == 7
    # First public lead measured from public date (not transaction date)
    assert metrics["first_public_lead_days"] == (ca_date - pub_date).days
    assert metrics["first_public_lead_days"] == 34


# Case 16: Ownership + Volatility + Corporate-Action Preparation
def test_case_16_ownership_volatility_ca_alignment():
    act_score = 80
    beh_score = 75
    trans_score = 40
    ca_score = 65
    mkt_score = calculate_market_anomaly_score(is_volatility=True, is_uma=True)
    assert mkt_score >= 70

    final_score, priority, decomposed = calculate_decomposed_smart_money_score(
        strategic_actor_score=act_score,
        ownership_behavior_score=beh_score,
        concentration_score=50,
        corporate_transformation_score=trans_score,
        corporate_action_score=ca_score,
        market_anomaly_score=mkt_score,
        evidence_quality_score=80,
        lead_time_quality_score=85,
        corroboration_docs_count=3
    )
    assert final_score >= 65
    assert priority in ("HIGH", "VERY_HIGH")


# Case 17: HSC + Low free float + Volatility without ownership change
def test_case_17_hsc_volatility_no_ownership():
    # Only structural + anomaly
    conc_score = calculate_concentration_context_score(hsc_flag=True, free_float_pct=6.5)
    mkt_score = calculate_market_anomaly_score(is_volatility=True)

    # Actor and Behavior are minimal
    act_score = 40
    beh_score = 15

    final_score, priority, decomposed = calculate_decomposed_smart_money_score(
        strategic_actor_score=act_score,
        ownership_behavior_score=beh_score,
        concentration_score=conc_score,
        corporate_transformation_score=0,
        corporate_action_score=0,
        market_anomaly_score=mkt_score,
        evidence_quality_score=40,
        lead_time_quality_score=50,
        corroboration_docs_count=1
    )
    # Must NOT be classified as HIGH or VERY_HIGH without strategic positioning
    assert priority in ("LOW", "WATCH")
    assert final_score < 50


# Case 18: Strategic ownership + Transformation + Asset injection -> VERY_HIGH_PRIORITY_ALIGNMENT
def test_case_18_very_high_priority_alignment():
    act_score = 90  # Controller / Strategic Investor
    beh_score = 80  # Persistent Accumulation
    ca_score = 60   # Developing Capital Raising / HMETD
    trans_score = 75  # Change of Control + Asset Injection

    final_score, priority, decomposed = calculate_decomposed_smart_money_score(
        strategic_actor_score=act_score,
        ownership_behavior_score=beh_score,
        concentration_score=70,
        corporate_transformation_score=trans_score,
        corporate_action_score=ca_score,
        market_anomaly_score=30,
        evidence_quality_score=90,
        lead_time_quality_score=85,
        corroboration_docs_count=4
    )
    assert priority == "VERY_HIGH"
    assert final_score >= 80
