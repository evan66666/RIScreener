# RIScreener 📈

> **IDX Strategic Ownership, Smart Money & Corporate Transformation Intelligence Engine**

RIScreener is a full-stack platform designed to analyze, extract, and screen Indonesia Stock Exchange (IDX) corporate action disclosures, strategic shareholding changes, and smart money accumulation signals directly from official company announcements and disclosure PDFs.

---

## 🚀 Key Features

- **Automated Ingestion Engine**: Fetches official IDX disclosures, public announcements, and corporate action releases with automated retrieval and session handling.
- **Deep PDF Information Extraction**: Extracts structured shareholding data, transaction dates, prices, and entity identifiers using high-accuracy PDF parsing and normalization pipelines.
- **Smart Money & Ownership Scoring Rules**:
  - Strategic ownership accumulation / distribution detection.
  - Multi-tier classification for institutional, director/commissioner, and major shareholder actions.
  - Corporate action quality scoring and risk-signal evaluation.
- **FastAPI REST API**: High-performance backend endpoints for screening, filtering, and retrieving granular transaction logs and analytics.
- **Modern React Dashboard**: Built with React 19, TypeScript, Tailwind CSS, and Lucide icons for responsive real-time data visualization and filtering.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM / Database**: [SQLModel](https://sqlmodel.tiangolo.com/) / SQLite
- **PDF Extraction**: [PyMuPDF](https://pymupdf.readthedocs.io/)
- **HTTP & Scraping**: [HTTPX](https://www.python-httpx.org/), [Playwright](https://playwright.dev/)
- **Testing**: [pytest](https://docs.pytest.org/)

### Frontend
- **Framework**: [React 19](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons**: [Lucide React](https://lucide.dev/)

---

## 📁 Repository Structure

```text
RIScreener/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI API routers & endpoints
│   │   ├── engine/         # Pipeline, scoring & screening logic
│   │   ├── extractor/      # PDF parsing and entity normalization
│   │   ├── ingestion/      # IDX disclosure scrapers and clients
│   │   ├── models/         # SQLModel database models & schemas
│   │   └── rules/          # Smart money and strategic ownership rules
│   ├── scripts/            # Maintenance, diagnostic & test scripts
│   ├── tests/              # Test suite
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/            # API client layer
│   │   ├── components/     # UI components & widgets
│   │   ├── types/          # TypeScript interfaces
│   │   └── App.tsx         # Main dashboard view
│   └── package.json        # Frontend dependencies
├── PRD_*.md                # Product requirement documents & specifications
└── README.md
```

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend API server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite development server
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

---

## 🧪 Testing

Run backend tests with pytest:
```bash
cd backend
pytest
```

---

## 📄 License

MIT License. See project documentation for details.
