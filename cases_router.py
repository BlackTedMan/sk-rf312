from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..websocket_manager import manager

router = APIRouter(prefix="/cases", tags=["cases"])


def _log(db: Session, user_id: int, action: str, case_id: Optional[int] = None):
    db.add(models.ActivityLog(user_id=user_id, action=action, case_id=case_id))
    db.commit()


@router.get("", response_model=list[schemas.CaseOut])
def list_cases(
    department_id: Optional[int] = None,
    category_id: Optional[int] = None,
    status: Optional[models.CaseStatus] = None,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    q = db.query(models.Case)
    if category_id:
        q = q.filter(models.Case.category_id == category_id)
    if status:
        q = q.filter(models.Case.status == status)
    if department_id:
        q = q.join(models.CaseCategory).filter(models.CaseCategory.department_id == department_id)
    return q.order_by(models.Case.created_at.desc()).all()


@router.get("/{case_id}", response_model=schemas.CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db), _user: models.User = Depends(get_current_user)):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")
    return case


@router.post("", response_model=schemas.CaseOut)
async def create_case(
    payload: schemas.CaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if db.query(models.Case).filter(models.Case.number == payload.number).first():
        raise HTTPException(status_code=400, detail="Дело с таким номером уже существует")

    category = db.query(models.CaseCategory).filter(models.CaseCategory.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Категория не найдена")

    case = models.Case(
        number=payload.number,
        article=payload.article,
        suspects=payload.suspects,
        complainant=payload.complainant,
        category_id=payload.category_id,
        investigator_id=payload.investigator_id or current_user.id,
        created_by_id=current_user.id,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    _log(db, current_user.id, "case_created", case.id)

    # уведомляем всех подключённых клиентов о новом деле
    await manager.broadcast("new_case", schemas.CaseOut.model_validate(case).model_dump())

    return case


@router.patch("/{case_id}", response_model=schemas.CaseOut)
async def update_case(
    case_id: int,
    payload: schemas.CaseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(case, field, value)

    db.commit()
    db.refresh(case)
    _log(db, current_user.id, "case_updated", case.id)

    await manager.broadcast("case_updated", schemas.CaseOut.model_validate(case).model_dump())
    return case


@router.post("/{case_id}/close", response_model=schemas.CaseOut)
async def close_case(
    case_id: int,
    payload: schemas.CaseClose,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    case.status = models.CaseStatus.CLOSED
    case.outcome = payload.outcome
    case.close_date = datetime.utcnow()

    db.commit()
    db.refresh(case)
    _log(db, current_user.id, "case_closed", case.id)

    await manager.broadcast("case_closed", schemas.CaseOut.model_validate(case).model_dump())
    return case


@router.post("/{case_id}/evidence", response_model=schemas.EvidenceOut)
def add_evidence(
    case_id: int,
    payload: schemas.EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Дело не найдено")

    evidence = models.Evidence(case_id=case_id, title=payload.title, url_or_path=payload.url_or_path)
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    _log(db, current_user.id, "evidence_added", case_id)
    return evidence
