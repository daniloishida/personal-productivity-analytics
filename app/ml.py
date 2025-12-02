# app/ml.py
"""
Módulo de Machine Learning para previsão de gastos mensais.

Agora sem scikit-learn nem scipy:
- usa apenas NumPy + Pandas
- modelo de regressão linear simples via np.polyfit

Fluxo:
- Lê as despesas da tabela Expense
- Agrega por mês
- Ajusta uma reta (y = a*x + b) nos pontos (mês_idx, gasto_mensal)
- Prevê o gasto do próximo mês
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .database import SessionLocal
from .models import Expense


@dataclass
class SpendingForecaster:
    """
    Classe responsável por carregar os dados de despesas
    e prever o gasto do próximo mês usando uma regressão linear simples.
    """

    def _load_data(self) -> pd.DataFrame:
        """
        Lê a tabela Expense e retorna um DataFrame com gasto mensal agregado.

        Colunas retornadas:
        - month (periodo mensal ex: 2025-01)
        - amount (soma de gastos no mês)
        - month_idx (0,1,2,...)
        """
        session = SessionLocal()
        try:
            rows = session.query(Expense.date, Expense.amount).all()
        finally:
            session.close()

        if not rows:
            raise ValueError("Nenhum dado de despesa encontrado para treinar o modelo.")

        df = pd.DataFrame(rows, columns=["date", "amount"])
        df["date"] = pd.to_datetime(df["date"])

        # período mensal
        df["month"] = df["date"].dt.to_period("M")

        monthly = (
            df.groupby("month")["amount"]
            .sum()
            .sort_index()
            .reset_index()
        )

        monthly["month_idx"] = np.arange(len(monthly))

        return monthly

    def predict_next_month(self) -> float:
        """
        Retorna a previsão de gasto para o próximo mês.

        Estratégia:
        - Se tiver apenas 1 mês de dados: retorna o próprio valor.
        - Se tiver 2+ meses:
            - usa np.polyfit para ajustar uma linha (grau 1)
            - prevê o valor para o próximo month_idx
        """
        monthly = self._load_data()

        # Caso com só um ponto: devolve o próprio valor
        if len(monthly) == 1:
            return float(monthly["amount"].iloc[0])

        x = monthly["month_idx"].to_numpy(dtype=float)
        y = monthly["amount"].to_numpy(dtype=float)

        # np.polyfit retorna coeficientes [a, b] da reta y = a*x + b
        a, b = np.polyfit(x, y, 1)

        next_idx = float(monthly["month_idx"].iloc[-1] + 1)
        next_value = a * next_idx + b

        # Segurança: não deixar valor negativo
        return float(max(next_value, 0.0))
