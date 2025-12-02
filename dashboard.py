# dashboard.py
"""
Dashboard Streamlit do Personal Productivity Analytics.

Mostra:
- Métricas de agilidade (throughput, horas focadas, tempo médio por tarefa)
- Distribuição por categoria
- Série temporal de tarefas concluídas
- Resumo financeiro por categoria
- Previsão de gastos (se houver dados suficientes)
"""

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from sqlalchemy import text

from app.database import engine
from app.analytics import (
    get_productivity_summary,
    get_finance_summary,
    get_monthly_forecast,
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def load_tasks_df(period: str) -> pd.DataFrame:
    """
    Carrega tasks do banco como DataFrame, filtrando pelo período.
    period: "today", "7d", "30d", "all"
    """
    base_query = "SELECT id, external_id, title, category, completed_at, duration_minutes FROM tasks"
    params = {}

    now = datetime.now()

    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        base_query += " WHERE completed_at >= :start"
        params["start"] = start
    elif period == "7d":
        start = now - timedelta(days=7)
        base_query += " WHERE completed_at >= :start"
        params["start"] = start
    elif period == "30d":
        start = now - timedelta(days=30)
        base_query += " WHERE completed_at >= :start"
        params["start"] = start
    # "all" não filtra

    with engine.connect() as conn:
        df = pd.read_sql(text(base_query), conn, params=params or None)

    if not df.empty and "completed_at" in df.columns:
        df["completed_at"] = pd.to_datetime(df["completed_at"])

    return df


def load_expenses_df(period: str) -> pd.DataFrame:
    """
    Carrega expenses do banco como DataFrame, filtrando pelo período.
    """
    base_query = "SELECT id, date, category, description, amount FROM expenses"
    params = {}
    now = datetime.now()

    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        base_query += " WHERE date >= :start"
        params["start"] = start
    elif period == "7d":
        start = now - timedelta(days=7)
        base_query += " WHERE date >= :start"
        params["start"] = start
    elif period == "30d":
        start = now - timedelta(days=30)
        base_query += " WHERE date >= :start"
        params["start"] = start

    with engine.connect() as conn:
        df = pd.read_sql(text(base_query), conn, params=params or None)

    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    return df


# ---------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Personal Productivity Analytics",
    layout="wide",
)

st.title("📊 Personal Productivity Analytics")
st.caption("Métricas de produtividade + finanças com foco em agilidade")


# Sidebar - filtro de período
period = st.sidebar.selectbox(
    "Período",
    options=["today", "7d", "30d", "all"],
    format_func=lambda p: {
        "today": "Hoje",
        "7d": "Últimos 7 dias",
        "30d": "Últimos 30 dias",
        "all": "Todo o histórico",
    }[p],
    index=3,
)

st.sidebar.markdown("---")
st.sidebar.write("💡 Dica: use `all` para ver a base inteira.")


# ---------------------------------------------------------------------
# Seção 1: Métricas de Agilidade (Produtividade)
# ---------------------------------------------------------------------

st.header("⚙️ Métricas de Agilidade (Tasks)")

tasks_df = load_tasks_df(period)
prod_summary = get_productivity_summary(period)

total_tasks = prod_summary["tasks"]
total_minutes = prod_summary["minutes"]
total_hours = round(total_minutes / 60, 2) if total_minutes else 0

avg_minutes = round(total_minutes / total_tasks, 2) if total_tasks else 0
avg_hours = round(avg_minutes / 60, 2) if avg_minutes else 0

# Throughput: tasks por dia (no período)
if period == "today":
    days = 1
elif period == "7d":
    days = 7
elif period == "30d":
    days = 30
else:
    # all: calcular pelo delta entre min e max completed_at
    if not tasks_df.empty:
        delta_days = (tasks_df["completed_at"].max() - tasks_df["completed_at"].min()).days
        days = max(delta_days, 1)
    else:
        days = 1

throughput_per_day = round(total_tasks / days, 2) if days else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📌 Tasks concluídas", f"{total_tasks}")
col2.metric("⏱️ Horas focadas (total)", f"{total_hours} h")
col3.metric("🧠 Tempo médio por task", f"{avg_minutes} min ({avg_hours} h)")
col4.metric("🚀 Throughput (tasks/dia)", f"{throughput_per_day}")

# Distribuição por categoria (horas)
if prod_summary["by_category"]:
    cat_df = (
        pd.DataFrame(
            [
                {"category": cat, "minutes": mins, "hours": round(mins / 60, 2)}
                for cat, mins in prod_summary["by_category"].items()
            ]
        )
        .sort_values("hours", ascending=False)
    )

    st.subheader("📂 Tempo por categoria (horas)")
    st.dataframe(cat_df, use_container_width=True)

    st.bar_chart(
        cat_df.set_index("category")["hours"],
        use_container_width=True,
    )
else:
    st.info("Nenhuma task encontrada no período selecionado.")

# Série temporal de tasks por dia
if not tasks_df.empty:
    # cria uma coluna "day" com apenas a data (sem hora)
    daily = tasks_df.copy()
    daily["day"] = daily["completed_at"].dt.date

    # conta quantas tasks por dia
    daily = (
        daily.groupby("day")["id"]
        .count()
        .reset_index(name="tasks")
    )

    # converte para datetime e usa como índice
    daily["date"] = pd.to_datetime(daily["day"])
    daily = daily.set_index("date")[["tasks"]]

    st.subheader("📈 Tasks concluídas por dia")
    st.line_chart(daily, width="stretch")
else:
    st.info("Ainda não há dados suficientes para série temporal de tasks.")


# ---------------------------------------------------------------------
# Seção 2: Métricas Financeiras
# ---------------------------------------------------------------------

st.header("💰 Métricas Financeiras")

fin_summary = get_finance_summary(period)
total_spent = fin_summary["total"]

colf1, colf2 = st.columns(2)
colf1.metric(
    "💵 Gasto total no período",
    f"R$ {total_spent:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
)

try:
    forecast = get_monthly_forecast()
    colf2.metric(
        "📈 Previsão próximo mês",
        f"R$ {forecast:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    )
except Exception as e:
    colf2.metric("📈 Previsão próximo mês", "Indisponível")
    st.warning(f"Erro ao calcular previsão: {e}")

if fin_summary["by_category"]:
    fin_cat_df = (
        pd.DataFrame(
            [
                {"category": cat, "amount": amt}
                for cat, amt in fin_summary["by_category"].items()
            ]
        )
        .sort_values("amount", ascending=False)
    )

    fin_cat_df["amount_fmt"] = fin_cat_df["amount"].apply(
        lambda v: f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.subheader("📂 Gasto por categoria")
    st.dataframe(fin_cat_df[["category", "amount_fmt"]], use_container_width=True)

    st.bar_chart(
        fin_cat_df.set_index("category")["amount"],
        use_container_width=True,
    )
else:
    st.info("Nenhuma despesa encontrada no período selecionado.")
