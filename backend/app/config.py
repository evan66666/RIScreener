import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
DB_PATH = DATA_DIR / "riscreener.db"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "IDX Strategic Ownership, Smart Money & Corporate Transformation Intelligence Engine"
    version: str = "7.0"
    database_url: str = f"sqlite:///{DB_PATH}"
    data_dir: Path = DATA_DIR
    pdf_dir: Path = PDF_DIR
    default_lookback_days: int = 60
    extended_lookback_days: int = 120
    idx_base_url: str = "https://www.idx.co.id/primary"
    request_timeout: float = 15.0
    max_pdf_size_mb: int = 50

settings = Settings()
