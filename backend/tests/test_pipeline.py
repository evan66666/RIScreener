import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from sqlmodel import Session, create_engine, SQLModel, select
from app.models.schema import Company, Actor, OwnershipEvent, Scan, IssuerActionState, IssuerIntelligenceState
from app.engine.pipeline import execute_screening_pipeline
from app.ingestion.sample_data import generate_sample_corpus

@pytest.fixture
def test_db_session():
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session

@pytest.mark.asyncio
async def test_full_v7_screening_pipeline_execution(test_db_session):
    now = datetime.now()
    d_from = now - timedelta(days=7)
    d_to = now

    with patch("app.engine.pipeline.IDXClient.fetch_announcements", return_value=generate_sample_corpus()):
        scan = await execute_screening_pipeline(
            session=test_db_session,
            scan_from=d_from,
            scan_to=d_to,
            lookback_days=60,
            scan_mode="smart"
        )

    assert scan.status == "COMPLETED"
    assert scan.announcements_found > 0
    assert scan.tier_a_documents > 0
    assert scan.documents_processed > 0
    assert scan.ownership_events_found > 0
    assert scan.bootstrap_performed is True

    # Check companies in DB
    companies = test_db_session.exec(select(Company)).all()
    assert len(companies) > 0

    # Check actors resolved in DB
    actors = test_db_session.exec(select(Actor)).all()
    assert len(actors) > 0

    # Check ownership events persisted
    ow_events = test_db_session.exec(select(OwnershipEvent)).all()
    assert len(ow_events) > 0

    # Check issuer intelligence states calculated
    intel_states = test_db_session.exec(select(IssuerIntelligenceState)).all()
    assert len(intel_states) > 0

    # Check BRMS or AMMN has high smart money score
    high_score = any(s.smart_money_score >= 50 for s in intel_states)
    assert high_score is True


def test_impossible_corporate_action_filter():
    from app.engine.document_router import is_impossible_corporate_action

    # Titles that MUST be excluded (impossible corporate actions)
    assert is_impossible_corporate_action("Penyampaian Bukti Iklan Hasil RUPSLB") is True
    assert is_impossible_corporate_action("Bukti Pemasangan Iklan Keterbukaan Informasi") is True
    assert is_impossible_corporate_action("Bukti Pemuatan Iklan di Harian Kompas") is True
    assert is_impossible_corporate_action("Laporan Kurs Valuta Asing Harian") is True
    assert is_impossible_corporate_action("Laporan Harian Atas Nilai Aktiva Bersih Reksa Dana") is True
    assert is_impossible_corporate_action("Jadwal Pembayaran Bunga Obligasi Berkelanjutan III") is True
    assert is_impossible_corporate_action("Pembayaran Imbalan Sukuk Ijarah") is True
    assert is_impossible_corporate_action("Laporan Bulanan Registrasi Pemegang Efek") is True
    assert is_impossible_corporate_action("Pengumuman Libur Bursa Idul Fitri") is True

    # Valid stock disclosure titles that MUST NOT be excluded
    assert is_impossible_corporate_action("Keterbukaan Informasi Mengenai Kebutuhan Pendanaan Ekspansi") is False
    assert is_impossible_corporate_action("Penjelasan atas Permintaan Penjelasan Bursa") is False
    assert is_impossible_corporate_action("Laporan Informasi atau Fakta Material") is False
    assert is_impossible_corporate_action("Pemberitahuan Rencana RUPS Luar Biasa") is False
    assert is_impossible_corporate_action("Laporan Perubahan Kepemilikan Saham Lebih Dari 5%") is False
    assert is_impossible_corporate_action("Penyampaian Materi Paparan Publik Insidentil") is False
    assert is_impossible_corporate_action("Penyampaian Laporan Keuangan Tahunan") is False


@pytest.mark.asyncio
async def test_prd_v5_general_title_disclosures_are_extracted(test_db_session):
    """
    Verifies that under PRD v5 screening rules, stock announcements with general
    titles (e.g. 'Keterbukaan Informasi Mengenai Rencana Kebutuhan Pendanaan...')
    are deep-extracted via PDF, not skipped as metadata-only.
    """
    from app.models.schema import Announcement, Document

    now = datetime.now()
    d_from = now - timedelta(days=7)
    d_to = now

    with patch("app.engine.pipeline.IDXClient.fetch_announcements", return_value=generate_sample_corpus()):
        scan = await execute_screening_pipeline(
            session=test_db_session,
            scan_from=d_from,
            scan_to=d_to,
            lookback_days=60,
            scan_mode="smart"
        )

    # Find the BRMS general funding disclosure announcement
    funding_ann = test_db_session.exec(
        select(Announcement).where(Announcement.title.contains("Kebutuhan Pendanaan Ekspansi"))
    ).first()
    assert funding_ann is not None
    # Under PRD v5, its PDF was downloaded and processed
    assert funding_ann.status == "PROCESSED_PDF"

    # Verify a Document record exists for this announcement
    doc = test_db_session.exec(
        select(Document).where(Document.announcement_id == funding_ann.id)
    ).first()
    assert doc is not None
    assert doc.extraction_status == "EXTRACTED"

