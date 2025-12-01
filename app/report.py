# app/report.py
from .analytics import show_productivity_summary, show_finance_summary
from .ml import SpendingForecaster


def generate_daily_report(period: str = "30d"):
    """
    Gera um relatório consolidado de produtividade + finanças + previsão de gastos.

    O parâmetro `period` é repassado para as funções de analytics:
    - "today", "7d", "30d", "all"
    """
    print("========== PERSONAL PRODUCTIVITY ANALYTICS ==========\n")

    # Produtividade
    show_productivity_summary(period=period)

    # Finanças
    show_finance_summary(period=period)

    # Previsão de gastos (usando todo o histórico disponível)
    try:
        forecaster = SpendingForecaster()
        forecaster.train()
        predicted = forecaster.forecast_next_month()
        print(f"\n📈 Previsão de gasto para o próximo mês: R$ {predicted:,.2f}")
    except RuntimeError as e:
        print(f"\n📈 Ainda não é possível prever gasto: {e}")
