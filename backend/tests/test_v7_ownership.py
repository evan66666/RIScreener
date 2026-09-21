import pytest
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from app.models.schema import Company, Actor, ActorAlias, OwnershipEvent
from app.extractor.actor_normalizer import generate_normalized_key, classify_actor_role, resolve_or_create_actor
from app.extractor.ownership_extractor import extract_ownership_facts_from_text
from app.engine.positioning_engine import cluster_actor_behavior, calculate_disclosed_cost_basis, detect_threshold_crossings
from app.engine.document_router import classify_document_priority

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_actor_normalization():
    # Suffixes and casing
    k1 = generate_normalized_key("PT. Investama Abadi Tbk")
    k2 = generate_normalized_key("Investama Abadi PT")
    k3 = generate_normalized_key("INVESTAMA ABADI, PT.")
    assert k1 == k2 == k3 == "investama abadi"

    role = classify_actor_role("Agus Projosasmito", "Direktur Utama Perseroan")
    assert role == "DIRECTOR"

    psp_role = classify_actor_role("Grup Salim", "Pemegang Saham Pengendali")
    assert psp_role == "CONTROLLER"

def test_resolve_or_create_actor(db_session):
    actor1, created1 = resolve_or_create_actor(db_session, "PT Barito Pacific Tbk")
    assert created1 is True
    assert actor1.canonical_name == "PT Barito Pacific Tbk"
    assert actor1.actor_type == "CORPORATE"

    # Second call with variation should resolve to same actor
    actor2, created2 = resolve_or_create_actor(db_session, "Barito Pacific PT")
    assert created2 is False
    assert actor2.id == actor1.id

def test_extract_valid_acquisition():
    # Case A from PRD Section 59
    text = """
    LAPORAN KEPEMILIKAN SAHAM
    Nama Pemegang Saham: Emirates Tarian Global Ventures
    Jumlah saham sebelum transaksi: 6.880.000.000 saham
    Persentase kepemilikan sebelum transaksi: 4.85%
    Jumlah saham setelah transaksi: 10.150.000.000 saham
    Persentase setelah transaksi: 7.15%
    Jumlah saham yang dibeli: 3.270.000.000 saham
    Harga transaksi: Rp 165
    Tujuan transaksi: Investasi Strategis Jangka Panjang
    """
    facts = extract_ownership_facts_from_text(text, "Laporan Perubahan Kepemilikan Saham Lebih Dari 5%")
    assert len(facts) == 1
    f = facts[0]
    assert f["direction"] == "ACQUIRE"
    assert f["context_classification"] == "MARKET_ACQUISITION_CANDIDATE"
    assert f["delta_shares"] == 3_270_000_000
    assert f["pct_before"] == 4.85
    assert f["pct_after"] == 7.15
    assert f["price"] == 165.0

def test_extract_valid_disposal():
    # Case B from PRD Section 59
    text = """
    LAPORAN KEPEMILIKAN SAHAM
    Nama Pemegang Saham: Falcon Capital Ltd
    Jumlah saham sebelum transaksi: 500.000.000 saham
    Persentase kepemilikan sebelum transaksi: 5.50%
    Jumlah saham setelah transaksi: 300.000.000 saham
    Persentase setelah transaksi: 3.30%
    Jumlah saham yang dijual: 200.000.000 saham
    Harga transaksi: Rp 950
    Tujuan transaksi: Realisasi Keuntungan (Divestasi)
    """
    facts = extract_ownership_facts_from_text(text, "Laporan Pengurangan Kepemilikan Saham")
    assert len(facts) == 1
    f = facts[0]
    assert f["direction"] == "DISPOSE"
    assert f["context_classification"] == "MARKET_DISPOSAL_CANDIDATE"
    assert f["delta_shares"] == 200_000_000
    assert f["pct_after"] < f["pct_before"]

def test_extract_administrative_transfer():
    # Case C from PRD Section 59 - Administrative Transfer should be penalized, not accumulation
    text = """
    PEMBERITAHUAN PENGALIHAN SAHAM
    Nama Pemegang Saham: Keluarga Pendiri
    Jumlah saham sebelum transaksi: 100.000.000 saham
    Jumlah saham setelah transaksi: 50.000.000 saham
    Jumlah saham dialihkan: 50.000.000 saham
    Tujuan transaksi: Hibah keluarga dan restrukturisasi internal antar sub-rekening
    """
    facts = extract_ownership_facts_from_text(text, "Pengalihan Saham Internal Karena Hibah")
    assert len(facts) == 1
    f = facts[0]
    assert f["context_classification"] == "ADMINISTRATIVE_TRANSFER"

def test_repeated_accumulation_cluster():
    # Case E from PRD Section 59 - Repeated acquisition sequence
    events = [
        {
            "event_date": datetime(2026, 8, 1),
            "direction": "ACQUIRE",
            "delta_shares": 50_000_000,
            "pct_before": 2.0,
            "pct_after": 2.7,
            "price": 150.0
        },
        {
            "event_date": datetime(2026, 8, 15),
            "direction": "ACQUIRE",
            "delta_shares": 70_000_000,
            "pct_before": 2.7,
            "pct_after": 3.7,
            "price": 160.0
        }
    ]
    cluster = cluster_actor_behavior(1, 1, events)
    assert cluster["behavior_type"] == "ACCUMULATION_CANDIDATE"
    assert cluster["transaction_count"] == 2
    assert cluster["total_shares_delta"] == 120_000_000
    # Weighted avg price: (50M * 150 + 70M * 160) / 120M = (7500M + 11200M) / 120M = 18700 / 120 = 155.83
    assert cluster["avg_price"] == 155.83

def test_threshold_crossing_detection():
    crossings = detect_threshold_crossings(pct_before=4.8, pct_after=7.1)
    # Crosses 5% upward
    crossed_5 = next((c for c in crossings if c["threshold"] == 5.0 and c["direction"] == "UP"), None)
    assert crossed_5 is not None

def test_document_priority_router():
    tier, should_deep = classify_document_priority("Laporan Kepemilikan Saham Lebih Dari 5%", "Laporan Kepemilikan", "smart")
    assert tier == "TIER_A"
    assert should_deep is True

    tier_b, should_b = classify_document_priority("Pemanggilan RUPSLB Agenda Penambahan Modal Dasar", "Pemanggilan RUPS", "smart")
    assert tier_b == "TIER_B"
    assert should_b is True

    tier_c, should_c = classify_document_priority("Laporan Keuangan Triwulan II 2026", "Laporan Keuangan", "smart")
    assert tier_c == "TIER_C"
    assert should_c is False
