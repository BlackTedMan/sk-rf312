import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
)
from sqlalchemy.orm import relationship

from .database import Base


class CaseStatus(str, enum.Enum):
    IN_PROGRESS = "в_расследовании"
    CLOSED = "закончено"


class Department(Base):
    """Отдел фракции: УПРДЛ, УСБ, УПК, УПОВД, ООСБ, ФГГС, УК, Руководство и т.д."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)   # короткий код, напр. "УПРДЛ"
    name = Column(String(255), nullable=False)                # полное название

    categories = relationship("CaseCategory", back_populates="department", cascade="all, delete-orphan")
    users = relationship("User", back_populates="department")


class CaseCategory(Base):
    """Категория дел внутри отдела (напр. 'особо важные дела', 'коррупционные дела')."""
    __tablename__ = "case_categories"

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name = Column(String(255), nullable=False)
    is_archive = Column(Boolean, default=False)  # категория-архив (закрытые дела складываются сюда логически по статусу)

    department = relationship("Department", back_populates="categories")
    cases = relationship("Case", back_populates="category")


class User(Base):
    """Игрок: логин, ФИО, должность, отдел."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    full_name = Column(String(255), nullable=False)   # ФИО
    position = Column(String(255), nullable=False)     # должность (напр. "Следователь УПРДЛ")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    discord_id = Column(String(50), nullable=True)     # для сверки с Discord-ботом
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="users")
    cases = relationship("Case", back_populates="investigator", foreign_keys="Case.investigator_id")
    activity_logs = relationship("ActivityLog", back_populates="user")


class Case(Base):
    """Дело."""
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)       # номер дела
    article = Column(String(255), nullable=False)                    # статья УК РФ
    suspects = Column(Text, nullable=True)                           # фигуранты/обвиняемые
    complainant = Column(Text, nullable=True)                        # потерпевший/заявитель
    outcome = Column(Text, nullable=True)                            # итог дела

    category_id = Column(Integer, ForeignKey("case_categories.id"), nullable=False)
    investigator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(SAEnum(CaseStatus), default=CaseStatus.IN_PROGRESS, nullable=False)

    open_date = Column(DateTime, default=datetime.utcnow)
    close_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("CaseCategory", back_populates="cases")
    investigator = relationship("User", back_populates="cases", foreign_keys=[investigator_id])
    evidence = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")


class Evidence(Base):
    """Доказательство/приложение к делу — файл или ссылка."""
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    title = Column(String(255), nullable=True)
    url_or_path = Column(String(500), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="evidence")


class ActivityLog(Base):
    """Лог активности игрока — используется для расчёта характеристики."""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)   # login, case_created, case_updated, case_closed...
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_logs")
