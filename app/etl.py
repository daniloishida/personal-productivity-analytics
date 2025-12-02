# app/etl.py
"""
ETL do projeto Personal Productivity Analytics.

Responsabilidades:
- Ler CSVs de tarefas (tasks.csv) e despesas (finance.csv)
- Tratar e normalizar dados (tipos, categorias, datas)
- Carregar no banco (SQLite ou outro, via SQLAlchemy)
- Evitar duplicação de tasks via external_id (upsert simples)
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from .config import DATA_DIR
from .database import SessionLocal, init_db
from .models import Task, Expense


# ---------------------------------------------------------------------------
# Helpers de leitura
# ---------------------------------------------------------------------------

def _read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"[ETL] ⚠ Arquivo não encontrado: {path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        print(f"[ETL] ✅ Leitura de CSV concluída: {path} ({len(df)} linhas)")
        return df
    except Exception as e:
        print(f"[ETL] ❌ Erro ao ler {path}: {e}")
        return pd.DataFrame()


# ---------------------------------------------------------------------------
# Transformações
# ---------------------------------------------------------------------------

def _transform_tasks(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    # Normaliza nomes de colunas (caso venham com maiúsculas, espaços, etc.)
    df = df.rename(
        columns={
            "external_id": "external_id",
            "title": "title",
            "category": "category",
            "completed_at": "completed_at",
            "duration_minutes": "duration_minutes",
        }
    )

    # Garante colunas obrigatórias
    required_cols = ["external_id", "title", "category", "completed_at", "duration_minutes"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Limpa strings
    df["external_id"] = df["external_id"].astype(str).str.strip()
    df["title"] = df["title"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip().str.lower()

    # Datas
    def parse_dt(val: Optional[str]) -> Optional[datetime]:
        if pd.isna(val) or val is None:
            return None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
            try:
                return datetime.strptime(str(val), fmt)
            except ValueError:
                continue
        return None

    df["completed_at"] = df["completed_at"].apply(parse_dt)

    # Duração em minutos
    df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce").fillna(0.0)

    # Remove linhas sem external_id ou title
    df = df[df["external_id"].notna() & df["external_id"].ne("")]
    df = df[df["title"].notna() & df["title"].ne("")]

    return df


def _transform_finance(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.rename(
        columns={
            "date": "date",
            "category": "category",
            "description": "description",
            "amount": "amount",
        }
    )

    required_cols = ["date", "category", "description", "amount"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = None

    # Datas
    def parse_date(val: Optional[str]) -> Optional[datetime]:
        if pd.isna(val) or val is None:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(str(val), fmt)
            except ValueError:
                continue
        return None

    df["date"] = df["date"].apply(parse_date)

    # Categorias
    df["category"] = df["category"].astype(str).str.strip().str.lower()

    # Description
    df["description"] = df["description"].astype(str).str.strip()

    # Valores
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    # Remove linhas sem data ou amount
    df = df[df["date"].notna()]
    df = df[df["amount"].notna()]

    return df


# ---------------------------------------------------------------------------
# Load (DB)
# ---------------------------------------------------------------------------

def _load_tasks_to_db(df: pd.DataFrame) -> tuple[int, int]:
    """
    Carrega tasks no banco com upsert por external_id.

    Retorna: (inseridos, atualizados)
    """
    if df.empty:
        print("[ETL] ⚠ Nenhuma tarefa para carregar.")
        return 0, 0

    session = SessionLocal()
    inserted = 0
    updated = 0

    try:
        # Carrega external_ids existentes de uma vez só
        existing = {
            ext_id: id_
            for ext_id, id_ in session.query(Task.external_id, Task.id).all()
        }

        for row in df.itertuples(index=False):
            ext_id = row.external_id

            if ext_id in existing:
                # UPDATE (mantém banco em dia sem quebrar UNIQUE)
                task: Task = (
                    session.query(Task)
                    .filter(Task.id == existing[ext_id])
                    .one()
                )
                task.title = row.title
                task.category = row.category
                task.completed_at = row.completed_at
                task.duration_minutes = float(row.duration_minutes or 0.0)
                updated += 1
            else:
                # INSERT
                task = Task(
                    external_id=ext_id,
                    title=row.title,
                    category=row.category,
                    completed_at=row.completed_at,
                    duration_minutes=float(row.duration_minutes or 0.0),
                )
                session.add(task)
                inserted += 1

        session.commit()
        print(f"[ETL] ✅ Tasks carregadas. Inseridos: {inserted}, Atualizados: {updated}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"[ETL] ❌ Erro ao carregar tasks: {e}")
    finally:
        session.close()

    return inserted, updated


def _load_expenses_to_db(df: pd.DataFrame) -> int:
    """
    Carrega despesas no banco.

    Aqui não temos UNIQUE definido, então vamos apenas inserir
    (se quiser, pode-se adicionar uma regra de deduplicação).
    """
    if df.empty:
        print("[ETL] ⚠ Nenhuma despesa para carregar.")
        return 0

    session = SessionLocal()
    inserted = 0

    try:
        # Exemplo simples: sempre insere
        for row in df.itertuples(index=False):
            expense = Expense(
                date=row.date,
                category=row.category,
                description=row.description,
                amount=float(row.amount or 0.0),
            )
            session.add(expense)
            inserted += 1

        session.commit()
        print(f"[ETL] ✅ Expenses carregadas. Inseridos: {inserted}")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"[ETL] ❌ Erro ao carregar expenses: {e}")
    finally:
        session.close()

    return inserted


# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def run_etl():
    """
    Pipeline ETL completo:
    - Garante que as tabelas existem
    - Lê CSVs
    - Transforma dados
    - Carrega no banco (upsert para Task)
    """
    print("[ETL] 🚀 Iniciando ETL...")

    # Garante que o schema está criado
    init_db()

    tasks_csv = DATA_DIR / "tasks.csv"
    finance_csv = DATA_DIR / "finance.csv"

    # Read
    tasks_df_raw = _read_csv_safe(tasks_csv)
    finance_df_raw = _read_csv_safe(finance_csv)

    # Transform
    tasks_df = _transform_tasks(tasks_df_raw)
    finance_df = _transform_finance(finance_df_raw)

    # Load
    t_inserted, t_updated = _load_tasks_to_db(tasks_df)
    e_inserted = _load_expenses_to_db(finance_df)

    print("[ETL] ✅ ETL concluído com sucesso.")
    print(f"[ETL] 📌 Resumo:")
    print(f"      Tasks - inseridas: {t_inserted}, atualizadas: {t_updated}")
    print(f"      Expenses - inseridas: {e_inserted}")
