"""
Подключение к базе данных.
Локально по умолчанию — SQLite (файл sk_app.db рядом с проектом).
На хостинге (напр. Render) переменная окружения DATABASE_URL укажет на
настоящую PostgreSQL — тогда используется она.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./sk_app.db")

# Render (и некоторые другие хостинги) отдают строку вида "postgres://",
# а современный SQLAlchemy требует "postgresql://" — поправляем на лету.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Используем современный драйвер psycopg (v3) вместо psycopg2 — он собирается
# без проблем на новых версиях Python, включая 3.13+.
if DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
