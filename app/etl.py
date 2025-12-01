# app/etl.py
import pandas as pd
from datetime import datetime

from .config import RAW_DIR, CURATED_DIR
from .models import init_db, SessionLocal, Task, TimeLog, Expense


def _parse_datetime(value: str):
    """Tenta converter string em datetime usando alguns formatos comuns."""
    if pd.isna(value):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    return None


def run_etl() -> None:
    """
    ETL simples:
    - lê tasks.csv, timelog.csv, expenses.csv (se existirem)
    - padroniza colunas
    - grava versões curated em data/curated
    - carrega/atualiza os dados no banco
    """
    init_db()
    session = SessionLocal()

    try:
        # ==========================
        # 1) TASKS
        # ==========================
        tasks_path = RAW_DIR / "tasks.csv"
        if tasks_path.exists():
            tasks_df = pd.read_csv(tasks_path)

            # espera colunas: id,title,category,completed_at,duration_minutes
            tasks_df["completed_at"] = tasks_df["completed_at"].apply(_parse_datetime)

            curated_tasks = CURATED_DIR / "tasks_curated.csv"
            tasks_df.to_csv(curated_tasks, index=False)

            for _, row in tasks_df.iterrows():
                ext_id = str(row["id"])

                # verifica se já existe task com esse external_id
                task = (
                    session.query(Task)
                    .filter(Task.external_id == ext_id)
                    .one_or_none()
                )

                if task is None:
                    # cria nova
                    task = Task(
                        external_id=ext_id,
                        title=row["title"],
                        category=row.get("category") or "desconhecido",
                        completed_at=row["completed_at"],
                        duration_minutes=int(row.get("duration_minutes") or 0),
                    )
                    session.add(task)
                else:
                    # atualiza existente (idempotente)
                    task.title = row["title"]
                    task.category = row.get("category") or "desconhecido"
                    task.completed_at = row["completed_at"]
                    task.duration_minutes = int(row.get("duration_minutes") or 0)

        # ==========================
        # 2) TIME LOGS
        # ==========================
        timelog_path = RAW_DIR / "timelog.csv"
        if timelog_path.exists():
            tl_df = pd.read_csv(timelog_path)
            # espera colunas: task_label,project,started_at,ended_at,duration_minutes
            tl_df["started_at"] = tl_df["started_at"].apply(_parse_datetime)
            tl_df["ended_at"] = tl_df["ended_at"].apply(_parse_datetime)

            curated_tl = CURATED_DIR / "timelog_curated.csv"
            tl_df.to_csv(curated_tl, index=False)

            # aqui não fizemos upsert, assumindo logs como eventos
            for _, row in tl_df.iterrows():
                tl = TimeLog(
                    task_label=row.get("task_label") or "desconhecido",
                    project=row.get("project") or "geral",
                    started_at=row["started_at"],
                    ended_at=row["ended_at"],
                    duration_minutes=int(row.get("duration_minutes") or 0),
                )
                session.add(tl)

        # ==========================
        # 3) EXPENSES
        # ==========================
        expenses_path = RAW_DIR / "expenses.csv"
        if expenses_path.exists():
            exp_df = pd.read_csv(expenses_path)
            # espera colunas: date,category,description,amount
            exp_df["date"] = exp_df["date"].apply(_parse_datetime)

            curated_exp = CURATED_DIR / "expenses_curated.csv"
            exp_df.to_csv(curated_exp, index=False)

            for _, row in exp_df.iterrows():
                exp = Expense(
                    date=row["date"],
                    category=row.get("category") or "outros",
                    description=row.get("description") or "",
                    amount=float(row["amount"]),
                )
                session.add(exp)

        session.commit()
        print("✅ ETL concluído com sucesso.")
    finally:
        session.close()
