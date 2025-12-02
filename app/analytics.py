# app/analytics.py
"""
Funções de análise (produção e finanças)
Usadas por report.py e pela CLI.
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from .database import SessionLocal
from .models import Task, Expense


# -------------------------------------------------------------------------
# Helpers de período
# -------------------------------------------------------------------------

def _get_date_limit(period: str) -> datetime | None:
    """
    Retorna a data limite para filtragem.
    period pode ser: "today", "7d", "30d", "all"
    """
    now = datetime.now()

    if period == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "7d":
        return now - timedelta(days=7)
    elif period == "30d":
        return now - timedelta(days=30)
    elif period == "all":
        return None
    else:
        raise ValueError(f"Período inválido: {period}")


# -------------------------------------------------------------------------
# PRODUTIVIDADE
# -------------------------------------------------------------------------

def get_productivity_summary(period: str):
    """
    Retorna:
      - número de tasks concluídas
      - total de minutos
      - soma por categoria
    """
    session = SessionLocal()
    date_limit = _get_date_limit(period)

    q = session.query(Task)

    if date_limit:
        q = q.filter(Task.completed_at >= date_limit)

    total_tasks = q.count()

    total_minutes = q.with_entities(func.sum(Task.duration_minutes)).scalar() or 0

    # agrupamento por categoria
    category_rows = (
        q.with_entities(Task.category, func.sum(Task.duration_minutes))
        .group_by(Task.category)
        .all()
    )

    category_summary = {
        cat: float(minutes or 0)
        for cat, minutes in category_rows
    }

    session.close()

    return {
        "tasks": total_tasks,
        "minutes": total_minutes,
        "by_category": category_summary,
    }


# -------------------------------------------------------------------------
# FINANÇAS
# -------------------------------------------------------------------------

def get_finance_summary(period: str):
    """
    Retorna:
      - total gasto
      - gasto por categoria
    """
    session = SessionLocal()
    date_limit = _get_date_limit(period)

    q = session.query(Expense)

    if date_limit:
        q = q.filter(Expense.date >= date_limit)

    total_spent = q.with_entities(func.sum(Expense.amount)).scalar() or 0

    # agrupamento por categoria
    category_rows = (
        q.with_entities(Expense.category, func.sum(Expense.amount))
        .group_by(Expense.category)
        .all()
    )

    category_summary = {
        cat: float(amount or 0)
        for cat, amount in category_rows
    }

    session.close()

    return {
        "total": total_spent,
        "by_category": category_summary,
    }


# -------------------------------------------------------------------------
# PREVISÃO (ML)
# -------------------------------------------------------------------------

def get_monthly_forecast():
    """
    Retorna um valor de previsão usando o ml.py (modelo Linear Regression)
    """
    try:
        from .ml import SpendingForecaster
        forecast = SpendingForecaster().predict_next_month()
        return float(forecast)
    except Exception as e:
        print("[analytics] ⚠ Erro ao calcular previsão:", e)
        return 0.0
