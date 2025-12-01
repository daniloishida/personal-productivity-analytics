# app/main.py
import argparse
from .etl import run_etl
from .report import generate_daily_report
from .analytics import show_productivity_summary, show_finance_summary
from .add_data import add_task, add_timelog, add_expense


def main():
    parser = argparse.ArgumentParser(description="Personal Productivity Analytics CLI")

    subparsers = parser.add_subparsers(dest="command")

    # ETL
    subparsers.add_parser("etl", help="Executa o pipeline ETL")

    # PROD
    prod_parser = subparsers.add_parser("prod", help="Mostra resumo de produtividade")
    prod_parser.add_argument(
        "--period",
        choices=["today", "7d", "30d", "all"],
        default="7d",
        help="Período para análise"
    )

    # FIN
    fin_parser = subparsers.add_parser("fin", help="Mostra resumo financeiro")
    fin_parser.add_argument(
        "--period",
        choices=["today", "7d", "30d", "all"],
        default="30d",
        help="Período para análise"
    )

    # REPORT
    report_parser = subparsers.add_parser("report", help="Gera relatório completo")
    report_parser.add_argument(
        "--period",
        choices=["today", "7d", "30d", "all"],
        default="30d",
        help="Período para análise"
    )

    # ADD
    add_parser = subparsers.add_parser("add", help="Adicionar dados aos CSVs")
    add_parser.add_argument(
        "type",
        choices=["task", "timelog", "expense"],
        help="Tipo de dado para adicionar"
    )

    args = parser.parse_args()

    if args.command == "etl":
        run_etl()

    elif args.command == "prod":
        show_productivity_summary(period=args.period)

    elif args.command == "fin":
        show_finance_summary(period=args.period)

    elif args.command == "report":
        generate_daily_report(period=args.period)

    elif args.command == "add":
        if args.type == "task":
            add_task()
        elif args.type == "timelog":
            add_timelog()
        elif args.type == "expense":
            add_expense()
        else:
            print("Tipo inválido.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
