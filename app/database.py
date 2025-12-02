# app/database.py
"""
Módulo de conexão e sessão com o banco de dados.

- Usa DATABASE_URL definido em app.config
- Cria o engine do SQLAlchemy
- Define SessionLocal para obter sessões
- Define Base para os modelos ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import DATABASE_URL

# -----------------------------------------------------------------------------
# ENGINE
# -----------------------------------------------------------------------------

# Config extra para SQLite (necessário por causa do check_same_thread)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    future=True,
)


# -----------------------------------------------------------------------------
# SESSION FACTORY
# -----------------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


# -----------------------------------------------------------------------------
# BASE ORM
# -----------------------------------------------------------------------------
Base = declarative_base()


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def get_session():
    """
    Helper para obter uma sessão de banco de dados.

    Uso típico em scripts:

        from app.database import get_session

        with get_session() as session:
            # usa session aqui

    Ou com 'next(get_session())' se não estiver usando contexto.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa o banco de dados, criando todas as tabelas definidas em app.models.

    Deve ser chamada em um ponto de bootstrap do sistema, por exemplo:
        - no começo do ETL
        - em um script separado de migração inicial
    """
    # Importa os modelos para que o Base.metadata conheça todas as tabelas
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
