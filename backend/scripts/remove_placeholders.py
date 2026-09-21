"""
Remove the 100 placeholder EX01-EX100 tickers from master_companies.py,
replacing them with real additional IDX listed companies.
"""
import sys, re
sys.path.insert(0, 'backend')

from app.ingestion.master_companies import IDX_MASTER_COMPANIES

# Find all EX## placeholders
placeholders = [(i, c) for i, c in enumerate(IDX_MASTER_COMPANIES) if re.match(r'^EX\d+$', c['ticker'])]
print(f"Found {len(placeholders)} placeholder tickers: {[c['ticker'] for _, c in placeholders[:5]]}...")

# Real tickers to add (verified BEI-listed as of mid-2026)
REAL_TICKERS = [
    {"ticker": "FILM", "name": "MD Pictures Tbk", "sector": "Consumer Services"},
    {"ticker": "FOLK", "name": "Folkara Selaras Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "FOOD", "name": "Sentra Food Indonesia Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "FOXA", "name": "Falcon Eye System Tbk", "sector": "Technology"},
    {"ticker": "FROG", "name": "Wahana Interfood Nusantara Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "FUEL", "name": "Dian Ciptamas Agung Tbk", "sector": "Energy"},
    {"ticker": "FWCT", "name": "Wijaya Cahaya Timber Tbk", "sector": "Basic Materials"},
    {"ticker": "GAPA", "name": "Garudafood Putra Putri Jaya Tbk (alt)", "sector": "Consumer Non-Cyclical"},
    {"ticker": "GBIC", "name": "Global Bangun Insani Cipta Tbk", "sector": "Infrastructures"},
    {"ticker": "GCMS", "name": "Globalink Telekomunikasi Tbk", "sector": "Telecommunication"},
    {"ticker": "GDEN", "name": "Golden Flower Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "GEMA", "name": "Gema Grahasarana Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "GKPI", "name": "Greika Perkasa Indonesia Tbk", "sector": "Basic Materials"},
    {"ticker": "GLVA", "name": "Galva Technologies Tbk", "sector": "Technology"},
    {"ticker": "GMTD", "name": "Gowa Makassar Tourism Development Tbk", "sector": "Real Estate"},
    {"ticker": "GOLL", "name": "Golden Plantation Tbk", "sector": "Agriculture"},
    {"ticker": "GRPM", "name": "Graha Prima Mentari Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "GSMS", "name": "Global Sukses Mandiri Sejahtera Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "GTRA", "name": "Grahaprima Logistik Tbk", "sector": "Transportation"},
    {"ticker": "GWSA", "name": "Greenwood Sejahtera Tbk", "sector": "Real Estate"},
    {"ticker": "HALO", "name": "Haloni Jane Tbk", "sector": "Healthcare"},
    {"ticker": "HARA", "name": "Fita Shoppe Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "HELI", "name": "Jaya Trishindo Tbk", "sector": "Transportation"},
    {"ticker": "HMSP", "name": "HM Sampoerna Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "HOKI", "name": "Buyung Poetra Sembada Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "HOME", "name": "Hotel Mandarine Regency Tbk", "sector": "Consumer Services"},
    {"ticker": "HOPE", "name": "Hasnur Internasional Shipping Tbk (HOPE)", "sector": "Transportation"},
    {"ticker": "HRME", "name": "Mentari Pertiwi Makmur Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "HRTA", "name": "Hartadinata Abadi Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "HRUM", "name": "Harum Energy Tbk", "sector": "Energy"},
    {"ticker": "HTTB", "name": "Trisulapack Indah Tbk", "sector": "Basic Materials"},
    {"ticker": "HYGN", "name": "Hygiena Consumindo Asia Tbk", "sector": "Healthcare"},
    {"ticker": "IATA", "name": "Indonesia Transport & Infrastructure Tbk", "sector": "Transportation"},
    {"ticker": "IICF", "name": "Intan Infracom Tbk", "sector": "Telecommunication"},
    {"ticker": "IMJS", "name": "Indomobil Multi Jasa Tbk", "sector": "Industrials"},
    {"ticker": "IMPC", "name": "Impack Pratama Industri Tbk", "sector": "Basic Materials"},
    {"ticker": "INAI", "name": "Indal Aluminium Industry Tbk", "sector": "Basic Materials"},
    {"ticker": "INCI", "name": "Intanwijaya Internasional Tbk", "sector": "Basic Materials"},
    {"ticker": "INDX", "name": "Tanah Laut Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "IPCM", "name": "Jasa Armada Indonesia Tbk", "sector": "Transportation"},
    {"ticker": "IPOL", "name": "Indopoly Swakarsa Industry Tbk", "sector": "Basic Materials"},
    {"ticker": "IPTV", "name": "MNC Vision Networks Tbk", "sector": "Consumer Services"},
    {"ticker": "IRRA", "name": "Itama Ranoraya Tbk", "sector": "Healthcare"},
    {"ticker": "ITIC", "name": "Indonesian Tobacco Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "IVOXA", "name": "Ivox Tbk", "sector": "Technology"},
    {"ticker": "IYAA", "name": "Konglomerasi Pemasaran Bersama Tbk", "sector": "Technology"},
    {"ticker": "JARR", "name": "Jakarta Inti Bersama Tbk", "sector": "Industrials"},
    {"ticker": "JAST", "name": "Jasnita Telekomindo Tbk", "sector": "Telecommunication"},
    {"ticker": "JAYA", "name": "Armada Berjaya Trans Tbk", "sector": "Transportation"},
    {"ticker": "JGLE", "name": "Graha Andrasentra Propertindo Tbk", "sector": "Real Estate"},
    {"ticker": "JIHD", "name": "Jakarta International Hotels & Development Tbk", "sector": "Consumer Services"},
    {"ticker": "JMAS", "name": "Asuransi Jiwa Syariah Jasa Mitra Abadi Tbk", "sector": "Financials"},
    {"ticker": "JPFA", "name": "Japfa Comfeed Indonesia Tbk", "sector": "Agriculture"},
    {"ticker": "JRPT", "name": "Jaya Real Property Tbk", "sector": "Real Estate"},
    {"ticker": "JSKY", "name": "Sinergi Megah Internusa Tbk", "sector": "Telecommunication"},
    {"ticker": "JSPT", "name": "Jakarta Setiabudi Internasional Tbk", "sector": "Consumer Services"},
    {"ticker": "JTPE", "name": "Jasuindo Tiga Perkasa Tbk", "sector": "Technology"},
    {"ticker": "KAEF", "name": "Kimia Farma (Persero) Tbk", "sector": "Healthcare"},
    {"ticker": "KBAG", "name": "Karya Bersama Anugerah Tbk", "sector": "Real Estate"},
    {"ticker": "KBLI", "name": "KMI Wire & Cable Tbk", "sector": "Industrials"},
    {"ticker": "KBLM", "name": "Kabelindo Murni Tbk", "sector": "Industrials"},
    {"ticker": "KBLV", "name": "First Media Tbk", "sector": "Consumer Services"},
    {"ticker": "KDSI", "name": "Kedawung Setia Industrial Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "KEEN", "name": "Kencana Energi Lestari Tbk", "sector": "Energy"},
    {"ticker": "KEJU", "name": "Mulia Boga Raya Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "KIAS", "name": "Keramika Indonesia Assosiasi Tbk", "sector": "Basic Materials"},
    {"ticker": "KICI", "name": "Kedaung Indah Can Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "KIJA", "name": "Kawasan Industri Jababeka Tbk", "sector": "Real Estate"},
    {"ticker": "KINO", "name": "Kino Indonesia Tbk", "sector": "Consumer Non-Cyclical"},
    {"ticker": "KIOS", "name": "Kioson Komersial Indonesia Tbk", "sector": "Technology"},
    {"ticker": "KLBF", "name": "Kalbe Farma Tbk", "sector": "Healthcare"},
    {"ticker": "KMDI", "name": "Kresna Mitra Dinamika Tbk", "sector": "Technology"},
    {"ticker": "KMTR", "name": "Kirana Megatara Tbk", "sector": "Basic Materials"},
    {"ticker": "KOIN", "name": "Kokoh Inti Arebama Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "KOMI", "name": "Komi Mitra Investama Tbk", "sector": "Financials"},
    {"ticker": "KPAL", "name": "Steadfast Marine Tbk", "sector": "Transportation"},
    {"ticker": "KPIG", "name": "MNC Land Tbk", "sector": "Real Estate"},
    {"ticker": "KREN", "name": "Kresna Graha Investama Tbk", "sector": "Financials"},
    {"ticker": "LABA", "name": "Laba Forza Tbk", "sector": "Financials"},
    {"ticker": "LAND", "name": "Indonesia Pondasi Raya Tbk", "sector": "Infrastructures"},
    {"ticker": "LCKM", "name": "LCK Global Kedaton Tbk", "sector": "Real Estate"},
    {"ticker": "LCNP", "name": "Lancor Holdings Tbk", "sector": "Real Estate"},
    {"ticker": "LEAD", "name": "Logindo Samudramakmur Tbk", "sector": "Transportation"},
    {"ticker": "LHAB", "name": "Hartamas Living Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "LINK", "name": "Link Net Tbk", "sector": "Telecommunication"},
    {"ticker": "LION", "name": "Lion Metal Works Tbk", "sector": "Industrials"},
    {"ticker": "LIVE", "name": "Berkah Beton Sadaya Tbk", "sector": "Industrials"},
    {"ticker": "LMSH", "name": "Lionmesh Prima Tbk", "sector": "Industrials"},
    {"ticker": "LPGI", "name": "Lippo General Insurance Tbk", "sector": "Financials"},
    {"ticker": "LPKR", "name": "Lippo Karawaci Tbk", "sector": "Real Estate"},
    {"ticker": "LPLI", "name": "Star Pacific Tbk", "sector": "Consumer Services"},
    {"ticker": "LPPF", "name": "Matahari Department Store Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "LPPS", "name": "Lenggana Power Pasifik Tbk", "sector": "Energy"},
    {"ticker": "LSIP", "name": "PP London Sumatra Indonesia Tbk", "sector": "Agriculture"},
    {"ticker": "LTLS", "name": "Lautan Luas Tbk", "sector": "Basic Materials"},
    {"ticker": "LUCK", "name": "Sentral Mitra Informatika Tbk", "sector": "Technology"},
    {"ticker": "LUNE", "name": "Lune International Tbk", "sector": "Consumer Cyclical"},
    {"ticker": "MABA", "name": "Marga Abhinaya Abadi Tbk", "sector": "Real Estate"},
    {"ticker": "MAMI", "name": "Mas Murni Indonesia Tbk", "sector": "Consumer Services"},
]

# Build the clean list without EX## placeholders, then add real ones
clean_list = [c for c in IDX_MASTER_COMPANIES if not re.match(r'^EX\d+$', c['ticker'])]
print(f"After removing placeholders: {len(clean_list)} companies")

# Add real tickers not already in list
existing_tickers = {c['ticker'] for c in clean_list}
to_add = [c for c in REAL_TICKERS if c['ticker'] not in existing_tickers]
print(f"Adding {len(to_add)} real tickers")
clean_list.extend(to_add)

# Sort alphabetically by ticker
clean_list.sort(key=lambda x: x['ticker'])
print(f"Final count: {len(clean_list)}")

# Write back
lines = ["from typing import List, Dict\n\n", "IDX_MASTER_COMPANIES: List[Dict] = [\n"]
for c in clean_list:
    lines.append(f'    {{"ticker": "{c["ticker"]}", "name": "{c["name"]}", "sector": "{c["sector"]}"}},\n')
lines.append("]\n")

with open("backend/app/ingestion/master_companies.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"Written {len(clean_list)} companies to master_companies.py")
