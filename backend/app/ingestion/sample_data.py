import fitz  # PyMuPDF
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from app.config import settings
from app.ingestion.downloader import calculate_sha256

def create_sample_pdf(file_path: Path, title: str, pages_content: List[str]) -> str:
    """Generates a real PDF file with structured pages using PyMuPDF."""
    doc = fitz.open()
    for idx, content in enumerate(pages_content):
        page = doc.new_page(width=595, height=842)  # A4
        # Title header
        page.insert_text((50, 50), f"{title} - Page {idx + 1}", fontsize=13, fontname="helv", color=(0, 0.2, 0.6))
        # Body text
        rect = fitz.Rect(50, 80, 545, 780)
        page.insert_textbox(rect, content, fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
        # Page footer
        page.insert_text((270, 810), f"- Page {idx + 1} of {len(pages_content)} -", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
    
    doc.save(str(file_path))
    doc.close()
    return calculate_sha256(file_path)

def generate_sample_corpus() -> List[Dict[str, Any]]:
    """
    Generates a comprehensive IDX disclosure corpus across all 15 action families
    with deep coverage of Right Issue / HMETD precursor indicators.
    """
    now = datetime.now()
    corpus = []

    # Rich scenarios defined for IDX issuers
    scenarios = [
        # =========================================================================
        # 0. STRATEGIC OWNERSHIP & CORPORATE TRANSFORMATION (PRD v7.0)
        # =========================================================================
        
        # 0.1 BRMS - Prior Strategic Holder Accumulation (T-30 of Pattern A)
        {
            "ticker": "BRMS",
            "name": "PT Bumi Resources Minerals Tbk",
            "sector": "Basic Materials",
            "title": "Laporan Perubahan Kepemilikan Saham Lebih Dari 5% PT Bumi Resources Minerals Tbk",
            "category": "Laporan Kepemilikan Saham",
            "days_ago": 30,
            "filename": "sample_brms_00_ownership.pdf",
            "pages": [
                "LAPORAN PERUBAHAN KEPEMILIKAN SAHAM LEBIH DARI 5%\n\nNama Pemegang Saham: Emirates Tarian Global Ventures\nJumlah saham sebelum transaksi: 6.880.000.000 saham\nPersentase kepemilikan sebelum transaksi: 4.85%\nJumlah saham setelah transaksi: 10.150.000.000 saham\nPersentase setelah transaksi: 7.15%\nJumlah saham yang dibeli: 3.270.000.000 saham\nHarga transaksi: Rp 165 per lembar saham\nTanggal transaksi: 15 Agustus 2026\nTujuan transaksi: Investasi Strategis Jangka Panjang\nStatus kepemilikan: Kepemilikan Langsung"
            ]
        },

        # 0.2 AMMN - Repeated Director / Strategic Accumulation Sequence (Event 1 & Event 2)
        {
            "ticker": "AMMN",
            "name": "PT Amman Mineral Internasional Tbk",
            "sector": "Basic Materials",
            "title": "Laporan Transaksi Pembelian Saham Oleh Direksi PT Amman Mineral Internasional Tbk",
            "category": "Laporan Transaksi Direksi",
            "days_ago": 20,
            "filename": "sample_ammn_01.pdf",
            "pages": [
                "LAPORAN TRANSAKSI SAHAM OLEH DIREKSI\n\nNama Pemegang Saham: Agus Projosasmito\nJabatan: Direktur\nJumlah saham sebelum transaksi: 50.000.000 saham\nPersentase kepemilikan sebelum transaksi: 0.69%\nJumlah saham setelah transaksi: 120.000.000 saham\nPersentase setelah transaksi: 1.65%\nJumlah saham yang dibeli: 70.000.000 saham\nHarga transaksi: Rp 8.250 per lembar saham\nTujuan transaksi: Investasi pribadi dan peningkatan porsi kepemilikan"
            ]
        },
        {
            "ticker": "AMMN",
            "name": "PT Amman Mineral Internasional Tbk",
            "sector": "Basic Materials",
            "title": "Laporan Perubahan Kepemilikan Saham Lanjutan Oleh Direksi PT Amman Mineral Internasional Tbk",
            "category": "Laporan Transaksi Direksi",
            "days_ago": 5,
            "filename": "sample_ammn_02.pdf",
            "pages": [
                "LAPORAN PERUBAHAN KEPEMILIKAN SAHAM LANJUTAN\n\nNama Pemegang Saham: Agus Projosasmito\nJabatan: Direktur\nJumlah saham sebelum transaksi: 120.000.000 saham\nPersentase kepemilikan sebelum transaksi: 1.65%\nJumlah saham setelah transaksi: 180.000.000 saham\nPersentase setelah transaksi: 2.48%\nJumlah saham yang dibeli: 60.000.000 saham\nHarga transaksi: Rp 8.450 per lembar saham\nTujuan transaksi: Menambah kepemilikan saham perseroan secara berkala"
            ]
        },

        # 0.3 BREN - Corporate Transformation & Geothermal Asset Injection
        {
            "ticker": "BREN",
            "name": "PT Barito Renewables Energy Tbk",
            "sector": "Utilities",
            "title": "Keterbukaan Informasi Injeksi Aset Geotermal dan Kemitraan Strategis Global",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 10,
            "filename": "sample_bren_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI TRANSFORMASI BISNIS DAN INJEKSI ASET\n\nPT Barito Renewables Energy Tbk (BREN) mengumumkan pelaksanaan injeksi aset strategis proyek panas bumi (geotermal) berkapasitas 220 MW dan penandatanganan kemitraan strategis dengan investor global untuk percepatan transisi energi hijau.",
                "STRUKTUR KEPEMILIKAN DAN SINERGI\n\nLangkah transformasi ini memperkuat posisi perseroan sebagai pemimpin energi terbarukan di Asia Tenggara dengan kepemilikan aset geotermal terintegrasi."
            ]
        },

        # 0.4 DATA - Administrative Transfer (Hibah / Restrukturisasi Internal - Penalized)
        {
            "ticker": "DATA",
            "name": "PT Remala Abadi Tbk",
            "sector": "Telecommunication",
            "title": "Laporan Pengalihan Saham Internal Karena Hibah Keluarga",
            "category": "Laporan Kepemilikan Saham",
            "days_ago": 7,
            "filename": "sample_admin_01.pdf",
            "pages": [
                "PEMBERITAHUAN PENGALIHAN SAHAM INTERNAL\n\nNama Pemegang Saham: Keluarga Pendiri\nJumlah saham sebelum transaksi: 100.000.000 saham\nJumlah saham setelah transaksi: 50.000.000 saham\nJumlah saham dialihkan: 50.000.000 saham\nTujuan transaksi: Hibah keluarga dan restrukturisasi internal tanpa adanya transaksi jual beli di pasar reguler bursa."
            ]
        },

        # =========================================================================
        # 1. RIGHT ISSUE / HMETD FOCUS SCENARIOS (Precursors, Developing & Explicit)
        # =========================================================================
        
        # 1.1 BRMS - Right Issue Multi-Stage (Developing -> Explicit)
        {
            "ticker": "BRMS",
            "name": "PT Bumi Resources Minerals Tbk",
            "sector": "Basic Materials",
            "title": "Keterbukaan Informasi Mengenai Rencana Kebutuhan Pendanaan Ekspansi Fasilitas Pengolahan",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 25,
            "filename": "sample_brms_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI\n\nPT Bumi Resources Minerals Tbk (BRMS) mengumumkan bahwa Perseroan memiliki kebutuhan pendanaan ekspansi untuk pengembangan fasilitas pabrik pengolahan emas kedua di Palu. Perseroan sedang mempertimbangkan alternatif pendanaan ekuitas jangka panjang guna memperkuat struktur permodalan.",
                "LAMPIRAN KEUANGAN\n\nPerseroan membutuhkan alokasi capex sebesar USD 100 juta untuk penyelesaian konstruksi infrastruktur tambang emas."
            ]
        },
        {
            "ticker": "BRMS",
            "name": "PT Bumi Resources Minerals Tbk",
            "sector": "Basic Materials",
            "title": "Pemanggilan Rapat Umum Pemegang Saham Luar Biasa (RUPSLB)",
            "category": "Pemanggilan RUPS",
            "days_ago": 12,
            "filename": "sample_brms_02.pdf",
            "pages": [
                "PEMANGGILAN RAPAT UMUM PEMEGANG SAHAM LUAR BIASA (RUPSLB)\n\nDireksi Perseroan dengan ini memanggil para pemegang saham untuk menghadiri RUPSLB dengan agenda penambahan modal dasar dan peningkatan modal ditempatkan dan disetor Perseroan.",
                "PENJELASAN MATA ACARA RAPAT\n\nPersetujuan pemegang saham terkait rencana penambahan modal dan penyesuaian struktur permodalan untuk mendukung ekspansi usaha dan belanja modal (capex)."
            ]
        },
        {
            "ticker": "BRMS",
            "name": "PT Bumi Resources Minerals Tbk",
            "sector": "Basic Materials",
            "title": "Keterbukaan Informasi Rencana Penambahan Modal Melalui HMETD",
            "category": "Corporate Action",
            "days_ago": 0,
            "filename": "sample_brms_03.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI PENERBITAN SAHAM BARU DENGAN HMETD\n\nPerseroan berencana melakukan Penawaran Umum Terbatas dengan Hak Memesan Efek Terlebih Dahulu (HMETD) sebanyak-banyaknya 15.000.000.000 saham baru. Dana yang diperoleh akan digunakan seluruhnya untuk pembangunan fasilitas produksi dan modal kerja.",
                "STRUKTUR PEMBELI SIAGA (STANDBY BUYER)\n\nPerseroan telah menandatangani komitmen awal dengan pembeli siaga (standby buyer) yang berkomitmen mengambil sisa saham yang tidak diambil bagian oleh pemegang saham."
            ]
        },

        # 1.2 BBTN - Right Issue for Housing Loan Expansion (Developing)
        {
            "ticker": "BBTN",
            "name": "PT Bank Tabungan Negara (Persero) Tbk",
            "sector": "Financials",
            "title": "Keterbukaan Informasi Kebutuhan Pendanaan Ekuitas Penyaluran KPR",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 18,
            "filename": "sample_bbtn_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI KEBUTUHAN PENDANAAN EKUITAS\n\nPerseroan menyampaikan adanya kebutuhan pendanaan ekspansi untuk mendukung pembiayaan perumahan nasional. Direksi mengkaji penyesuaian struktur permodalan dan penguatan rasio kecukupan modal (CAR).",
                "RENCANA STRATEGIS\n\nPerseroan mempersiapkan opsi penambahan modal dasar dan pengeluaran saham baru guna menjaga pertumbuhan aset pembiayaan perumahan."
            ]
        },
        {
            "ticker": "BBTN",
            "name": "PT Bank Tabungan Negara (Persero) Tbk",
            "sector": "Financials",
            "title": "Pemanggilan RUPSLB Agenda Penambahan Modal Dasar dan Rencana Pengeluaran Saham Baru",
            "category": "Pemanggilan RUPS",
            "days_ago": 4,
            "filename": "sample_bbtn_02.pdf",
            "pages": [
                "PEMANGGILAN RUPSLB DENGAN AGENDA PENAMBAHAN MODAL\n\nMata acara rapat: Persetujuan penambahan modal dasar serta peningkatan modal ditempatkan dan disetor Perseroan melalui rencana penerbitan saham baru untuk mendukung ekspansi pembiayaan perumahan nasional.",
                "PENGGUNAAN DANA DAN PEMBELI SIAGA\n\nPerseroan menjajaki kesiapan pembeli siaga (standby buyer) strategis guna memperkuat struktur permodalan tier-1 perseroan."
            ]
        },

        # 1.3 PANI - Massive Land Acquisition Rights Issue (Developing)
        {
            "ticker": "PANI",
            "name": "PT Pantai Indah Kapuk Dua Tbk",
            "sector": "Real Estate",
            "title": "Keterbukaan Informasi Kebutuhan Dana Akuisisi Lahan Pengembangan PIK 2",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 15,
            "filename": "sample_pani_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI KEBUTUHAN PENDANAAN AKUISISI LOKASI STRATEGIS\n\nPerseroan memiliki kebutuhan dana ekspansi skala besar untuk akuisisi lahan seluas 1.000 hektar di kawasan pengembangan kota mandiri PIK 2.",
                "ALTERNATIF PERMODALAN\n\nPerseroan mengkaji penerbitan saham baru dan masuknya investor strategis untuk memperkuat modal disetor tanpa beban bunga."
            ]
        },
        {
            "ticker": "PANI",
            "name": "PT Pantai Indah Kapuk Dua Tbk",
            "sector": "Real Estate",
            "title": "Penyelenggaraan RUPSLB Agenda Persetujuan Penambahan Modal dan Pengeluaran Saham Baru",
            "category": "Pemanggilan RUPS",
            "days_ago": 2,
            "filename": "sample_pani_02.pdf",
            "pages": [
                "AGENDA RUPSLB DENGAN AGENDA PENAMBAHAN MODAL\n\nDireksi mengajukan persetujuan pemegang saham untuk rencana penerbitan saham baru dengan target perolehan dana Rp 10,5 Triliun. Pemegang saham pengendali siap bertindak sebagai pembeli siaga (standby buyer).",
                "PEMANFAATAN DANA\n\nDana penambahan modal ekuitas akan digunakan langsung untuk transaksi akuisisi aset tanah matang dan percepatan infrastruktur kota mandiri."
            ]
        },

        # 1.4 BBYB - Digital Bank Core Capital Rights Issue (Developing)
        {
            "ticker": "BBYB",
            "name": "PT Bank Neo Commerce Tbk",
            "sector": "Financials",
            "title": "Keterbukaan Informasi Pemenuhan Ketentuan Modal Inti Minimum Bank Digital",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 20,
            "filename": "sample_bbyb_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI STRUKTUR PERMODALAN\n\nPerseroan berencana melakukan penambahan modal dasar dan pengeluaran saham baru dalam rangka pemenuhan rasio modal inti dan ekspansi kredit ekosistem digital.",
                "KONTRIBUSI MITRA\n\nMitra teknologi strategis menyatakan komitmen awal untuk menyerap porsi hak saham baru."
            ]
        },
        {
            "ticker": "BBYB",
            "name": "PT Bank Neo Commerce Tbk",
            "sector": "Financials",
            "title": "Keterbukaan Informasi Rencana Penambahan Modal dan Pembeli Siaga Strategis",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 3,
            "filename": "sample_bbyb_02.pdf",
            "pages": [
                "RENCANA PENAMBAHAN MODAL DASAR DAN PENERBITAN SAHAM BARU\n\nPerseroan akan melaksanakan penambahan modal dasar dan pengeluaran saham baru dengan dukungan pembeli siaga (standby buyer) dari mitra strategis.",
                "TARGET KERJA SAMA\n\nDana penambahan modal digunakan untuk investasi infrastruktur IT, keamanan siber, dan modal kerja penyaluran kredit digital."
            ]
        },

        # 1.5 WIKA - Capital Restructuring & Infrastructure Capex (Developing)
        {
            "ticker": "WIKA",
            "name": "PT Wijaya Karya (Persero) Tbk",
            "sector": "Infrastructures",
            "title": "Keterbukaan Informasi Rencana Penyehatan Keuangan dan Kebutuhan Modal Kerja Proyek",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 16,
            "filename": "sample_wika_01.pdf",
            "pages": [
                "PENJELASAN RESTRUKTURISASI DAN KEBUTUHAN PENDANAAN\n\nPerseroan membutuhkan penyesuaian struktur permodalan guna menyelesaikan proyek strategis nasional dan percepatan infrastruktur IKN. Perseroan mengupayakan penguatan ekuitas.",
                "AGENDA PERMODALAN\n\nPerseroan mengusulkan penambahan modal dasar dan peningkatan modal ditempatkan dan disetor."
            ]
        },
        {
            "ticker": "WIKA",
            "name": "PT Wijaya Karya (Persero) Tbk",
            "sector": "Infrastructures",
            "title": "Pemanggilan RUPSLB Terkait Agenda Penambahan Modal Melalui HMETD II",
            "category": "Pemanggilan RUPS",
            "days_ago": 1,
            "filename": "sample_wika_02.pdf",
            "pages": [
                "PEMANGGILAN RUPSLB PENAMBAHAN MODAL HMETD\n\nDireksi memanggil pemegang saham untuk menyetujui rights issue HMETD dengan dukungan Penyertaan Modal Negara (PMN) dan alokasi bagi publik.",
                "PENGUATAN NERACA\n\nDana rights issue dialokasikan untuk penyelesaian konstruksi jalan tol, bendungan, dan modal kerja proyek tanpa menambah pinjaman bank."
            ]
        },

        # 1.6 ARCI - Gold Mine Underground Infrastructure Precursor (Early)
        {
            "ticker": "ARCI",
            "name": "PT Archi Indonesia Tbk",
            "sector": "Basic Materials",
            "title": "Keterbukaan Informasi Kebutuhan Pendanaan Pengembangan Tambang Emas Bawah Tanah",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 10,
            "filename": "sample_arci_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI KEBUTUHAN PENDANAAN EKSPANSI\n\nPerseroan mengumumkan adanya kebutuhan pendanaan ekspansi untuk pengembangan tambang emas bawah tanah (underground mining) di Toka Tindung.",
                "STUDI PERMODALAN\n\nPerseroan sedang menjajaki opsi penambahan modal dasar dan penerbitan saham baru guna memperkuat struktur permodalan jangka panjang."
            ]
        },

        # 1.7 DEWA - Mining Contractor Expansion & Capital Agenda (Early)
        {
            "ticker": "DEWA",
            "name": "PT Darma Henwa Tbk",
            "sector": "Energy",
            "title": "Keterbukaan Informasi Rencana RUPSLB Agenda Penyesuaian Struktur Modal dan Pengeluaran Saham",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 6,
            "filename": "sample_dewa_01.pdf",
            "pages": [
                "RENCANA RUPSLB PENYESUAIAN STRUKTUR PERMODALAN\n\nDireksi Perseroan menyampaikan rencana pelaksanaan RUPSLB dengan agenda peningkatan modal ditempatkan dan disetor serta rencana penerbitan saham baru untuk peremajaan alat berat tambang.",
                "SUMBER PENDANAAN\n\nPerseroan mengundang pembeli siaga strategis untuk berpartisipasi dalam penguatan ekuitas perseroan."
            ]
        },

        # 1.8 MDKA - Copper Project Expansion & Equity Financing (Early)
        {
            "ticker": "MDKA",
            "name": "PT Merdeka Copper Gold Tbk",
            "sector": "Basic Materials",
            "title": "Keterbukaan Informasi Penjajakan Pendanaan Ekuitas Proyek Tembaga Tujuh Bukit",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 5,
            "filename": "sample_mdka_01.pdf",
            "pages": [
                "INFORMASI KEBUTUHAN PENDANAAN PROYEK TEMBAGA\n\nPerseroan memiliki kebutuhan dana investasi lanjutan untuk proyek tembaga kelas dunia Tujuh Bukit. Perseroan mempertimbangkan alternatif penambahan modal tanpa utang.",
                "STRUKTUR PENDANAAN\n\nManajemen mengkaji rencana penawaran umum terbatas dan penerbitan efek bersifat ekuitas."
            ]
        },

        # 1.9 BKSL - Capital Structure Adjustment & New Shares Discussion (Early)
        {
            "ticker": "BKSL",
            "name": "PT Sentul City Tbk",
            "sector": "Real Estate",
            "title": "Keterbukaan Informasi Agenda RUPS Terkait Penambahan Modal Dasar dan Saham Baru",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 7,
            "filename": "sample_bksl_01.pdf",
            "pages": [
                "AGENDA RUPSLB PENAMBAHAN MODAL DASAR\n\nPerseroan mengumumkan agenda RUPSLB mengenai persetujuan peningkatan modal dasar dan rencana pengeluaran saham baru dalam rangka pelunasan kewajiban dan ekspansi residensial.",
                "PENGEMBANGAN LAHAN\n\nPenambahan modal ekuitas akan menopang peluncuran klaster komersial baru."
            ]
        },

        # 1.10 AMAR - Capital Increase & Digital Lending Expansion (Early)
        {
            "ticker": "AMAR",
            "name": "PT Bank Amar Indonesia Tbk",
            "sector": "Financials",
            "title": "Keterbukaan Informasi Rencana Penambahan Modal dan Penguatan Rasio Ekuitas",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 8,
            "filename": "sample_amar_01.pdf",
            "pages": [
                "RENCANA PENAMBAHAN MODAL PERSEROAN\n\nDireksi menyampaikan bahwa perseroan berencana melakukan penambahan modal dasar dan mencari alternatif pendanaan ekuitas untuk mendanai pertumbuhan pinjaman digital Tunaiku.",
                "DUKUNGAN PEMEGANG SAHAM\n\nPemegang saham utama mendukung rencana penerbitan saham baru untuk memperkokoh fondasi CAR."
            ]
        },

        # =========================================================================
        # 2. OTHER ACTION FAMILIES (Acquisition, Buyback, Dividends, Strategic, etc.)
        # =========================================================================

        # 2.1 PGAS - Strategic Acquisition (Early Stage)
        {
            "ticker": "PGAS",
            "name": "PT Perusahaan Gas Negara Tbk",
            "sector": "Energy",
            "title": "Keterbukaan Informasi Penjajakan Pengambilalihan Saham Perusahaan Infrastruktur Gas",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 2,
            "filename": "sample_pgas_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI PENJAJAKAN AKUISISI ASET INFRASTRUKTUR\n\nPerseroan menyampaikan bahwa saat ini sedang dalam tahap penjajakan akuisisi dan pelaksanaan uji tuntas (due diligence) atas saham mayoritas perusahaan pengelola pipa transmisi gas di Jawa Timur. Langkah ini bertujuan untuk memperkuat posisi pasar dan sinergi operasional distribusi gas bumi.",
                "STATUS KESEPAKATAN\n\nPerseroan telah menandatangani non-binding Letter of Intent (LOI) dan proses negosiasi pembelian saham masih berjalan secara positif."
            ]
        },

        # 2.2 BBRI - Share Buyback
        {
            "ticker": "BBRI",
            "name": "PT Bank Rakyat Indonesia (Persero) Tbk",
            "sector": "Financials",
            "title": "Keterbukaan Informasi Rencana Pembelian Kembali Saham Perseroan (Share Buyback)",
            "category": "Corporate Action",
            "days_ago": 1,
            "filename": "sample_bbri_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI RENCANA PEMBELIAN KEMBALI SAHAM (BUYBACK)\n\nPT Bank Rakyat Indonesia (Persero) Tbk mengumumkan alokasi dana sebesar Rp 3,0 Triliun untuk pembelian kembali saham (share buyback). Direksi memandang fundamental perseroan sangat solid dan harga saham saat ini undervalued sehingga buyback akan meningkatkan nilai pemegang saham (EPS).",
                "JADWAL DAN PERIODE BUYBACK\n\nPelaksanaan buyback akan dilakukan selama periode 12 bulan setelah memperoleh persetujuan RUPS."
            ]
        },

        # 2.3 GOTO - Strategic Investor
        {
            "ticker": "GOTO",
            "name": "PT GoTo Gojek Tokopedia Tbk",
            "sector": "Technology",
            "title": "Keterbukaan Informasi Kemitraan Strategis dengan Mitra Global",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 0,
            "filename": "sample_goto_01.pdf",
            "pages": [
                "PENGUMUMAN KEMITRAAN STRATEGIS GLOBAL\n\nPerseroan telah menandatangani strategic partnership agreement dengan konsorsium institusi teknologi global terkemuka untuk pengembangan ekosistem pembayaran digital dan AI di Asia Tenggara.",
                "MANFAAT DAN DAMPAK\n\nKerja sama ini mencakup transfer teknologi dan keahlian serta validasi model bisnis perseroan menuju profitabilitas berkelanjutan."
            ]
        },

        # 2.4 MEDC - Major Contract Win
        {
            "ticker": "MEDC",
            "name": "PT Medco Energi Internasional Tbk",
            "sector": "Energy",
            "title": "Perolehan Kontrak Pasokan Gas Material Jangka Panjang Senilai USD 450 Juta",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 4,
            "filename": "sample_medc_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI PEROLEHAN KONTRAK MATERIAL BARU\n\nAnak usaha perseroan telah memenangkan tender dan menandatangani kontrak kerja sama pasokan gas jangka panjang senilai USD 450 Juta dengan pembeli industri regional.",
                "DAMPAK KEUANGAN\n\nKontrak ini menambah order book backlog dan memberikan kepastian recurring revenue selama 10 tahun ke depan dengan margin keuntungan sehat."
            ]
        },

        # 2.5 PTBA - Special Dividend
        {
            "ticker": "PTBA",
            "name": "PT Bukit Asam Tbk",
            "sector": "Energy",
            "title": "Pengumuman Jadwal dan Tata Cara Pembagian Dividen Spesial Tunai",
            "category": "Dividen",
            "days_ago": 6,
            "filename": "sample_ptba_01.pdf",
            "pages": [
                "PENGUMUMAN PEMBAGIAN DIVIDEN SPESIAL TAHUN BUKU 2025\n\nBerdasarkan keputusan RUPS, perseroan memutuskan membagikan dividen khusus (special dividend) sebesar Rp 450 per lembar saham yang berasal dari kelebihan kas (excess cash) dan rekor profitabilitas.",
                "JADWAL PEMBAYARAN\n\nCum dividen di pasar reguler ditetapkan pada 15 September 2026."
            ]
        },

        # 2.6 UNTR - Major Expansion
        {
            "ticker": "UNTR",
            "name": "PT United Tractors Tbk",
            "sector": "Industrials",
            "title": "Keterbukaan Informasi Groundbreaking Fasilitas Smelter Pengolahan Nikel",
            "category": "Corporate Action",
            "days_ago": 7,
            "filename": "sample_untr_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI GROUNDBREAKING FASILITAS PABRIK SMELTER NIKEL BARU\n\nPerseroan memulai konstruksi groundbreaking pembangunan pabrik smelter nikel baru dengan penambahan kapasitas produksi sebesar 50% untuk menangkap lonjakan permintaan pasar global.",
                "JADWAL PROYEK\n\nKomisioning dan operasi komersial ditargetkan selesai dalam 24 bulan."
            ]
        },

        # 2.7 AMMN - Private Placement & Smelter
        {
            "ticker": "AMMN",
            "name": "PT Amman Mineral Internasional Tbk",
            "sector": "Basic Materials",
            "title": "Keterbukaan Informasi Rencana Penambahan Modal Tanpa HMETD (PMTHMETD)",
            "category": "Corporate Action",
            "days_ago": 3,
            "filename": "sample_ammn_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI PENAMBAHAN MODAL TANPA HMETD (PRIVATE PLACEMENT)\n\nPerseroan merencanakan pelaksanaan PMTHMETD atau private placement dengan menerbitkan saham baru hingga 10% untuk memperkuat struktur permodalan dan mendanai ekspansi hilirisasi konsentrator tembaga.",
                "STRUKTUR INVESTOR\n\nDana hasil private placement akan dialokasikan langsung untuk percepatan commissioning fasilitas smelter tembaga dan pemurnian emas."
            ]
        },

        # 2.8 BREN - Geothermal Expansion & Warrant
        {
            "ticker": "BREN",
            "name": "PT Barito Renewables Energy Tbk",
            "sector": "Energy",
            "title": "Keterbukaan Informasi Rencana Penerbitan Efek Berupa Waran dan Ekspansi Panas Bumi",
            "category": "Corporate Action",
            "days_ago": 5,
            "filename": "sample_bren_01.pdf",
            "pages": [
                "RENCANA PENERBITAN WARAN SERI I DAN PENGEMBANGAN PLTP BARU\n\nPerseroan merencanakan penerbitan waran seri I sebagai insentif jangka panjang sekaligus persiapan alokasi capex pembangunan unit PLTP Salak dan Wayang Windu sebesar 100 MW.",
                "POTENSI PENDAPATAN\n\nPenambahan kapasitas produksi energi hijau ini akan memberikan recurring cash flow stabil jangka panjang."
            ]
        },

        # 2.9 CUAN - CSPA Acquisition of Coal Infrastructure
        {
            "ticker": "CUAN",
            "name": "PT Petrindo Jaya Kreasi Tbk",
            "sector": "Energy",
            "title": "Keterbukaan Informasi Penandatanganan CSPA Pengambilalihan Saham Perusahaan Tambang",
            "category": "Corporate Action",
            "days_ago": 8,
            "filename": "sample_cuan_01.pdf",
            "pages": [
                "PENANDATANGANAN CONDITIONAL SHARE PURCHASE AGREEMENT (CSPA)\n\nPerseroan telah menandatangani CSPA pengambilalihan saham sebesar 100% pada entitas pemilik konsesi tambang batubara metalurgi untuk memperkuat portofolio energi dan diversifikasi pendapatan.",
                "PENGUASAAN PASAR\n\nTransaksi akuisisi ini akan meningkatkan cadangan batubara dan sinergi logistik terintegrasi."
            ]
        },

        # 2.10 TPIA - Joint Venture & Petrochemical Expansion
        {
            "ticker": "TPIA",
            "name": "PT Chandra Asri Pacific Tbk",
            "sector": "Basic Materials",
            "title": "Keterbukaan Informasi Pembentukan Joint Venture Strategis Skala Global",
            "category": "Corporate Action",
            "days_ago": 9,
            "filename": "sample_tpia_01.pdf",
            "pages": [
                "KEMITRAAN STRATEGIS DAN PEMBANGUNAN KOMPLEKS PETROKIMIA BARU\n\nPerseroan menandatangani perjanjian kemitraan strategis dengan investor institusi global untuk investasi kompleks petrokimia terintegrasi kedua (CAP2) guna memenuhi lonjakan permintaan pasar domestik.",
                "PENGUATAN NERACA\n\nInvestasi ekuitas dari mitra strategis memperkuat struktur keuangan perseroan tanpa menambah rasio utang."
            ]
        },

        # 2.11 BMRI - Stock Split
        {
            "ticker": "BMRI",
            "name": "PT Bank Mandiri (Persero) Tbk",
            "sector": "Financials",
            "title": "Keterbukaan Informasi Rencana Pemecahan Nilai Nominal Saham (Stock Split)",
            "category": "Corporate Action",
            "days_ago": 11,
            "filename": "sample_bmri_01.pdf",
            "pages": [
                "RENCANA PEMECAHAN NILAI NOMINAL SAHAM (STOCK SPLIT) DENGAN RASIO 1:2\n\nDireksi mengusulkan rencana pemecahan nilai nominal saham (stock split) rasio 1:2 guna meningkatkan likuiditas perdagangan saham perseroan di Bursa Efek Indonesia dan memperluas basis investor ritel.",
                "AGENDA RUPS\n\nRencana stock split telah dimasukkan dalam mata acara RUPSLB mendatang."
            ]
        },

        # 2.12 ADRO - Spin-Off / Separation of Coal Business
        {
            "ticker": "ADRO",
            "name": "PT Adaro Energy Indonesia Tbk",
            "sector": "Energy",
            "title": "Keterbukaan Informasi Rancangan Pemisahan Usaha dan Penawaran Umum Terbuka",
            "category": "Restrukturisasi",
            "days_ago": 14,
            "filename": "sample_adro_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI RANCANGAN PEMISAHAN USAHA (SPIN-OFF)\n\nPerseroan mengumumkan rancangan pemisahan unit bisnis batubara termal (spin-off) untuk membuka nilai (unlock value) dan memfokuskan portofolio induk pada energi hijau dan smelter aluminium.",
                "DISTRIBUSI NILAI\n\nLangkah spin-off ini akan memberikan kemandirian operasional dan distribusi dividen spesial bagi pemegang saham."
            ]
        },

        # 2.13 INCO - Change of Control to MIND ID
        {
            "ticker": "INCO",
            "name": "PT Vale Indonesia Tbk",
            "sector": "Basic Materials",
            "title": "Keterbukaan Informasi Penyelesaian Pengalihan Saham dan Perubahan Pengendali",
            "category": "Corporate Action",
            "days_ago": 18,
            "filename": "sample_inco_01.pdf",
            "pages": [
                "PENGUMUMAN PERUBAHAN PENGENDALI PERSEROAN\n\nDengan telah efektifnya pengalihan 14% saham kepada BUMN Holding Industri Pertambangan, telah terjadi perubahan pengendali perseroan secara resmi.",
                "KOMITMEN INVESTASI\n\nPengendali baru berkomitmen mempercepat pembangunan proyek smelter HPAL di Pomalaa dan Morowali."
            ]
        },

        # 2.14 ICBP - Convertible Bond Issuance
        {
            "ticker": "ICBP",
            "name": "PT Indofood CBP Sukses Makmur Tbk",
            "sector": "Consumer Non-Cyclical",
            "title": "Keterbukaan Informasi Rencana Penerbitan Obligasi Konversi (Convertible Bonds)",
            "category": "Corporate Action",
            "days_ago": 21,
            "filename": "sample_icbp_01.pdf",
            "pages": [
                "RENCANA EMISI OBLIGASI KONVERSI (CONVERTIBLE BONDS) PASAR GLOBAL\n\nPerseroan mempersiapkan emisi surat utang obligasi konversi senilai USD 500 Juta untuk pendanaan jangka panjang ekspansi fasilitas manufaktur mie instan dan makanan di Timur Tengah dan Afrika.",
                "OPSI KONVERSI\n\nSurat utang membawa opsi konversi menjadi ekuitas dengan bunga kompetitif."
            ]
        },

        # 2.15 TLKM - Negated Rumor
        {
            "ticker": "TLKM",
            "name": "PT Telkom Indonesia (Persero) Tbk",
            "sector": "Telecommunication",
            "title": "Tanggapan Atas Permintaan Penjelasan Bursa Terkait Isu Pemberitaan Media",
            "category": "Tanggapan Permintaan Penjelasan",
            "days_ago": 3,
            "filename": "sample_tlkm_01.pdf",
            "pages": [
                "PENJELASAN ATAS PERTANYAAN BURSA MENGENAI ISU AKUISISI\n\nMenanggapi permintaan penjelasan dari Bursa Efek Indonesia, manajemen perseroan dengan ini membantah kabar dan menegaskan bahwa perseroan tidak memiliki rencana untuk melakukan pengambilalihan atau akuisisi entitas telekomunikasi satelit dalam waktu dekat.",
                "KLARIFIKASI INFORMASI\n\nInformasi yang beredar di media massa bukan merupakan fakta material yang bersumber dari manajemen perseroan."
            ]
        },

        # 2.16 BUMI - Distress PKPU Restructuring
        {
            "ticker": "BUMI",
            "name": "PT BUMI Resources Tbk",
            "sector": "Energy",
            "title": "Keterbukaan Informasi Proses Restrukturisasi Utang dan Penyelesaian Kewajiban PKPU",
            "category": "Pengumuman Keterbukaan Informasi",
            "days_ago": 5,
            "filename": "sample_bumi_01.pdf",
            "pages": [
                "KETERBUKAAN INFORMASI PERMOHONAN RESTRUKTURISASI UTANG DAN PKPU\n\nPerseroan menyampaikan bahwa anak usaha menghadapi masalah likuiditas mendesak dan tekanan arus kas berat. Perseroan sedang mengupayakan restrukturisasi utang akibat potensi gagal bayar kewajiban jatuh tempo.",
                "UPAYA PENYELESAIAN\n\nPerseroan mengajukan rencana konversi utang menjadi saham untuk menghindari putusan pailit dalam persidangan penundaan kewajiban pembayaran utang (PKPU)."
            ]
        },

        # 2.17 ASII - Routine Periodic Filing
        {
            "ticker": "ASII",
            "name": "PT Astra International Tbk",
            "sector": "Industrials",
            "title": "Laporan Bulanan Registrasi Pemegang Efek / Perubahan Kepemilikan Saham Bulanan",
            "category": "Laporan Bulanan",
            "days_ago": 0,
            "filename": "sample_asii_01.pdf",
            "pages": [
                "LAPORAN BULANAN REGISTRASI PEMEGANG EFEK\n\nPerseroan menyampaikan laporan bulanan registrasi pemegang efek untuk periode yang berakhir pada 31 Agustus 2026. Tidak terdapat perubahan signifikan pada struktur pemegang saham pengendali perseroan.",
                "TABEL KEPEMILIKAN\n\nJardine Cycle & Carriage Ltd memiliki 50.11% saham perseroan."
            ]
        }
    ]

    for sc in scenarios:
        pdf_path = settings.pdf_dir / sc["filename"]
        create_sample_pdf(pdf_path, f"{sc['name']} - {sc['title']}", sc["pages"])

        pub_date = now - timedelta(days=sc["days_ago"])
        corpus.append({
            "source_id": f"{sc['ticker']}-DISC-{pub_date.strftime('%Y%m%d')}",
            "ticker": sc["ticker"],
            "name": sc["name"],
            "sector": sc["sector"],
            "title": sc["title"],
            "category": sc["category"],
            "published_at": pub_date,
            "pdf_path": pdf_path,
            "attachments": [{"url": str(pdf_path)}]
        })

    return corpus
