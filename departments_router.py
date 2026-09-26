from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, require_admin
from ..database import get_db

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[schemas.DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    return db.query(models.Department).all()


@router.get("/{department_id}/categories", response_model=list[schemas.CaseCategoryOut])
def list_categories(department_id: int, db: Session = Depends(get_db)):
    return db.query(models.CaseCategory).filter(models.CaseCategory.department_id == department_id).all()


@router.post("/categories", response_model=schemas.CaseCategoryOut)
def create_category(
    payload: schemas.CaseCategoryCreate,
    db: Session = Depends(get_db),
    _admin: models.User = Depends(require_admin),
):
    """Добавить новую категорию дел отделу (только админ — обычно руководитель отдела)."""
    category = models.CaseCategory(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
