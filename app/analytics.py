# app/analytics.py
from datetime import datetime, timedelta
from tabulate import tabulate
from sqlalchemy import func

from .models import SessionLocal, Task, TimeLog, Expense


def _period_filter(query, model_datetime_field, period: str):
    """
    Aplica filtro de período, com suporte para ALL = sem filtro.
    """
    if period == "all":
        return query

    now = datetime.now()

    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    elif period == "7d":
        start = now - timedelta(days=7)

    elif period == "30d":
        start = now - timedelta(days=30)

    else:
        # fallback: não filtra
        return query

    return query.filter(model_datetime_field >= start)


# =====================================================
# PRODUTIVIDADE
# =====================================================
def show_productivity_summary(period="7d"):
    session = SessionLocal()

    print("\n📌 Resumo de produtividade")

    # tarefas
    q_tasks = session.query(Task)
    q_tasks = _period_filter(q_tasks, Task.completed_at, period)
    tasks_count = q_tasks.count()

    # tempo registrado
    q_tl = session.query(TimeLog)
    q_tl = _period_filter(q_tl, TimeLog.started_at, period)

    total_minutes = sum(t.duration_minutes for t in q_tl.all())

    print(f"Tarefas concluídas: {tasks_count}")
    print(f"Tempo total registrado: {total_minutes / 60:.1f} horas")

    # detalhes por label
    logs = q_tl.all()
    if logs:
        grouped = {}
        for l in logs:
            grouped.setdefault(l.task_label, 0)
            grouped[l.task_label] += l.duration_minutes

        table = [[k, f"{v/60:.2f} h"] for k, v in grouped.items()]
        print("\nTempo por tipo de atividade:")
        print(tabulate(table, headers=["Atividade", "Horas"]))
    else:
        print("\nNenhum registro de tempo no período.")

    session.close()


# =====================================================
# FINANCEIRO
# =====================================================
def show_finance_summary(period="30d"):
    session = SessionLocal()

    print("\n💰 Resumo financeiro")

    q_exp = session.query(Expense)
    q_exp = _period_filter(q_exp, Expense.date, period)

    expenses = q_exp.all()

    total = sum(e.amount for e in expenses)

    print(f"Gasto total: R$ {total:,.2f}")

    if expenses:
        grouped = {}
        for e in expenses:
            grouped.setdefault(e.category, 0)
            grouped[e.category] += e.amount

        table = [[cat, f"R$ {amt:,.2f}"] for cat, amt in grouped.items()]
        print("\nGasto por categoria:")
        print(tabulate(table, headers=["Categoria", "Total"]))
    else:
        print("\nNenhum gasto neste período.")

    session.close()
