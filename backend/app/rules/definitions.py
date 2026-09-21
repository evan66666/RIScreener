"""
Corporate Action & Strategic Ownership Rule Definitions (Version 7.3.0 Patch)
Contains structured, versioned rule definitions for:
- 18 IDX Corporate Action Families
- 14 Corporate Transformation Families
- Corporate Action Quality & Shareholder Value Assessment (PRD v7.3)
- Use of Proceeds, Dilution, Recipient & Standby Buyer Taxonomies
- Investor Classification Taxonomy (KSEI 39-investor mapping + normalized classes)
- Share Pledge / Release Event Family (POJK 4/2024 compliance)
- High Shareholding Concentration (HSC) & Free Float Context (15% rule)
- Ownership & Transaction Taxonomies, Anti-False-Positive Rules
"""

from typing import Dict, List, Any

RULE_LIBRARY_VERSION = "7.3.0"

# Common Indonesian & English negation triggers
GLOBAL_NEGATIONS = [
    r"tidak\s+(?:ada|akan|sedang|pernah|memiliki)\s+(?:rencana|agenda|niat|pembahasan)",
    r"belum\s+(?:ada|memiliki|memutuskan|merencanakan)\s+(?:rencana|agenda|keputusan)",
    r"membantah\s+(?:kabar|isu|rumor|berita|informasi)",
    r"tidak\s+benar\s+(?:bahwa|mengenai|adanya)",
    r"bukan\s+merupakan\s+(?:rencana|bagian|agenda)",
    r"tidak\s+melakukan",
    r"tidak\s+terdapat\s+(?:rencana|informasi|fakta)",
    r"has\s+no\s+plan\s+to",
    r"does\s+not\s+intend\s+to",
    r"denies\s+(?:rumors|reports|information)"
]

# Common cancellation / supersession triggers
GLOBAL_CANCELLATIONS = [
    r"dibatalkan",
    r"membatalkan\s+(?:rencana|agenda|pelaksanaan|transaksi|perjanjian)",
    r"tidak\s+(?:jadi|dilanjutkan|diteruskan)",
    r"pengakhiran\s+(?:rencana|perjanjian|kesepakatan|proses)",
    r"batal\s+demi\s+hukum",
    r"cancelled",
    r"terminated\s+(?:the\s+plan|agreement|process)",
    r"aborted"
]

# Common distress / emergency triggers
GLOBAL_DISTRESS = [
    r"gagal\s+bayar",
    r"default",
    r"masalah\s+likuiditas\s+mendesak",
    r"krisis\s+keuangan",
    r"pkpu",
    r"penundaan\s+kewajiban\s+pembayaran\s+utang",
    r"pailit",
    r"kebangkrutan",
    r"tekanan\s+arus\s+kas\s+berat",
    r"menutup\s+kerugian\s+operasional",
    r"restrukturisasi\s+utang\s+akibat\s+gagal\s+bayar"
]

# Common uncertainty / exploratory triggers
GLOBAL_UNCERTAINTY = [
    r"masih\s+dalam\s+(?:tahap\s+)?(?:kajian|penjajakan|eksplorasi|pertimbangan)",
    r"belum\s+(?:dapat\s+dipastikan|final|mengikat)",
    r"bersifat\s+non-binding",
    r"wacana",
    r"subject\s+to\s+feasibility",
    r"exploratory\s+stage"
]

# ─────────────────────────────────────────────────────────────────────────────
# 18 CORPORATE ACTION FAMILIES (PRD v7.0 Section 22)
# ─────────────────────────────────────────────────────────────────────────────

ACTION_FAMILIES: Dict[str, Dict[str, Any]] = {
    "RIGHT_ISSUE_HMETD": {
        "name": "Right Issue / HMETD",
        "category": "CAPITAL_RAISING",
        "explicit_terms": [
            r"hak\s+memesan\s+efek\s+terlebih\s+dahulu",
            r"\bhmetd\b",
            r"penawaran\s+umum\s+terbatas\s+(?:i|ii|iii|iv|v|\d+)",
            r"rights?\s+issue",
            r"rights?\s+offering",
            r"prospektus\s+(?:ringkas\s+)?hmetd",
            r"penerbitan\s+saham\s+dengan\s+hmetd"
        ],
        "early_terms": [
            r"kebutuhan\s+(?:pendanaan|dana)\s+(?:ekspansi|pengembangan|tambahan)",
            r"penambahan\s+modal\s+dasar",
            r"peningkatan\s+modal\s+ditempatkan\s+dan\s+disetor",
            r"rupslb\s+(?:dengan\s+)?agenda\s+penambahan\s+modal",
            r"rencana\s+penerbitan\s+saham\s+baru",
            r"pembeli\s+siaga\s+(?:standby\s+buyer)?",
            r"penyesuaian\s+struktur\s+permodalan",
            r"mencari\s+alternatif\s+pendanaan\s+ekuitas",
            r"standby\s+buyer",
            r"capital\s+structure\s+adjustment"
        ],
        "lifecycle_stages": [
            {"stage": "FUNDING_NEED", "name": "Funding Need", "patterns": [r"kebutuhan\s+dana", r"funding\s+requirement", r"mencari\s+pendanaan"]},
            {"stage": "CAPITAL_DISCUSSION", "name": "Capital Discussion", "patterns": [r"penambahan\s+modal\s+dasar", r"struktur\s+permodalan"]},
            {"stage": "RUPSLB_AGENDA", "name": "RUPSLB Capital Agenda", "patterns": [r"rupslb.*penambahan\s+modal", r"mata\s+acara\s+rups.*modal"]},
            {"stage": "NEW_SHARES_PLANNED", "name": "New Shares Planned", "patterns": [r"penerbitan\s+saham\s+baru", r"rencana\s+pengeluaran\s+saham"]},
            {"stage": "HMETD_DECLARED", "name": "HMETD Disclosed", "patterns": [r"hmetd", r"hak\s+memesan\s+efek\s+terlebih\s+dahulu", r"penawaran\s+umum\s+terbatas"]},
            {"stage": "EXECUTION", "name": "Execution / Trading", "patterns": [r"jadwal\s+pelaksanaan\s+hmetd", r"cum-date\s+hmetd", r"distribusi\s+sertifikat\s+hmetd"]}
        ],
        "positive_contexts": [
            r"ekspansi\s+usaha",
            r"pembangunan\s+fasilitas\s+produksi",
            r"akuisisi\s+(?:perusahaan|aset|tambang|bisnis)",
            r"penurunan\s+beban\s+bunga\s+dan\s+penguatan\s+neraca",
            r"belanja\s+modal\s+(?:capex)"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "PRIVATE_PLACEMENT": {
        "name": "Private Placement / PMTHMETD",
        "category": "CAPITAL_RAISING",
        "explicit_terms": [
            r"penambahan\s+modal\s+tanpa\s+hak\s+memesan\s+efek\s+terlebih\s+dahulu",
            r"\bpmthmetd\b",
            r"private\s+placement",
            r"non-preemptive\s+rights?\s+issue",
            r"penerbitan\s+saham\s+tanpa\s+hmetd"
        ],
        "early_terms": [
            r"masuknya\s+investor\s+strategis",
            r"penyertaan\s+modal\s+langsung",
            r"alokasi\s+saham\s+baru\s+kepada\s+mitra",
            r"penjajakan\s+investor\s+baru",
            r"strategic\s+placement"
        ],
        "lifecycle_stages": [
            {"stage": "STRATEGIC_SEARCH", "name": "Strategic Partner Search", "patterns": [r"menjajaki\s+mitra\s+strategis", r"pembicaraan\s+awal\s+investor"]},
            {"stage": "RUPSLB_AGENDA", "name": "RUPSLB Approval Agenda", "patterns": [r"rupslb.*pmthmetd", r"agenda.*tanpa\s+hmetd"]},
            {"stage": "INVESTOR_IDENTIFIED", "name": "Investor Disclosed", "patterns": [r"nama\s+pemodal\s+strategis", r"pihak\s+pengambil\s+bagian"]},
            {"stage": "PRICE_SET", "name": "Placement Price Set", "patterns": [r"harga\s+pelaksanaan\s+pmthmetd", r"harga\s+nominal\s+penempatan"]},
            {"stage": "EXECUTION", "name": "Execution & Allotment", "patterns": [r"pelaksanaan\s+pmthmetd", r"pencatatan\s+saham\s+tambahan"]}
        ],
        "positive_contexts": [
            r"masuknya\s+dana\s+segar\s+langsung",
            r"sinergi\s+bisnis\s+strategis",
            r"tanpa\s+beban\s+bunga\s+pinjaman"
        ],
        "negative_contexts": [
            r"dilusi\s+signifikan\s+bagi\s+pemegang\s+saham\s+publik",
            r"diskon\s+harga\s+terlalu\s+dalam"
        ] + GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "ACQUISITION": {
        "name": "Acquisition / Pengambilalihan",
        "category": "M_AND_A",
        "explicit_terms": [
            r"akuisisi",
            r"pengambilalihan\s+(?:saham|aset|perusahaan)",
            r"conditional\s+share\s+purchase\s+agreement",
            r"\bcspa\b",
            r"\bppjb\b",
            r"perjanjian\s+jual\s+beli\s+bersyarat",
            r"penyelesaian\s+transaksi\s+pengambilalihan"
        ],
        "early_terms": [
            r"nota\s+kesepahaman\s+(?:mou)?\s+akuisisi",
            r"memorandum\s+of\s+understanding",
            r"tahap\s+uji\s+tuntas\s+(?:due\s+diligence)?",
            r"penjajakan\s+pembelian\s+saham",
            r"head\s+of\s+agreement\s+(?:hoa)?",
            r"term\s+sheet\s+akuisisi",
            r"eksplorasi\s+akuisisi"
        ],
        "lifecycle_stages": [
            {"stage": "EXPLORATORY_MOU", "name": "MOU / Letter of Intent", "patterns": [r"mou", r"nota\s+kesepahaman", r"letter\s+of\s+intent"]},
            {"stage": "DUE_DILIGENCE", "name": "Due Diligence", "patterns": [r"due\s+diligence", r"uji\s+tuntas", r"pemeriksaan\s+finansial"]},
            {"stage": "CSPA_SIGNED", "name": "CSPA Signed", "patterns": [r"cspa", r"perjanjian\s+jual\s+beli\s+bersyarat", r"conditional\s+agreement"]},
            {"stage": "CONDITIONS_PRECEDENT", "name": "Fulfilling CP / Approval", "patterns": [r"persetujuan\s+instansi\s+berwenang", r"kondisi\s+prasyarat"]},
            {"stage": "CLOSING", "name": "Closing / Settlement", "patterns": [r"closing\s+transaksi", r"penyelesaian\s+pengambilalihan", r"efektif\s+menjadi\s+pengendali"]}
        ],
        "positive_contexts": [
            r"peningkatan\s+pangsa\s+pasar",
            r"integrasi\s+hulu\s+hilir",
            r"penambahan\s+cadangan\s+(?:tambang|minyak|gas)",
            r"pendapatan\s+konsolidasian\s+meningkat"
        ],
        "negative_contexts": [
            r"beban\s+utang\s+akuisisi\s+terlalu\s+besar",
            r"transaksi\s+dengan\s+pihak\s+terafiliasi\s+merugikan"
        ] + GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "DIVESTMENT": {
        "name": "Divestment / Pelepasan Aset",
        "category": "M_AND_A",
        "explicit_terms": [
            r"divestasi",
            r"pelepasan\s+(?:saham|aset|kepemilikan|anak\s+perusahaan)",
            r"penjualan\s+(?:saham|aset)\s+material",
            r"divestment",
            r"asset\s+sale"
        ],
        "early_terms": [
            r"mengkaji\s+pelepasan\s+aset\s+non-inti",
            r"pencarian\s+calon\s+pembeli\s+anak\s+perusahaan",
            r"reorganisasi\s+portofolio\s+bisnis",
            r"seeking\s+buyers\s+for\s+non-core\s+assets"
        ],
        "lifecycle_stages": [
            {"stage": "STRATEGIC_REVIEW", "name": "Strategic Asset Review", "patterns": [r"evaluasi\s+aset\s+non-inti", r"rencana\s+pelepasan"]},
            {"stage": "BIDDING_MOU", "name": "Bidding / MOU", "patterns": [r"penawaran\s+dari\s+calon\s+pembeli", r"mou\s+pelepasan"]},
            {"stage": "SALE_AGREEMENT", "name": "Sale Agreement Signed", "patterns": [r"perjanjian\s+penjualan\s+saham", r"spa\s+divestasi"]},
            {"stage": "COMPLETION", "name": "Completion & Gain", "patterns": [r"penyelesaian\s+divestasi", r"penerimaan\s+dana\s+hasil\s+penjualan"]}
        ],
        "positive_contexts": [
            r"penerimaan\s+dana\s+tunai\s+segar",
            r"fokus\s+pada\s+bisnis\s+utama\s+(?:core\s+business)",
            r"penurunan\s+rasio\s+utang\s+(?:deleverage)"
        ],
        "negative_contexts": [
            r"penjualan\s+aset\s+dipaksa\s+karena\s+utang"
        ] + GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "MERGER": {
        "name": "Merger / Penggabungan Usaha",
        "category": "M_AND_A",
        "explicit_terms": [
            r"penggabungan\s+usaha",
            r"merger",
            r"rancangan\s+penggabungan\s+usaha",
            r"peleburan\s+usaha\s+(?:konsolidasi)?"
        ],
        "early_terms": [
            r"penjajakan\s+penggabungan\s+usaha",
            r"kajian\s+merger\s+entitas",
            r"sinergi\s+dua\s+perusahaan",
            r"pembentukan\s+komite\s+merger"
        ],
        "lifecycle_stages": [
            {"stage": "EXPLORATORY", "name": "Exploratory & Discussion", "patterns": [r"penjajakan\s+merger", r"pembahasan\s+penggabungan"]},
            {"stage": "DRAFT_PLAN", "name": "Draft Merger Plan", "patterns": [r"rancangan\s+penggabungan", r"merger\s+plan"]},
            {"stage": "SHAREHOLDER_APPROVAL", "name": "RUPS Approval", "patterns": [r"persetujuan\s+rups.*penggabungan", r"buyback\s+saham\s+tidak\s+setuju"]},
            {"stage": "EFFECTIVE_MERGER", "name": "Effective Merger", "patterns": [r"tanggal\s+efektif\s+penggabungan", r"entitas\s+yang\s+menerima\s+penggabungan"]}
        ],
        "positive_contexts": [
            r"efisiensi\s+operasional\s+dan\s+skala\s+ekonomi",
            r"entitas\s+gabungan\s+menjadi\s+pemimpin\s+pasar"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "SPIN_OFF": {
        "name": "Spin-off / Pemisahan Usaha",
        "category": "RESTRUCTURING",
        "explicit_terms": [
            r"pemisahan\s+usaha",
            r"spin-off",
            r"pemisahan\s+unit\s+usaha\s+syariah\s+(?:uus)?",
            r"rancangan\s+pemisahan"
        ],
        "early_terms": [
            r"persiapan\s+pemisahan\s+lini\s+bisnis",
            r"kewajiban\s+pemisahan\s+regulator",
            r"kajian\s+independensi\s+unit\s+usaha"
        ],
        "lifecycle_stages": [
            {"stage": "PLAN_PREPARATION", "name": "Plan Preparation", "patterns": [r"persiapan\s+pemisahan", r"kajian\s+spin-off"]},
            {"stage": "DRAFT_DISCLOSED", "name": "Draft Disclosed", "patterns": [r"rancangan\s+pemisahan", r"keterbukaan\s+spin-off"]},
            {"stage": "APPROVAL", "name": "RUPS & Regulatory Approval", "patterns": [r"persetujuan\s+rups.*pemisahan", r"izin\s+ojk.*pemisahan"]},
            {"stage": "COMPLETED", "name": "Completed Independence", "patterns": [r"pendirian\s+entitas\s+baru\s+hasil\s+pemisahan", r"efektif\s+spin-off"]}
        ],
        "positive_contexts": [
            r"unlocking\s+value",
            r"fokus\s+manajemen\s+entitas\s+mandiri"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "SHARE_BUYBACK": {
        "name": "Share Buyback / Pembelian Kembali Saham",
        "category": "CAPITAL_ALLOCATION",
        "explicit_terms": [
            r"pembelian\s+kembali\s+saham",
            r"buyback\s+saham",
            r"share\s+buyback",
            r"alokasi\s+dana\s+buyback"
        ],
        "early_terms": [
            r"harga\s+saham\s+tidak\s+mencerminkan\s+fundamental",
            r"menjaga\s+stabilitas\s+harga\s+pasar",
            r"persiapan\s+dana\s+untuk\s+pembelian\s+kembali"
        ],
        "lifecycle_stages": [
            {"stage": "ANNOUNCEMENT_PLAN", "name": "Buyback Plan Announced", "patterns": [r"rencana\s+buyback", r"informasi\s+pembelian\s+kembali"]},
            {"stage": "RUPS_APPROVAL", "name": "RUPS Approval", "patterns": [r"persetujuan\s+rups.*buyback", r"tanpa\s+rups\s+kondisi\s+pasar\s+berfluktuasi"]},
            {"stage": "EXECUTION_PERIOD", "name": "Execution Window", "patterns": [r"periode\s+pembelian\s+kembali", r"realisasi\s+buyback\s+saham"]},
            {"stage": "COMPLETED", "name": "Completed / Treasury Held", "patterns": [r"laporan\s+penyelesaian\s+buyback", r"saham\s+tresuri"]}
        ],
        "positive_contexts": [
            r"arus\s+kas\s+berlebih",
            r"peningkatan\s+earnings\s+per\s+share\s+(?:eps)",
            r"keyakinan\s+manajemen\s+akan\s+nilai\s+intrinsik"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "SPECIAL_DIVIDEND": {
        "name": "Special Dividend / Dividen Spesial",
        "category": "CAPITAL_ALLOCATION",
        "explicit_terms": [
            r"dividen\s+spesial",
            r"special\s+dividend",
            r"dividen\s+luar\s+biasa",
            r"dividen\s+interim\s+bernilai\s+material"
        ],
        "early_terms": [
            r"keuntungan\s+luar\s+biasa\s+penjualan\s+aset",
            r"pembagian\s+kelebihan\s+likuiditas\s+tunai"
        ],
        "lifecycle_stages": [
            {"stage": "PROPOSED", "name": "Proposed", "patterns": [r"usulan\s+dividen\s+spesial", r"rencana\s+dividen\s+luar\s+biasa"]},
            {"stage": "APPROVED", "name": "Approved & Schedule", "patterns": [r"persetujuan\s+direksi\s+komisaris\s+dividen", r"cum\s+date\s+dividen\s+spesial"]},
            {"stage": "PAID", "name": "Payment Date", "patterns": [r"pembayaran\s+dividen\s+spesial"]}
        ],
        "positive_contexts": [
            r"profitabilitas\s+rekor",
            r"imbal\s+hasil\s+bagi\s+pemegang\s+saham",
            r"kinerja\s+keuangan\s+sangat\s+baik"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "STOCK_SPLIT": {
        "name": "Stock Split / Reverse Split",
        "category": "SHARE_STRUCTURE",
        "explicit_terms": [
            r"pemecahan\s+nilai\s+nominal\s+saham\s+(?:stock\s+split)?",
            r"stock\s+split",
            r"penggabungan\s+nilai\s+nominal\s+saham\s+(?:reverse\s+stock\s+split)?",
            r"reverse\s+stock\s+split"
        ],
        "early_terms": [
            r"meningkatkan\s+likuiditas\s+perdagangan\s+saham",
            r"rasio\s+pemecahan\s+saham",
            r"agenda\s+rups.*pemecahan\s+nilai\s+nominal",
            r"penyesuaian\s+harga\s+agar\s+lebih\s+terjangkau"
        ],
        "lifecycle_stages": [
            {"stage": "PLAN_ANNOUNCED", "name": "Plan Announced", "patterns": [r"rencana\s+stock\s+split", r"usulan\s+pemecahan\s+saham"]},
            {"stage": "RUPS_APPROVAL", "name": "RUPS Approval", "patterns": [r"persetujuan\s+rups.*stock\s+split", r"persetujuan\s+pemegang\s+saham.*nominal"]},
            {"stage": "BEI_APPROVAL", "name": "IDX Approval & Schedule", "patterns": [r"persetujuan\s+bursa.*jadwal\s+stock\s+split", r"akhir\s+perdagangan\s+nominal\s+lama"]},
            {"stage": "EFFECTIVE", "name": "Trading with New Nominal", "patterns": [r"awal\s+perdagangan\s+nominal\s+baru", r"efektif\s+stock\s+split"]}
        ],
        "positive_contexts": [
            r"meningkatkan\s+likuiditas\s+transaksi",
            r"memperluas\s+basis\s+investor\s+ritel"
        ],
        "negative_contexts": [
            r"reverse\s+split\s+akibat\s+harga\s+di\s+bawah\s+ketentuan\s+minimum"
        ] + GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "WARRANT": {
        "name": "Warrant / Penerbitan Waran",
        "category": "SECURITIES",
        "explicit_terms": [
            r"waran\s+(?:seri\s+[i|ii|iii|\d+])?",
            r"warrants?",
            r"penerbitan\s+waran",
            r"pelaksanaan\s+waran"
        ],
        "early_terms": [
            r"pemanis\s+(?:sweetener)?\s+penerbitan\s+saham",
            r"rasio\s+waran",
            r"harga\s+pelaksanaan\s+waran",
            r"persiapan\s+emisi\s+waran"
        ],
        "lifecycle_stages": [
            {"stage": "PROPOSAL", "name": "Warrant Proposed", "patterns": [r"rencana\s+penerbitan\s+waran", r"usulan\s+waran"]},
            {"stage": "ISSUED", "name": "Warrant Issued", "patterns": [r"pencatatan\s+waran", r"distribusi\s+waran"]},
            {"stage": "EXERCISE_PERIOD", "name": "Exercise Period", "patterns": [r"periode\s+pelaksanaan\s+waran", r"jadwal\s+konversi\s+waran"]},
            {"stage": "COMPLETED", "name": "Expired / Fully Exercised", "patterns": [r"akhir\s+masa\s+berlaku\s+waran", r"hasil\s+pelaksanaan\s+waran"]}
        ],
        "positive_contexts": [
            r"potensi\s+tambahan\s+modal\s+masa\s+depan",
            r"daya\s+tarik\s+tambahan\s+bagi\s+investor"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "CONVERTIBLE_SECURITIES": {
        "name": "Convertible Securities",
        "category": "SECURITIES",
        "explicit_terms": [
            r"obligasi\s+konversi",
            r"convertible\s+bonds?",
            r"sukuk\s+konversi",
            r"mandatory\s+convertible\s+notes?",
            r"surat\s+utang\s+wajib\s+konversi"
        ],
        "early_terms": [
            r"penerbitan\s+surat\s+utang\s+dapat\s+dikonversi",
            r"negosiasi\s+pembiayaan\s+berbasis\s+ekuitas\s+kuasi",
            r"penjajakan\s+convertible\s+loan"
        ],
        "lifecycle_stages": [
            {"stage": "PLAN_PROPOSED", "name": "Plan Proposed", "patterns": [r"rencana\s+penerbitan\s+obligasi\s+konversi", r"persiapan\s+convertible\s+bond"]},
            {"stage": "APPROVAL", "name": "Approval", "patterns": [r"persetujuan\s+rups.*obligasi\s+konversi", r"efektif\s+ojk.*konversi"]},
            {"stage": "ISSUED", "name": "Issued", "patterns": [r"pencatatan\s+obligasi\s+konversi", r"emisi\s+obligasi\s+konversi"]},
            {"stage": "CONVERSION", "name": "Conversion to Equity", "patterns": [r"pelaksanaan\s+konversi\s+menjadi\s+saham", r"penambahan\s+saham\s+hasil\s+konversi"]}
        ],
        "positive_contexts": [
            r"bunga\s+rendah\s+dengan\s+opsi\s+ekuitas",
            r"pendanaan\s+jangka\s+panjang\s+ekspansi"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "MAJOR_EXPANSION": {
        "name": "Major Expansion / Ekspansi Usaha Skala Besar",
        "category": "BUSINESS_EXPANSION",
        "explicit_terms": [
            r"ekspansi\s+fasilitas\s+(?:produksi|pabrik|smelter)",
            r"pembangunan\s+pabrik\s+baru",
            r"groundbreaking\s+(?:proyek|fasilitas)",
            r"capacity\s+expansion",
            r"major\s+capex\s+deployment"
        ],
        "early_terms": [
            r"studi\s+kelayakan\s+ekspansi",
            r"alokasi\s+belanja\s+modal\s+skala\s+besar",
            r"feasibility\s+study\s+pabrik\s+baru",
            r"rencana\s+peningkatan\s+kapasitas\s+produksi"
        ],
        "lifecycle_stages": [
            {"stage": "FEASIBILITY", "name": "Feasibility Study", "patterns": [r"studi\s+kelayakan", r"kajian\s+ekspansi"]},
            {"stage": "COMMITTED", "name": "Capex Committed", "patterns": [r"alokasi\s+capex\s+disetujui", r"penandatanganan\s+kontrak\s+epc"]},
            {"stage": "CONSTRUCTION", "name": "Construction", "patterns": [r"tahap\s+konstruksi", r"pembangunan\s+fisik"]},
            {"stage": "COMMISSIONING", "name": "Commissioning & COD", "patterns": [r"commercial\s+operation\s+date", r"uji\s+coba\s+operasional", r"beroperasi\s+penuh"]}
        ],
        "positive_contexts": [
            r"peningkatan\s+kapasitas\s+hingga\s+\d+%",
            r"memenuhi\s+permintaan\s+ekspor",
            r"efisiensi\s+biaya\s+skala\s+besar"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "MAJOR_CONTRACT": {
        "name": "Major Contract / Kontrak Material",
        "category": "BUSINESS_COMMERCIAL",
        "explicit_terms": [
            r"perolehan\s+kontrak\s+(?:baru|material)",
            r"penandatanganan\s+kontrak\s+bernilai\s+material",
            r"material\s+contract\s+award",
            r"offtake\s+agreement",
            r"perjanjian\s+pembelian\s+jangka\s+panjang"
        ],
        "early_terms": [
            r"mengikuti\s+tender\s+proyek\s+strategis",
            r"lolos\s+kualifikasi\s+tender",
            r"surat\s+penunjukan\s+(?:letter\s+of\s+award)?",
            r"tahap\s+finalisasi\s+kontrak"
        ],
        "lifecycle_stages": [
            {"stage": "TENDER_BID", "name": "Tender / Bidding", "patterns": [r"mengikuti\s+proses\s+tender", r"penawaran\s+proyek"]},
            {"stage": "LOA_RECEIVED", "name": "Letter of Award", "patterns": [r"letter\s+of\s+award", r"surat\s+penunjukan\s+pemenang"]},
            {"stage": "CONTRACT_SIGNED", "name": "Contract Signed", "patterns": [r"penandatanganan\s+kontrak", r"signing\s+agreement"]},
            {"stage": "EXECUTION", "name": "Project Execution", "patterns": [r"pelaksanaan\s+pekerjaan\s+kontrak", r"milestone\s+proyek"]}
        ],
        "positive_contexts": [
            r"kontrak\s+bernilai\s+triliun",
            r"menjamin\s+pendapatan\s+jangka\s+panjang",
            r"visibilitas\s+arus\s+kas\s+terjamin"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "STRATEGIC_INVESTOR": {
        "name": "Strategic Investor Entry / Investor Strategis",
        "category": "INVESTMENT",
        "explicit_terms": [
            r"masuknya\s+investor\s+strategis",
            r"penyertaan\s+saham\s+oleh\s+investor\s+strategis",
            r"kemitraan\s+investasi\s+strategis",
            r"strategic\s+investor\s+entry",
            r"strategic\s+equity\s+investment"
        ],
        "early_terms": [
            r"pembicaraan\s+dengan\s+calon\s+investor\s+strategis",
            r"eksplorasi\s+kolaborasi\s+investasi",
            r"penjajakan\s+mitra\s+global"
        ],
        "lifecycle_stages": [
            {"stage": "TALKS_MOU", "name": "Exploratory Talks / MOU", "patterns": [r"pembicaraan\s+investor", r"penjajakan\s+kemitraan"]},
            {"stage": "INVESTMENT_AGREEMENT", "name": "Investment Agreement", "patterns": [r"investment\s+agreement", r"perjanjian\s+investasi\s+strategis"]},
            {"stage": "CAPITAL_ENTRY", "name": "Capital Injected / Shares Allotted", "patterns": [r"penyetoran\s+modal\s+investor", r"penyelesaian\s+investasi"]},
            {"stage": "SYNERGY", "name": "Strategic Synergy Rolling", "patterns": [r"realisasi\s+sinergi\s+operasional", r"pengembangan\s+bersama"]}
        ],
        "positive_contexts": [
            r"transfer\s+teknologi\s+dan\s+keahlian",
            r"akses\s+ke\s+pasar\s+internasional",
            r"penguatan\s+permodalan\s+tanpa\s+utang"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "CHANGE_OF_CONTROL": {
        "name": "Change of Control / Perubahan Pengendali",
        "category": "GOVERNANCE",
        "explicit_terms": [
            r"perubahan\s+pengendali(?:\s+perseroan)?",
            r"pergantian\s+pemegang\s+saham\s+pengendali",
            r"pengendali\s+baru\s+perseroan",
            r"change\s+of\s+control",
            r"new\s+controlling\s+shareholder"
        ],
        "early_terms": [
            r"negosiasi\s+pengalihan\s+saham\s+pengendali",
            r"rencana\s+pergantian\s+kendali\s+perseroan",
            r"pembicaraan\s+dengan\s+calon\s+pengendali\s+baru"
        ],
        "lifecycle_stages": [
            {"stage": "NEGOTIATION", "name": "Control Talks / Negotiation", "patterns": [r"negosiasi\s+pengendalian", r"pembahasan\s+pengendali\s+baru"]},
            {"stage": "CSPA_CONTROL", "name": "CSPA for Controlling Stake", "patterns": [r"cspa.*pengendali", r"perjanjian\s+jual\s+beli.*saham\s+pengendali"]},
            {"stage": "EFFECTIVE_CONTROL", "name": "Effective Change of Control", "patterns": [r"telah\s+menjadi\s+pengendali\s+baru", r"efektif\s+perubahan\s+pengendali"]},
            {"stage": "TENDER_OFFER_OBLIGATION", "name": "Mandatory Tender Offer", "patterns": [r"penawaran\s+tender\s+wajib", r"mandatory\s+tender\s+offer"]}
        ],
        "positive_contexts": [
            r"masuknya\s+grup\s+konglomerasi\s+besar",
            r"komitmen\s+pengembangan\s+bisnis\s+jangka\s+panjang",
            r"injeksi\s+aset\s+baru\s+oleh\s+pengendali"
        ],
        "negative_contexts": [
            r"sengketa\s+kepengurusan\s+dan\s+kendali"
        ] + GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "TENDER_OFFER": {
        "name": "Tender Offer / Penawaran Tender",
        "category": "M_AND_A",
        "explicit_terms": [
            r"penawaran\s+tender\s+(?:wajib|sukarela)?",
            r"mandatory\s+tender\s+offer",
            r"voluntary\s+tender\s+offer",
            r"mto\b",
            r"jadwal\s+penawaran\s+tender"
        ],
        "early_terms": [
            r"kewajiban\s+melakukan\s+penawaran\s+tender",
            r"pernyataan\s+rencana\s+tender\s+offer",
            r"persiapan\s+dokumen\s+penawaran\s+tender"
        ],
        "lifecycle_stages": [
            {"stage": "OBLIGATION_TRIGGERED", "name": "Tender Obligation Triggered", "patterns": [r"kewajiban\s+penawaran\s+tender", r"pasca\s+pengambilalihan"]},
            {"stage": "STATEMENT_FILED", "name": "Tender Statement Filed", "patterns": [r"pernyataan\s+penawaran\s+tender", r"keterbukaan\s+tender\s+offer"]},
            {"stage": "OFFERING_WINDOW", "name": "Offering Period", "patterns": [r"periode\s+penawaran\s+tender", r"masa\s+penawaran\s+tender"]},
            {"stage": "SETTLEMENT", "name": "Settlement", "patterns": [r"penyelesaian\s+penawaran\s+tender", r"pembayaran\s+hasil\s+tender"]}
        ],
        "positive_contexts": [
            r"harga\s+penawaran\s+di\s+atas\s+harga\s+pasar\s+(?:premium)",
            r"likuiditas\s+keluar\s+dengan\s+valuasi\s+menarik"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "MATERIAL_CAPITAL_RESTRUCTURING": {
        "name": "Material Capital Restructuring / Restrukturisasi Permodalan",
        "category": "RESTRUCTURING",
        "explicit_terms": [
            r"restrukturisasi\s+permodalan\s+material",
            r"kuasi\s+reorganisasi",
            r"rekapitalisasi\s+modal",
            r"penurunan\s+modal\s+dasar\s+dan\s+disetor",
            r"eliminasi\s+saldo\s+defisit"
        ],
        "early_terms": [
            r"rencana\s+kuasi\s+reorganisasi",
            r"pembersihan\s+neraca\s+(?:balance\s+sheet\s+cleanup)",
            r"penataan\s+kembali\s+struktur\s+ekuitas"
        ],
        "lifecycle_stages": [
            {"stage": "PROPOSAL", "name": "Restructuring Proposed", "patterns": [r"rencana\s+kuasi\s+reorganisasi", r"usulan\s+restrukturisasi\s+modal"]},
            {"stage": "RUPS_APPROVAL", "name": "RUPS Approval", "patterns": [r"persetujuan\s+rups.*kuasi\s+reorganisasi", r"persetujuan\s+kreditor"]},
            {"stage": "COMPLETED", "name": "Clean Balance Sheet Effective", "patterns": [r"efektif\s+kuasi\s+reorganisasi", r"neraca\s+bersih\s+tanpa\s+defisit"]}
        ],
        "positive_contexts": [
            r"membuka\s+kembali\s+kemampuan\s+pembagian\s+dividen",
            r"penyehatan\s+kondisi\s+keuangan\s+perseroan"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    },

    "OTHER_STRATEGIC_TRANSACTION": {
        "name": "Other Strategic Transaction / Transaksi Strategis Lainnya",
        "category": "STRATEGIC",
        "explicit_terms": [
            r"transaksi\s+material\s+strategis",
            r"transaksi\s+afiliasi\s+benturan\s+kepentingan",
            r"penyertaan\s+modal\s+pada\s+perusahaan\s+patungan",
            r"joint\s+venture\s+agreement",
            r"strategic\s+collaboration\s+transaction"
        ],
        "early_terms": [
            r"penjajakan\s+transaksi\s+strategis",
            r"pembentukan\s+konsorsium\s+bisnis",
            r"rencana\s+investasi\s+proyek\s+bersama"
        ],
        "lifecycle_stages": [
            {"stage": "EXPLORATORY", "name": "Exploratory / Consortium", "patterns": [r"penjajakan\s+konsorsium", r"pembicaraan\s+awal"]},
            {"stage": "AGREEMENT", "name": "Definitive Agreement", "patterns": [r"penandatanganan\s+jv\s+agreement", r"perjanjian\s+kerja\s+sama"]},
            {"stage": "EXECUTION", "name": "Transaction Execution", "patterns": [r"penyelesaian\s+transaksi\s+material", r"efektif\s+transaksi"]}
        ],
        "positive_contexts": [
            r"penguatan\s+sinergi\s+usaha",
            r"diversifikasi\s+sumber\s+pendapatan"
        ],
        "negative_contexts": GLOBAL_DISTRESS,
        "negations": GLOBAL_NEGATIONS,
        "uncertainties": GLOBAL_UNCERTAINTY,
        "cancellations": GLOBAL_CANCELLATIONS
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# 14 CORPORATE TRANSFORMATION FAMILIES (PRD v7.0 Section 5.3)
# ─────────────────────────────────────────────────────────────────────────────

TRANSFORMATION_FAMILIES: Dict[str, Dict[str, Any]] = {
    "CHANGE_OF_CONTROL": {
        "name": "Change of Control / Pergantian Pengendali",
        "triggers": [
            r"perubahan\s+pengendali",
            r"pengendali\s+baru",
            r"pergantian\s+pemegang\s+saham\s+pengendali",
            r"new\s+controlling\s+shareholder"
        ]
    },
    "PRINCIPAL_BUSINESS_CHANGE": {
        "name": "Change of Principal Business / Perubahan Kegiatan Usaha Utama",
        "triggers": [
            r"perubahan\s+kegiatan\s+usaha\s+utama",
            r"penambahan\s+kegiatan\s+usaha\s+baru",
            r"pivot\s+bisnis",
            r"perubahan\s+fokus\s+usaha\s+utama"
        ]
    },
    "NEW_STRATEGIC_INDUSTRY": {
        "name": "Entry into New Strategic Industry / Masuk Industri Strategis Baru",
        "triggers": [
            r"masuk\s+ke\s+(?:industri|sektor)\s+(?:energi\s+terbarukan|ev|nikel|emas|data\s+center|ai|logistik)",
            r"diversifikasi\s+ke\s+bidang\s+strategis",
            r"ekspansi\s+lintas\s+sektor"
        ]
    },
    "STRATEGIC_ASSET_ACQUISITION": {
        "name": "Strategic Asset Acquisition / Akuisisi Aset Strategis",
        "triggers": [
            r"akuisisi\s+(?:tambang|lahan|landbank|pabrik|konsesi|data\s+center)",
            r"pembelian\s+aset\s+produktif\s+strategis",
            r"pengambilalihan\s+izin\s+tambang\s+(?:iup)?"
        ]
    },
    "MAJOR_ASSET_DISPOSAL": {
        "name": "Major Asset Disposal / Penjualan Aset Skala Besar",
        "triggers": [
            r"pelepasan\s+seluruh\s+atau\s+sebagian\s+besar\s+aset",
            r"penjualan\s+unit\s+bisnis\s+lama",
            r"divestasi\s+aset\s+operasional"
        ]
    },
    "ASSET_INJECTION": {
        "name": "Asset Injection / Injeksi Aset Baru",
        "triggers": [
            r"injeksi\s+aset",
            r"pemasukan\s+aset\s+(?:inbreng)?",
            r"penyetoran\s+modal\s+dalam\s+bentuk\s+aset\s+(?:inbreng)",
            r"asset\s+injection"
        ]
    },
    "PROJECT_INJECTION": {
        "name": "Project Injection / Injeksi Proyek Baru",
        "triggers": [
            r"injeksi\s+proyek\s+strategis",
            r"pengalihan\s+hak\s+pengelolaan\s+proyek",
            r"pemberian\s+mandat\s+proyek\s+nasional"
        ]
    },
    "STRATEGIC_PARTNERSHIP": {
        "name": "Strategic Partnership / Kemitraan Strategis",
        "triggers": [
            r"kemitraan\s+strategis\s+jangka\s+panjang",
            r"strategic\s+alliance",
            r"kolaborasi\s+ekosistem\s+usaha",
            r"joint\s+development\s+agreement"
        ]
    },
    "NEW_CONTROLLING_GROUP": {
        "name": "New Controlling Group / Masuknya Grup Konglomerasi Baru",
        "triggers": [
            r"bergabungnya\s+(?:grup|holding)\s+baru",
            r"sinergi\s+konglomerasi",
            r"konsolidasi\s+ke\s+dalam\s+grup\s+usaha"
        ]
    },
    "MAJOR_FINANCING_RECAPITALIZATION": {
        "name": "Major Financing / Rekapitalisasi Besar",
        "triggers": [
            r"fasilitas\s+kredit\s+sindikasi\s+skala\s+besar",
            r"rekapitalisasi\s+struktur\s+keuangan",
            r"refinancing\s+komprehensif\s+jangka\s+panjang"
        ]
    },
    "SUBSIDIARY_HOLDING_RESTRUCTURE": {
        "name": "Subsidiary & Holding Structure / Restrukturisasi Holding",
        "triggers": [
            r"pembentukan\s+holding\s+company",
            r"restrukturisasi\s+anak\s+perusahaan",
            r"konsolidasi\s+lini\s+bisnis\s+ke\s+sub-holding"
        ]
    },
    "SPIN_OFF_SEPARATION": {
        "name": "Spin-off & Separation / Pemisahan Unit",
        "triggers": [
            r"pemisahan\s+anak\s+perusahaan",
            r"spin-off\s+divisi\s+strategis",
            r"pemisahan\s+badan\s+usaha"
        ]
    },
    "MERGER_CONSOLIDATION": {
        "name": "Merger & Consolidation / Penggabungan Entitas",
        "triggers": [
            r"penggabungan\s+antar\s+anak\s+perusahaan",
            r"merger\s+entitas\s+sejenis",
            r"konsolidasi\s+operasional"
        ]
    },
    "STRATEGIC_INVESTOR_ENTRY": {
        "name": "Strategic Investor Entry / Masuknya Investor Strategis",
        "triggers": [
            r"masuknya\s+investor\s+jangka\s+panjang",
            r"investor\s+jangkar\s+(?:anchor\s+investor)",
            r"penyertaan\s+dana\s+ekuitas\s+strategis"
        ]
    }
}

TRANSFORMATION_LIFECYCLE_STAGES = [
    {"stage": "EXPLORATION", "name": "Exploration / Penjajakan", "patterns": [r"eksplorasi", r"penjajakan\s+awal", r"kajian\s+awal"]},
    {"stage": "DISCUSSION", "name": "Discussion / Pembahasan", "patterns": [r"pembahasan\s+intensif", r"pertemuan\s+antara\s+pihak"]},
    {"stage": "NEGOTIATION", "name": "Negotiation / Due Diligence", "patterns": [r"negosiasi\s+final", r"due\s+diligence", r"uji\s+tuntas"]},
    {"stage": "AGREEMENT", "name": "Agreement / Penandatanganan", "patterns": [r"penandatanganan\s+mou", r"penandatanganan\s+perjanjian", r"signing"]},
    {"stage": "APPROVAL", "name": "Approval / Persetujuan", "patterns": [r"persetujuan\s+rups", r"izin\s+regulator", r"persetujuan\s+ojk"]},
    {"stage": "EXECUTION", "name": "Execution / Pelaksanaan", "patterns": [r"pelaksanaan\s+transaksi", r"penyerahan\s+aset"]},
    {"stage": "COMPLETED", "name": "Completed / Selesai", "patterns": [r"efektif\s+beroperasi", r"transaksi\s+selesai", r"closing"]}
]

# ─────────────────────────────────────────────────────────────────────────────
# OWNERSHIP & TRANSACTION TAXONOMIES
# ─────────────────────────────────────────────────────────────────────────────

# Transaction Direction normalization
DIRECTION_PATTERNS = {
    "ACQUIRE": [
        r"\bmembeli\b",
        r"\bpembelian\b",
        r"\bacquisition\b",
        r"\bacquired\b",
        r"\bpurchase\b",
        r"\bpurchased\b",
        r"\bmenambah\s+kepemilikan\b",
        r"\bpenambahan\s+kepemilikan\b",
        r"\bmeningkatkan\s+porsi\b"
    ],
    "DISPOSE": [
        r"\bmenjual\b",
        r"\bpenjualan\b",
        r"\bdisposal\b",
        r"\bdisposed\b",
        r"\bsold\b",
        r"\bmengurangi\s+kepemilikan\b",
        r"\bpelepasan\s+saham\b",
        r"\bdivestasi\b"
    ],
    "SUBSCRIBE": [
        r"\bsubscribe\b",
        r"\bmengambil\s+bagian\b",
        r"\bmemesan\s+saham\s+baru\b",
        r"\bpenyertaan\s+saham\s+baru\b"
    ],
    "EXERCISE": [
        r"\bpelaksanaan\s+waran\b",
        r"\bexercise\b",
        r"\btebus\s+waran\b",
        r"\beksekusi\s+hak\b"
    ],
    "CONVERT": [
        r"\bkonversi\s+(?:obligasi|sukuk|utang)\b",
        r"\bconversion\b",
        r"\bpenukaran\s+efek\b"
    ],
    "TRANSFER": [
        r"\bpengalihan\s+saham\b",
        r"\bpemindahan\s+hak\b",
        r"\btransfer\b",
        r"\bhibah\b",
        r"\bwarisan\b"
    ],
    "PLEDGE": [
        r"\bgadai\s+saham\b",
        r"\bpenjaminan\s+saham\b",
        r"\bpledge\b",
        r"\bjaminan\s+fidusia\b"
    ],
    "RELEASE_PLEDGE": [
        r"\bpelepasan\s+gadai\b",
        r"\brelease\s+pledge\b",
        r"\bpencabutan\s+jaminan\b"
    ]
}

# Administrative change keywords (to avoid false accumulation flags)
ADMINISTRATIVE_TRIGGERS = [
    r"\bhibah\b",
    r"\bwarisan\b",
    r"\brestrukturisasi\s+internal\b",
    r"\bpengalihan\s+antar\s+rekening\s+internal\b",
    r"\bdividen\s+saham\b",
    r"\bpenyesuaian\s+nominee\b",
    r"\brepo\b",
    r"\btransaksi\s+repo\b",
    r"\bpemindahan\s+sub\s+rekening\b",
    r"\bsettlement\s+mekanik\b",
    r"\bpengalihan\s+afiliasi\b",
    r"\btransfer\s+afiliasi\b",
    r"\btransaksi\s+afiliasi\s+internal\b"
]

# Analytical ownership thresholds
OWNERSHIP_THRESHOLDS = [0.01, 0.03, 0.05, 0.10, 0.20, 0.50]


# ─────────────────────────────────────────────────────────────────────────────
# INVESTOR CLASSIFICATION TAXONOMY (PRD v7.2 Section 5 - KSEI 39-Investor Mapping)
# ─────────────────────────────────────────────────────────────────────────────

NORMALIZED_INVESTOR_CLASSES = [
    "INDIVIDUAL",
    "INSTITUTION",
    "CORPORATE",
    "FUND",
    "INSURANCE",
    "PENSION",
    "BANK",
    "GOVERNMENT_RELATED",
    "STRATEGIC_INVESTOR",
    "CONTROLLER_RELATED",
    "DIRECTOR",
    "COMMISSIONER",
    "AFFILIATE",
    "FOREIGN",
    "DOMESTIC",
    "CUSTODIAN",
    "OTHER"
]

# KSEI Granular Taxonomy & Indonesian Disclosure Mapping
INVESTOR_CLASS_MAP = {
    # Domestic (ID)
    "id": "INDIVIDUAL",
    "perorangan indonesia": "INDIVIDUAL",
    "individu": "INDIVIDUAL",
    "is": "INSURANCE",
    "asuransi indonesia": "INSURANCE",
    "cp": "CORPORATE",
    "korporasi indonesia": "CORPORATE",
    "pf": "PENSION",
    "dana pensiun indonesia": "PENSION",
    "ib": "BANK",
    "bank indonesia": "BANK",
    "mf": "FUND",
    "reksa dana indonesia": "FUND",
    "sc": "INSTITUTION",
    "perusahaan efek indonesia": "INSTITUTION",
    "fd": "INSTITUTION",
    "yayasan indonesia": "INSTITUTION",
    "ot": "OTHER",
    
    # Foreign (Foreigner / Asing)
    "fo": "INDIVIDUAL",
    "perorangan asing": "INDIVIDUAL",
    "fs": "INSURANCE",
    "asuransi asing": "INSURANCE",
    "fc": "CORPORATE",
    "korporasi asing": "CORPORATE",
    "fp": "PENSION",
    "dana pensiun asing": "PENSION",
    "fb": "BANK",
    "bank asing": "BANK",
    "fm": "FUND",
    "reksa dana asing": "FUND",
    "fx": "INSTITUTION",
    "lembaga keuangan asing": "INSTITUTION"
}

INVESTOR_KEYWORD_PATTERNS = [
    (r"\b(?:reksadana|reksa\s+dana|mutual\s+fund|asset\s+management|investama)\b", "FUND"),
    (r"\b(?:dana\s+pensiun|pension\s+fund|dplk)\b", "PENSION"),
    (r"\b(?:asuransi|insurance|takaful)\b", "INSURANCE"),
    (r"\b(?:bank|perbankan|banking)\b", "BANK"),
    (r"\b(?:sekuritas|securities|perusahaan\s+efek|broker)\b", "INSTITUTION"),
    (r"\b(?:direktur\s+utama|direktur|director|managing\s+director)\b", "DIRECTOR"),
    (r"\b(?:komisaris\s+utama|komisaris|commissioner)\b", "COMMISSIONER"),
    (r"\b(?:pemegang\s+saham\s+pengendali|pengendali|controlling\s+shareholder|psp)\b", "CONTROLLER_RELATED"),
    (r"\b(?:investor\s+strategis|strategic\s+investor|anchor\s+investor)\b", "STRATEGIC_INVESTOR"),
    (r"\b(?:kustodian|custodian|nominee|sub\s+rekening\s+efek)\b", "CUSTODIAN"),
    (r"\b(?:pemerintah|republic\s+of\s+indonesia|kementerian|bumn)\b", "GOVERNMENT_RELATED"),
    (r"\b(?:afiliasi|terafiliasi|affiliated\s+party|entitas\s+anak)\b", "AFFILIATE"),
    (r"\b(?:pt|tbk|ltd|corp|corporation|sdn\s+bhd|pte\s+ltd)\b", "CORPORATE")
]


# ─────────────────────────────────────────────────────────────────────────────
# SHARE PLEDGE / FINANCING EVENT FAMILY (PRD v7.2 Section 4.5, POJK 4/2024)
# ─────────────────────────────────────────────────────────────────────────────

PLEDGE_EVENT_TYPES = {
    "PLEDGE_INITIATED": [
        r"perjanjian\s+gadai\s+saham",
        r"penggadaian\s+saham",
        r"penjaminan\s+saham",
        r"dijaminkan\s+kepada",
        r"menjaminkan\s+saham",
        r"jaminan\s+fidusia\s+atas\s+saham",
        r"pledge\s+of\s+shares\s+agreement"
    ],
    "PLEDGE_INCREASED": [
        r"penambahan\s+(?:jumlah\s+)?gadai\s+saham",
        r"peningkatan\s+saham\s+yang\s+dijaminkan",
        r"penambahan\s+agunan\s+saham"
    ],
    "PLEDGE_DECREASED": [
        r"pengurangan\s+(?:jumlah\s+)?gadai\s+saham",
        r"sebagian\s+gadai\s+saham\s+dilepas"
    ],
    "PLEDGE_RELEASED": [
        r"pelepasan\s+gadai\s+saham",
        r"pencabutan\s+(?:perjanjian\s+)?jaminan\s+saham",
        r"pengakhiran\s+gadai\s+saham",
        r"release\s+of\s+pledge",
        r"saham\s+telah\s+bebas\s+dari\s+gadai"
    ],
    "PLEDGE_THRESHOLD_REACHED": [
        r"gadai\s+saham\s+mencapai\s+(?:ambang\s+batas|threshold|5%)",
        r"kewajiban\s+pelaporan\s+gadai\s+saham",
        r"pojk\s+4\/2024.*gadai"
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# HIGH SHAREHOLDING CONCENTRATION (HSC) & FREE FLOAT (PRD v7.2 Sections 8 & 9)
# ─────────────────────────────────────────────────────────────────────────────

HSC_PATTERNS = [
    r"\bkonsentrasi\s+kepemilikan\s+saham\b",
    r"\bhigh\s+shareholding\s+concentration\b",
    r"\bhsc\b",
    r"\bsaham\s+terkonsentrasi\b",
    r"\bkepemilikan\s+saham\s+terkonsentrasi\s+tinggi\b"
]

FREE_FLOAT_PATTERNS = [
    r"free\s+float",
    r"saham\s+beredar\s+di\s+publik",
    r"porsi\s+kepemilikan\s+masyarakat",
    r"saham\s+publik\s+(?:kurang\s+dari|<)?\s*(?:15%|7\.5%)",
    r"ketentuan\s+(?:minimum\s+)?free\s+float\s+15%",
    r"peraturan\s+bursa\s+nomor\s+i-a"
]

MINIMUM_FREE_FLOAT_PCT = 15.0  # OJK/BEI 2026 rule (15% minimum free float)


# ─────────────────────────────────────────────────────────────────────────────
# NEW CONVERGENCE SIGNALS & ANTI-FALSE-POSITIVE PENALTIES (PRD Sections 13, 14, 15)
# ─────────────────────────────────────────────────────────────────────────────

SIGNAL_OWNERSHIP_CONVERGENCE = "OWNERSHIP_CONVERGENCE"
SIGNAL_VERY_HIGH_ALIGNMENT = "VERY_HIGH_PRIORITY_ALIGNMENT"

# Penalty deductions for non-discretionary or administrative transfers
PENALTY_ADMINISTRATIVE_TRANSFER = 30
PENALTY_UNVERIFIED_RELATIONSHIP = 20
PENALTY_TIMING_LAG_STALE = 15


# ─────────────────────────────────────────────────────────────────────────────
# CORPORATE ACTION QUALITY & SHAREHOLDER VALUE FRAMEWORK (PRD v7.3)
# ─────────────────────────────────────────────────────────────────────────────

# Section 7: Use of Proceeds Taxonomy
USE_OF_PROCEEDS_TAXONOMY = {
    "PRODUCTIVE_GROWTH": [
        r"ekspansi\s+(?:usaha|bisnis|operasional|jaringan)",
        r"belanja\s+modal",
        r"capital\s+expenditure",
        r"capex",
        r"pembangunan\s+(?:fasilitas|pabrik|proyek|infrastruktur)",
        r"peningkatan\s+kapasitas\s+produksi",
        r"pembelian\s+(?:mesin|peralatan|armada|kapal|tanah)",
        r"pengembangan\s+proyek\s+baru"
    ],
    "STRATEGIC_ACQUISITION": [
        r"akuisisi\s+(?:saham|perusahaan|aset|entitas)",
        r"pengambilalihan\s+(?:saham|entitas|aset)",
        r"penyertaan\s+modal\s+pada\s+entitas\s+anak",
        r"injeksi\s+aset\s+operasional",
        r"pembelian\s+unit\s+bisnis"
    ],
    "DELEVERAGING": [
        r"pelunasan\s+(?:sebagian|seluruh)?\s*pinjaman",
        r"pembayaran\s+(?:kembali|pokok)?\s*(?:utang|kewajiban|fasilitas\s+kredit)",
        r"deleveraging",
        r"penurunan\s+beban\s+bunga",
        r"refinancing\s+utang\s+jangka\s+panjang"
    ],
    "GENERAL_WORKING_CAPITAL": [
        r"modal\s+kerja\s+(?:operasional|perseroan|entitas)",
        r"working\s+capital",
        r"kebutuhan\s+operasional\s+umum",
        r"beban\s+operasional\s+rutin"
    ],
    "LIQUIDITY_SUPPORT": [
        r"dukungan\s+likuiditas\s+(?:mendesak|jangka\s+pendek)?",
        r"mempertahankan\s+likuiditas",
        r"emergency\s+liquidity",
        r"dana\s+talangan"
    ],
    "LOSS_COVERAGE": [
        r"menutup\s+(?:akumulasi\s+)?kerugian",
        r"loss\s+coverage",
        r"perbaikan\s+posisi\s+ekuitas\s+negatif"
    ],
    "DEBT_SERVICE": [
        r"pembayaran\s+bunga\s+utang",
        r"service\s+bunga\s+jatuh\s+tempo",
        r"debt\s+service"
    ],
    "RELATED_PARTY_SETTLEMENT": [
        r"penyelesaian\s+utang\s+kepada\s+pihak\s+berelasi",
        r"pelunasan\s+pinjaman\s+afiliasi",
        r"transaksi\s+dengan\s+pihak\s+berafiliasi"
    ]
}

# Section 18: Corporate Action Quality Score Bands
QUALITY_BANDS = {
    "VERY_ATTRACTIVE": (80, 100),
    "ATTRACTIVE": (65, 79),
    "NEUTRAL_MIXED": (50, 64),
    "RISKY_DILUTIVE": (35, 49),
    "UNATTRACTIVE_DISTRESS": (0, 34),
    "QUALITY_UNCLEAR": (-1, -1)
}

# Section 20: Opportunity States
OPPORTUNITY_STATES = [
    "EARLY_ATTRACTIVE",
    "DEVELOPING_ATTRACTIVE",
    "EXPLICIT_ATTRACTIVE",
    "EARLY_UNCLEAR",
    "DEVELOPING_UNCLEAR",
    "EXPLICIT_UNCLEAR",
    "DEVELOPING_RISKY",
    "EXPLICIT_RISKY",
    "DISTRESS_RISK",
    "CONTRADICTED",
    "CANCELLED",
    "EXPIRED",
    "SUPERSEDED"
]

# Section 22: Positive Drivers
QUALITY_POSITIVE_DRIVERS = [
    "STRATEGIC_INVESTOR",
    "PRODUCTIVE_ASSET",
    "SECURED_FINANCING",
    "CONTRACTED_REVENUE",
    "CLEAR_USE_OF_PROCEEDS",
    "CONTROL_ALIGNMENT",
    "STRATEGIC_TRANSFORMATION",
    "DELEVERAGING_BENEFIT",
    "ASSET_INJECTION",
    "REPEATED_SUPPORTING_EVIDENCE"
]

# Section 21: Quality Red Flags
QUALITY_RED_FLAGS = [
    "HIGH_DILUTION",
    "DISTRESS_FINANCING",
    "RELATED_PARTY_RISK",
    "EXECUTION_UNCERTAINTY",
    "CONTROL_TRANSFER",
    "UNCLEAR_USE_OF_PROCEEDS",
    "WEAK_STRATEGIC_RATIONALE",
    "FUNDING_DEPENDENCY",
    "LOW_EVIDENCE_QUALITY"
]

# Regex patterns for Dilution extraction (Section 8)
DILUTION_PATTERNS = [
    r"(?:mengeluarkan|menerbitkan)\s+sebanyak-banyaknya\s+([\d\.,]+)\s+(?:juta|miliar)?\s*(?:lembar\s+)?saham\s+baru",
    r"saham\s+baru\s+yang\s+dikeluarkan\s+sebanyak\s+([\d\.,]+)",
    r"persentase\s+dilusi\s+(?:sebesar\s+)?(?:mencapai\s+)?([\d\.,]+)%",
    r"terdilusi\s+sebesar\s+([\d\.,]+)%",
    r"dilution\s+of\s+([\d\.,]+)%",
    r"rasio\s+(?:hmetd|right\s+issue)\s*(?:adalah)?\s*(\d+\s*:\s*\d+)"
]

# Regex patterns for Subscription Price (Section 9)
SUBSCRIPTION_PRICE_PATTERNS = [
    r"harga\s+(?:pelaksanaan|penawaran|tebusan)\s+(?:sebesar\s+)?(?:rp\.?|idr)\s*([\d\.,]+)",
    r"exercise\s+price\s+(?:of\s+)?(?:rp\.?|idr)?\s*([\d\.,]+)",
    r"subscription\s+price\s+(?:of\s+)?(?:rp\.?|idr)?\s*([\d\.,]+)"
]

# Regex patterns for Standby Buyer & Strategic Investors (Section 10)
RECIPIENT_PATTERNS = {
    "STANDBY_BUYER": [
        r"pembeli\s+siaga",
        r"standby\s+buyer",
        r"bertindak\s+sebagai\s+pembeli\s+siaga",
        r"komitmen\s+pembeli\s+siaga"
    ],
    "STRATEGIC_INVESTOR": [
        r"investor\s+strategis",
        r"strategic\s+investor",
        r"anchor\s+investor",
        r"mitra\s+strategis\s+global",
        r"pemodal\s+strategis"
    ],
    "RELATED_PARTY_RECIPIENT": [
        r"pemegang\s+saham\s+utama\s+akan\s+melaksanakan\s+seluruh\s+hak",
        r"entitas\s+afiliasi\s+mengambil\s+bagian",
        r"pihak\s+berelasi\s+menjadi\s+pembeli\s+siaga"
    ]
}

# Distress Financing Detection (Section 16)
DISTRESS_PATTERNS = [
    r"kelangsungan\s+usaha\s+(?:terancam|going\s+concern)",
    r"kebutuhan\s+likuiditas\s+mendesak",
    r"emergency\s+liquidity",
    r"penundaan\s+kewajiban\s+pembayaran\s+utang\s+(?:pkpu)",
    r"kondisi\s+keuangan\s+kritis",
    r"tekanan\s+arus\s+kas\s+berat",
    r"restrukturisasi\s+utang\s+(?:karena\s+kesulitan|mendesak)",
    r"penjualan\s+aset\s+secara\s+terpaksa"
]

# Execution Conditions & Risk (Section 15)
EXECUTION_CONDITION_PATTERNS = [
    r"tunduk\s+pada\s+persetujuan\s+rups",
    r"subject\s+to\s+shareholder\s+approval",
    r"syarat\s+tangguh",
    r"conditions\s+precedent",
    r"persetujuan\s+ojk\s+(?:belum\s+diperoleh|masih\s+dalam\s+proses)",
    r"belum\s+(?:adanya\s+)?perjanjian\s+definitif",
    r"tahap\s+uji\s+tuntas\s+(?:due\s+diligence)",
    r"masih\s+dapat\s+berubah\s+sesuai\s+hasil\s+negosiasi"
]

# Commercial Asset Quality (Section 12)
ASSET_QUALITY_PATTERNS = [
    r"aset\s+produktif",
    r"sudah\s+beroperasi\s+secara\s+komersial",
    r"commercial\s+operation\s+date\s+(?:cod)",
    r"kontrak\s+penjualan\s+jangka\s+panjang",
    r"power\s+purchase\s+agreement\s+(?:ppa)",
    r"offtake\s+agreement",
    r"menghasilkan\s+arus\s+kas\s+positif"
]

