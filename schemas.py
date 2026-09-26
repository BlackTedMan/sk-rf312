from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .models import CaseStatus


# ---------- Department / Category ----------

class DepartmentOut(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class CaseCategoryOut(BaseModel):
    id: int
    department_id: int
    name: str
    is_archive: bool

    class Config:
        from_attributes = True


class CaseCategoryCreate(BaseModel):
    department_id: int
    name: str
    is_archive: bool = False


# ---------- Auth / User ----------

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str          # ФИО
    position: str            # должность
    department_id: int
    discord_id: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    position: str
    department_id: int
    discord_id: Optional[str] = None
    is_admin: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Case ----------

class CaseCreate(BaseModel):
    number: str
    article: str
    suspects: Optional[str] = None
    complainant: Optional[str] = None
    category_id: int
    investigator_id: Optional[int] = None   # если не указан — назначается создатель


class CaseUpdate(BaseModel):
    article: Optional[str] = None
    suspects: Optional[str] = None
    complainant: Optional[str] = None
    outcome: Optional[str] = None
    investigator_id: Optional[int] = None
    category_id: Optional[int] = None


class CaseClose(BaseModel):
    outcome: str


class EvidenceCreate(BaseModel):
    title: Optional[str] = None
    url_or_path: str


class EvidenceOut(BaseModel):
    id: int
    title: Optional[str]
    url_or_path: str
    added_at: datetime

    class Config:
        from_attributes = True


class CaseOut(BaseModel):
    id: int
    number: str
    article: str
    suspects: Optional[str]
    complainant: Optional[str]
    outcome: Optional[str]
    category_id: int
    investigator_id: int
    created_by_id: int
    status: CaseStatus
    open_date: datetime
    close_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    evidence: list[EvidenceOut] = []

    class Config:
        from_attributes = True


# ---------- Характеристика (на основе активности) ----------

class CharacteristicOut(BaseModel):
    user_id: int
    full_name: str
    position: str
    period_days: int
    total_actions: int
    cases_created: int
    cases_closed: int
    last_activity: Optional[datetime]
    summary_text: str
