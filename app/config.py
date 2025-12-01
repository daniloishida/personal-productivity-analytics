# app/config.py
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# se quiser apontar pra MySQL: mysql+pymysql://user:pass@host:3306/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'personal_analytics.db'}"
)

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
CURATED_DIR = DATA_DIR / "curated"

for d in (DATA_DIR, RAW_DIR, STAGING_DIR, CURATED_DIR):
    d.mkdir(parents=True, exist_ok=True)
