# app/ml.py
from datetime import datetime, timedelta

import numpy as np
from sqlalchemy import func

from .models import SessionLocal, Expense


class SpendingForecaster:
    """
    Modelo simples para prever gasto do próximo mês com base em alguns meses anteriores.
    Em vez de usar scikit-learn, implementamos uma regressão linear simples com NumPy.

    Ideia:
    - Coleta o total de gastos por mês (últimos N meses)
    - Ajusta uma reta y = a*x + b
    - Usa o próximo ponto no eixo x para prever o valor futuro
    """

    def __init__(self, months_back: int = 6):
        self.months_back = months_back
        self.coef_ = None
        self.intercept_ = None
        self.trained = False
        self._n_points = 0

    def _load_data(self):
        """
        Carrega o total de gastos por mês (últimos N meses).
        Retorna X (índices de tempo) e y (gasto total daquele mês).
        """
        session = SessionLocal()
        try:
            now = datetime.now()
            totals = []

            # vamos pegar months_back meses para trás
            for i in range(self.months_back, 0, -1):
                # início aproximado de cada "janela" mensal
                start = (now.replace(day=1) - timedelta(days=30 * i))
                end = start + timedelta(days=30)

                q = (
                    session.query(func.sum(Expense.amount))
                    .filter(Expense.date >= start)
                    .filter(Expense.date < end)
                )
                total = q.scalar() or 0.0
                totals.append(total)
        finally:
            session.close()

        # precisamos de pelo menos 2 pontos pra ajustar uma reta
        if len(totals) < 2:
            raise RuntimeError("Dados insuficientes para treinar o modelo de gastos.")

        X = np.arange(len(totals)).astype(float)  # [0, 1, 2, ..., n-1]
        y = np.array(totals, dtype=float)
        self._n_points = len(totals)
        return X, y

    def train(self):
        """
        Ajusta uma regressão linear simples y = a*x + b usando fórmula fechada.
        """
        X, y = self._load_data()

        # regressão linear simples
        x_mean = X.mean()
        y_mean = y.mean()

        # coeficiente angular (a)
        num = ((X - x_mean) * (y - y_mean)).sum()
        den = ((X - x_mean) ** 2).sum()
        if den == 0:
            # se der algum caso degenerado, assume linha horizontal
            a = 0.0
        else:
            a = num / den

        # intercepto (b)
        b = y_mean - a * x_mean

        self.coef_ = float(a)
        self.intercept_ = float(b)
        self.trained = True

    def forecast_next_month(self) -> float:
        """
        Faz a previsão para o "próximo" mês, ou seja, para x = n (se temos n pontos históricos).
        """
        if not self.trained:
            self.train()

        next_x = float(self._n_points)  # se temos pontos 0..n-1, o próximo é n
        y_pred = self.coef_ * next_x + self.intercept_
        # Evita valores negativos se houver muita oscilação
        return max(0.0, float(y_pred))
