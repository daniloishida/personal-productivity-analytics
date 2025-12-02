# app/config.py
"""
Configurações centrais do projeto Personal Productivity Analytics.

Prioridades de configuração de banco de dados:
1. Variável de ambiente DATABASE_URL (Postgres, MySQL, SQLite, etc.)
2. Caso não exista, usa SQLite local com arquivo na raiz do projeto:
   BASE_DIR / DB_FILENAME (default: personal_analytics.db)

Exemplos de DATABASE_URL:
- SQLite:     sqlite:///C:/path/projeto/personal_analytics.db
- Postgres:   postgresql+psycopg2://user:pass@host:5432/dbname
- MySQL:      mysql+pymysql://user:pass@host:3306/dbname
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# BASE E LOAD DE .ENV
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# DIRETÓRIOS DE DADOS
# -----------------------------------------------------------------------------
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
CURATED_DIR = DATA_DIR / "curated"

for d in (DATA_DIR, RAW_DIR, STAGING_DIR, CURATED_DIR):
    d.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------------------------
# FUNÇÃO PARA MONTAR URL DEFAULT DO SQLITE
# -----------------------------------------------------------------------------
def _build_default_sqlite_url() -> str:
    """
    Monta a URL default de SQLite quando DATABASE_URL não estiver definida.

    Por padrão:
    - usa o arquivo 'personal_analytics.db' na raiz do projeto (BASE_DIR)
    - é possível sobrescrever o nome do arquivo com a var de ambiente DB_FILENAME
    """
    db_filename = os.getenv("DB_FILENAME", "personal_analytics.db")
    db_path = BASE_DIR / db_filename
    # Importante: prefixo sqlite:/// + caminho absoluto
    return f"sqlite:///{db_path}"


# -----------------------------------------------------------------------------
# DATABASE_URL (PRONTA PARA SQLALCHEMY)
# -----------------------------------------------------------------------------
DATABASE_URL: str = os.getenv("DATABASE_URL") or _build_default_sqlite_url()

logger.info("Usando DATABASE_URL: %s", DATABASE_URL)


__all__ = [
    "BASE_DIR",
    "DATA_DIR",
    "RAW_DIR",
    "STAGING_DIR",
    "CURATED_DIR",
    "DATABASE_URL",
]
