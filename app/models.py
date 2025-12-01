# app/models.py
from sqlalchemy import (
    Column, Integer, Float, String, DateTime, create_engine, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from .config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    external_id = Column(String, index=True, unique=True)
    title = Column(String, nullable=False)
    category = Column(String, index=True)  # ex: trabalho, estudo, pessoal
    completed_at = Column(DateTime, index=True)
    duration_minutes = Column(Integer)     # se houver estimativa/duração

    def __repr__(self):
        return f"<Task {self.title} ({self.category})>"


class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True)
    task_label = Column(String, index=True)    # ex: deep work, reunião
    project = Column(String, index=True)
    started_at = Column(DateTime, index=True)
    ended_at = Column(DateTime, index=True)
    duration_minutes = Column(Integer)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)
    category = Column(String, index=True)  # ex: alimentação, transporte
    description = Column(String)
    amount = Column(Float)


def init_db():
    Base.metadata.create_all(bind=engine)
