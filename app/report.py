# app/report.py
"""
Geração de relatórios em texto para a CLI.

Usa as funções do módulo analytics:
- get_productivity_summary
- get_finance_summary
- get_monthly_forecast

Agora com métricas de agilidade:
- throughput (tasks/dia)
- horas focadas por dia
- tempo médio por tarefa
- categoria com maior foco
"""

from __future__ import annotations

from typing import Literal

from .analytics import (
    get_productivity_summary,
    get_finance_summary,
    get_monthly_forecast,
    _get_date_limit,  # usamos para calcular período real
)
from .database import SessionLocal
from .models import Task

PeriodType = Literal["today", "7d", "30d", "all"]


def _label_period(period: PeriodType) -> str:
    if period == "today":
        return "hoje"
    if period == "7d":
        return "últimos 7 dias"
    if period == "30d":
        return "últimos 30 dias"
    if period == "all":
        return "todo o histórico"
    return period


def _compute_days_in_period(period: PeriodType) -> int:
    """
    Calcula quantos dias existem de fato no recorte usado para tasks,
    com base em completed_at no banco.

    - Para today / 7d / 30d, usa a data limite do _get_date_limit
    - Para all, pega do primeiro completed_at até o último

    Sempre retorna pelo menos 1.
    """
    session = SessionLocal()
    try:
        q = session.query(Task.completed_at).filter(Task.completed_at.isnot(None))
        date_limit = _get_date_limit(period)

        if date_limit:
            q = q.filter(Task.completed_at >= date_limit)

        dates = [row[0] for row in q.all()]
    finally:
        session.close()

    if not dates:
        return 1

    min_date = min(dates)
    max_date = max(dates)
    days = (max_date.date() - min_date.date()).days + 1
    return max(days, 1)


# -------------------------------------------------------------------------
# Relatórios específicos
# -------------------------------------------------------------------------

def generate_productivity_summary(period: PeriodType = "7d") -> None:
    """Gera e imprime o resumo de produtividade + métricas de agilidade."""
    label = _label_period(period)
    summary = get_productivity_summary(period)

    total_tasks = summary["tasks"]
    total_minutes = summary["minutes"]
    total_hours = round(total_minutes / 60, 2) if total_minutes else 0.0

    # Métricas de agilidade
    days = _compute_days_in_period(period)
    throughput_per_day = round(total_tasks / days, 2) if days else 0.0
    avg_minutes = round(total_minutes / total_tasks, 2) if total_tasks else 0.0
    avg_hours = round(avg_minutes / 60, 2) if avg_minutes else 0.0
    focus_hours_per_day = round(total_hours / days, 2) if days else 0.0

    # Categoria com maior foco (por minutos)
    top_category = None
    top_category_hours = 0.0
    if summary["by_category"]:
        cat, mins = max(summary["by_category"].items(), key=lambda x: x[1])
        top_category = cat
        top_category_hours = round((mins or 0) / 60, 2)

    print("\n📌 Resumo de Produtividade")
    print(f"Período considerado: {label}")
    print(f"Tarefas concluídas: {total_tasks}")
    print(f"Tempo total registrado: {total_hours} horas\n")

    # Bloco de métricas de agilidade
    print("⚙️ Métricas de Agilidade (derivadas das tasks)")
    print(f"- Dias considerados no período: {days} dia(s)")
    print(f"- 🚀 Throughput (tasks/dia): {throughput_per_day}")
    print(f"- ⏱️ Tempo médio por tarefa: {avg_minutes} min ({avg_hours} h)")
    print(f"- 🔥 Horas focadas por dia: {focus_hours_per_day} h/dia")
    if top_category is not None:
        print(
            f"- 🎯 Categoria com maior foco: '{top_category}' "
            f"({top_category_hours} h acumuladas no período)"
        )
    print("")

    # Tabela por categoria
    if not summary["by_category"]:
        print("Nenhuma tarefa registrada no período.\n")
        return

    print("Tempo por tipo de atividade (visão por categoria):")
    print(f"{'Atividade':<15} {'Horas':>10} {'% do total':>12}")
    print(f"{'-'*15} {'-'*10} {'-'*12}")

    for category, minutes in summary["by_category"].items():
        hours = round(minutes / 60, 2)
        perc = (minutes / total_minutes * 100) if total_minutes else 0.0
        print(f"{category:<15} {hours:>8.2f} h {perc:>10.1f}%")

    print("")


def generate_finance_summary(period: PeriodType = "30d") -> None:
    """Gera e imprime o resumo financeiro apenas."""
    label = _label_period(period)
    summary = get_finance_summary(period)

    total_spent = summary["total"]

    print("\n💰 Resumo Financeiro")
    print(f"Período considerado: {label}")
    print(f"Gasto total: R$ {total_spent:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    if not summary["by_category"]:
        print("\nNenhuma despesa registrada no período.\n")
        return

    print("\nGasto por categoria:")
    print(f"{'Categoria':<15} {'Total':>15} {'% do total':>12}")
    print(f"{'-'*15} {'-'*15} {'-'*12}")

    for category, amount in summary["by_category"].items():
        perc = (amount / total_spent * 100) if total_spent else 0.0
        formatted = f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"{category:<15} {formatted:>15} {perc:>10.1f}%")

    print("")


# -------------------------------------------------------------------------
# Relatório completo (prod + fin + previsão)
# -------------------------------------------------------------------------

def generate_daily_report(period: PeriodType = "7d") -> None:
    """
    Gera relatório completo:
    - produtividade + métricas de agilidade
    - finanças
    - previsão de gasto do próximo mês
    """
    print("========== PERSONAL PRODUCTIVITY ANALYTICS ==========\n")

    # Produtividade + agilidade
    generate_productivity_summary(period=period)

    # Financeiro (se período for "today", usar pelo menos 30d para finanças)
    fin_period: PeriodType = period if period != "today" else "30d"
    generate_finance_summary(period=fin_period)

    # Previsão
    forecast = get_monthly_forecast()
    formatted_forecast = f"R$ {forecast:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    print(f"\n📈 Previsão de gasto para o próximo mês: {formatted_forecast}\n")
