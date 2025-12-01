# dashboard.py
import pandas as pd
import streamlit as st

from app.models import init_db, engine, Task, TimeLog, Expense

# Garante que o banco/tabelas existem
init_db()


def load_tasks():
    # Usa o nome real da tabela a partir do modelo
    return pd.read_sql_table(Task.__tablename__, engine)


def load_timelog():
    return pd.read_sql_table(TimeLog.__tablename__, engine)


def load_expenses():
    return pd.read_sql_table(Expense.__tablename__, engine)


st.set_page_config(page_title="Personal Productivity Analytics", layout="wide")

st.title("📊 Personal Productivity Analytics Dashboard")

tab1, tab2, tab3 = st.tabs(["Produtividade", "Time Log", "Financeiro"])

# -------------------------------------------------
# PRODUTIVIDADE
# -------------------------------------------------
with tab1:
    st.header("Produtividade (Tasks)")
    try:
        tasks_df = load_tasks()
        if not tasks_df.empty:
            tasks_df["completed_at"] = pd.to_datetime(tasks_df["completed_at"])
            tasks_df["date"] = tasks_df["completed_at"].dt.date

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de tarefas", len(tasks_df))
            with col2:
                st.metric(
                    "Duração média (min)",
                    f"{tasks_df['duration_minutes'].mean():.1f}",
                )

            st.subheader("Últimas tarefas")
            st.dataframe(
                tasks_df[
                    ["id", "title", "category", "completed_at", "duration_minutes"]
                ].tail(20)
            )

            st.subheader("Tarefas por categoria")
            cat_counts = (
                tasks_df.groupby("category")["id"].count().reset_index(name="count")
            )
            st.bar_chart(cat_counts.set_index("category"))

        else:
            st.info("Nenhuma task encontrada no banco.")
    except Exception as e:
        st.error(f"Erro ao carregar tasks: {e}")

# -------------------------------------------------
# TIME LOG
# -------------------------------------------------
with tab2:
    st.header("Time Log")
    try:
        tl_df = load_timelog()
        if not tl_df.empty:
            tl_df["started_at"] = pd.to_datetime(tl_df["started_at"])
            tl_df["date"] = tl_df["started_at"].dt.date

            st.subheader("Últimos registros de tempo")
            st.dataframe(
                tl_df[
                    [
                        "id",
                        "task_label",
                        "project",
                        "started_at",
                        "ended_at",
                        "duration_minutes",
                    ]
                ].tail(20)
            )

            st.subheader("Horas por atividade")
            agg = tl_df.groupby("task_label")["duration_minutes"].sum() / 60.0
            st.bar_chart(agg)
        else:
            st.info("Nenhum time log encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar time logs: {e}")

# -------------------------------------------------
# FINANCEIRO
# -------------------------------------------------
with tab3:
    st.header("Financeiro (Despesas)")
    try:
        exp_df = load_expenses()
        if not exp_df.empty:
            exp_df["date"] = pd.to_datetime(exp_df["date"])
            exp_df["dia"] = exp_df["date"].dt.date

            st.subheader("Últimas despesas")
            st.dataframe(
                exp_df[["id", "date", "category", "description", "amount"]].tail(20)
            )

            st.subheader("Gasto por categoria")
            cat_sum = exp_df.groupby("category")["amount"].sum()
            st.bar_chart(cat_sum)

            st.subheader("Gasto diário")
            daily = exp_df.groupby("dia")["amount"].sum()
            st.line_chart(daily)
        else:
            st.info("Nenhuma despesa encontrada.")
    except Exception as e:
        st.error(f"Erro ao carregar despesas: {e}")
