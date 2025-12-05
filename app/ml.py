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
from typing import Dict, Iterable, Protocol

import numpy as np
import pandas as pd

from .database import SessionLocal
from .models import Expense


class SpendingModel(Protocol):
    """Interface de modelos de previsão de gastos."""

    name: str
    min_points: int

    def predict(self, monthly: pd.DataFrame) -> float:  # pragma: no cover - protocolo simples
        ...


@dataclass
class LinearTrendModel:
    """Regressão linear simples (y = a*x + b) com NumPy."""

    name: str = "linear_trend"
    min_points: int = 2

    def predict(self, monthly: pd.DataFrame) -> float:
        if len(monthly) == 1:
            return float(monthly["amount"].iloc[0])

        x = monthly["month_idx"].to_numpy(dtype=float)
        y = monthly["amount"].to_numpy(dtype=float)

        a, b = np.polyfit(x, y, 1)
        next_idx = float(monthly["month_idx"].iloc[-1] + 1)
        next_value = a * next_idx + b

        return float(max(next_value, 0.0))


@dataclass
class MovingAverageModel:
    """Média móvel simples usando a janela mais recente."""

    window: int = 3
    name: str = "moving_average"
    min_points: int = 1

    def predict(self, monthly: pd.DataFrame) -> float:
        effective_window = min(self.window, len(monthly))
        recent_values = monthly["amount"].tail(effective_window)
        return float(recent_values.mean())


@dataclass
class MedianGrowthModel:
    """Projeta crescimento pela mediana das variações mensais."""

    name: str = "median_growth"
    min_points: int = 2

    def predict(self, monthly: pd.DataFrame) -> float:
        deltas = monthly["amount"].diff().dropna()
        median_delta = float(deltas.median()) if not deltas.empty else 0.0
        next_value = float(monthly["amount"].iloc[-1]) + median_delta
        return float(max(next_value, 0.0))


@dataclass
class SpendingForecaster:
    """
    Camada de orquestração para múltiplos modelos de previsão de gastos.

    Por padrão expõe três modelos leves (NumPy/Pandas):
    - Regressão linear simples (tendência)
    - Média móvel (baseline estável)
    - Crescimento pela mediana das variações
    """

    models: Iterable[SpendingModel] = (
        LinearTrendModel(),
        MovingAverageModel(window=3),
        MedianGrowthModel(),
    )

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

    def _get_model(self, name: str) -> SpendingModel:
        for model in self.models:
            if model.name == name:
                return model
        raise ValueError(
            f"Modelo '{name}' não encontrado. Disponíveis: {[m.name for m in self.models]}"
        )

    def predict_next_month(self, model: str | None = None) -> float:
        """
        Retorna a previsão de gasto para o próximo mês usando o modelo escolhido.

        - model=None: usa o primeiro modelo que tenha dados suficientes (ordem em `models`).
        - model="linear_trend" | "moving_average" | "median_growth": força um modelo específico.
        """
        monthly = self._load_data()

        if model:
            selected = self._get_model(model)
            if len(monthly) < selected.min_points:
                raise ValueError(
                    f"Modelo '{model}' requer pelo menos {selected.min_points} meses de dados."
                )
            return float(selected.predict(monthly))

        for candidate in self.models:
            if len(monthly) >= candidate.min_points:
                return float(candidate.predict(monthly))

        # Se a lista de modelos estiver vazia (caso extremo), devolve último valor
        return float(monthly["amount"].iloc[-1])

    def predict_all(self) -> Dict[str, float]:
        """Retorna as previsões de todos os modelos registrados."""
        monthly = self._load_data()
        results: Dict[str, float] = {}
        for model in self.models:
            if len(monthly) >= model.min_points:
                results[model.name] = float(model.predict(monthly))
        return results
