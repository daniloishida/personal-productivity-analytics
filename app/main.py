# app/main.py
"""
CLI principal do projeto Personal Productivity Analytics.

Comandos disponíveis:

- etl
    Roda o pipeline ETL (lê CSVs, transforma e carrega no banco).

- report
    Gera relatório completo (produtividade + finanças + previsão) para um período.

- prod
    Gera somente o resumo de PRODUTIVIDADE para um período.

- fin
    Gera somente o resumo FINANCEIRO para um período.

- add-task
    Adiciona uma nova tarefa ao arquivo data/tasks.csv.

- add-expense
    Adiciona uma nova despesa ao arquivo data/finance.csv.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Literal

from .config import DATA_DIR
from .etl import run_etl

# Estes imports assumem que seu report.py já tem essas funções.
# Se os nomes estiverem diferentes, é só ajustar aqui.
from .report import (
    generate_daily_report,
    generate_productivity_summary,
    generate_finance_summary,
)


# ---------------------------------------------------------------------------
# Constantes / helpers
# ---------------------------------------------------------------------------

ALLOWED_PERIODS: tuple[str, ...] = ("today", "7d", "30d", "all")

TASK_CATEGORIES_PT = [
    "pessoal",
    "profissional",
    "saude",
    "estudos",
    "familia",
    "financeiro",
]

EXPENSE_CATEGORIES_PT = [
    "alimentacao",
    "transporte",
    "assinaturas",
    "mercado",
    "lazer",
    "saude",
    "outros",
]


def _ensure_tasks_csv(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["external_id", "title", "category", "completed_at", "duration_minutes"])


def _ensure_finance_csv(path: Path) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "category", "description", "amount"])


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

def cmd_etl(args: argparse.Namespace) -> None:
    """Roda o pipeline ETL completo."""
    run_etl()


def cmd_report(args: argparse.Namespace) -> None:
    """Relatório completo (prod + fin + previsão) para um período."""
    period: Literal["today", "7d", "30d", "all"] = args.period
    generate_daily_report(period=period)


def cmd_prod(args: argparse.Namespace) -> None:
    """Resumo de produtividade para um período."""
    period: Literal["today", "7d", "30d", "all"] = args.period
    generate_productivity_summary(period=period)


def cmd_fin(args: argparse.Namespace) -> None:
    """Resumo financeiro para um período."""
    period: Literal["today", "7d", "30d", "all"] = args.period
    generate_finance_summary(period=period)


def cmd_add_task(args: argparse.Namespace) -> None:
    """
    Adiciona uma nova tarefa ao arquivo CSV de tasks.

    Exemplo de uso:

    python -m app.main add-task \\
        --title "Estudar IA" \\
        --category estudos \\
        --minutes 50
    """
    tasks_csv = DATA_DIR / "tasks.csv"
    _ensure_tasks_csv(tasks_csv)

    title = args.title.strip()
    category = args.category.strip().lower()
    minutes = float(args.minutes)

    if category not in TASK_CATEGORIES_PT:
        print(f"[add-task] ⚠ Categoria '{category}' não está na lista padrão.")
        print(f"[add-task]   Categorias recomendadas: {', '.join(TASK_CATEGORIES_PT)}")

    # Se o usuário não informar completed_at, usamos agora
    if args.completed_at:
        completed_at_str = args.completed_at
    else:
        completed_at_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # external_id único usando timestamp (para não conflitar com o UNIQUE do banco)
    external_id = str(int(datetime.now().timestamp() * 1000))

    with tasks_csv.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([external_id, title, category, completed_at_str, minutes])

    print("[add-task] ✅ Tarefa adicionada ao CSV com sucesso:")
    print(f"           external_id={external_id}")
    print(f"           title={title}")
    print(f"           category={category}")
    print(f"           completed_at={completed_at_str}")
    print(f"           duration_minutes={minutes}")


def cmd_add_expense(args: argparse.Namespace) -> None:
    """
    Adiciona uma nova despesa ao arquivo CSV de finanças.

    Exemplo:

    python -m app.main add-expense \\
        --category mercado \\
        --description "Compra da semana" \\
        --amount 320.50
    """
    finance_csv = DATA_DIR / "finance.csv"
    _ensure_finance_csv(finance_csv)

    category = args.category.strip().lower()
    description = args.description.strip() if args.description else ""
    amount = float(args.amount)

    if category not in EXPENSE_CATEGORIES_PT:
        print(f"[add-expense] ⚠ Categoria '{category}' não está na lista padrão.")
        print(f"[add-expense]   Categorias recomendadas: {', '.join(EXPENSE_CATEGORIES_PT)}")

    # Se não informar data, usamos hoje
    if args.date:
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    with finance_csv.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date_str, category, description, amount])

    print("[add-expense] ✅ Despesa adicionada ao CSV com sucesso:")
    print(f"              date={date_str}")
    print(f"              category={category}")
    print(f"              description={description}")
    print(f"              amount={amount}")


# ---------------------------------------------------------------------------
# Parser de linha de comando
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="personal-analytics",
        description="CLI do projeto Personal Productivity Analytics",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # etl
    p_etl = subparsers.add_parser("etl", help="Roda o pipeline ETL (CSV -> DB)")
    p_etl.set_defaults(func=cmd_etl)

    # report
    p_report = subparsers.add_parser("report", help="Relatório completo (prod + fin + previsão)")
    p_report.add_argument(
        "--period",
        choices=ALLOWED_PERIODS,
        default="7d",
        help="Período a considerar (default: 7d)",
    )
    p_report.set_defaults(func=cmd_report)

    # prod
    p_prod = subparsers.add_parser("prod", help="Resumo de produtividade para um período")
    p_prod.add_argument(
        "--period",
        choices=ALLOWED_PERIODS,
        default="7d",
        help="Período a considerar (default: 7d)",
    )
    p_prod.set_defaults(func=cmd_prod)

    # fin
    p_fin = subparsers.add_parser("fin", help="Resumo financeiro para um período")
    p_fin.add_argument(
        "--period",
        choices=ALLOWED_PERIODS,
        default="30d",
        help="Período a considerar (default: 30d)",
    )
    p_fin.set_defaults(func=cmd_fin)

    # add-task
    p_add_task = subparsers.add_parser("add-task", help="Adiciona uma tarefa ao tasks.csv")
    p_add_task.add_argument("--title", required=True, help="Título/descrição da tarefa")
    p_add_task.add_argument(
        "--category",
        required=True,
        help=f"Categoria da tarefa (ex: estudos, pessoal, profissional...)",
    )
    p_add_task.add_argument(
        "--minutes",
        required=True,
        type=float,
        help="Duração em minutos",
    )
    p_add_task.add_argument(
        "--completed-at",
        required=False,
        help="Data/hora de conclusão (YYYY-MM-DD HH:MM:SS). Se omitido, usa agora.",
    )
    p_add_task.set_defaults(func=cmd_add_task)

    # add-expense
    p_add_expense = subparsers.add_parser("add-expense", help="Adiciona uma despesa ao finance.csv")
    p_add_expense.add_argument(
        "--category",
        required=True,
        help="Categoria da despesa (ex: mercado, alimentacao, lazer...)",
    )
    p_add_expense.add_argument(
        "--amount",
        required=True,
        type=float,
        help="Valor da despesa",
    )
    p_add_expense.add_argument(
        "--description",
        required=False,
        help="Descrição da despesa",
    )
    p_add_expense.add_argument(
        "--date",
        required=False,
        help="Data da despesa (YYYY-MM-DD). Se omitido, usa hoje.",
    )
    p_add_expense.set_defaults(func=cmd_add_expense)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
