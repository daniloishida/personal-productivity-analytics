# app/models.py
"""
Modelos ORM do projeto Personal Productivity Analytics.

Tabelas principais:
- Task: registra atividades de produtividade (tarefas, tempo, categoria).
- Expense: registra despesas financeiras (data, categoria, valor).
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Task(Base):
    """
    Representa uma tarefa concluída, usada para análise de produtividade.

    Campos:
    - external_id: id externo vindo do CSV ou de outra fonte
    - title: nome ou descrição da tarefa
    - category: categoria (pessoal, profissional, estudos, etc.)
    - completed_at: data/hora de conclusão
    - duration_minutes: duração estimada/em minutos
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    duration_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("external_id", name="uq_tasks_external_id"),
        Index("ix_tasks_category_completed_at", "category", "completed_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Task id={self.id} external_id={self.external_id!r} "
            f"title={self.title!r} category={self.category!r} "
            f"completed_at={self.completed_at!r} duration={self.duration_minutes}>"
        )


class Expense(Base):
    """
    Representa uma despesa financeira.

    Campos:
    - date: data da despesa
    - category: categoria (alimentacao, mercado, lazer, etc.)
    - description: texto livre descrevendo a despesa
    - amount: valor em moeda
    """

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("ix_expenses_category_date", "category", "date"),
    )

    def __repr__(self) -> str:
        return (
            f"<Expense id={self.id} date={self.date!r} category={self.category!r} "
            f"amount={self.amount} description={self.description!r}>"
        )
