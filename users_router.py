from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[schemas.UserOut])
def list_users(
    department_id: int | None = None,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    q = db.query(models.User)
    if department_id:
        q = q.filter(models.User.department_id == department_id)
    return q.all()


@router.get("/{user_id}/characteristic", response_model=schemas.CharacteristicOut)
def get_characteristic(
    user_id: int,
    period_days: int = 30,
    db: Session = Depends(get_db),
    _user: models.User = Depends(get_current_user),
):
    """
    Авто-генерация характеристики по активности за период (по умолчанию 30 дней):
    сколько раз заходил/работал, сколько дел завёл, сколько закрыл.
    """
    target = db.query(models.User).filter(models.User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    since = datetime.utcnow() - timedelta(days=period_days)

    logs_q = db.query(models.ActivityLog).filter(
        models.ActivityLog.user_id == user_id,
        models.ActivityLog.timestamp >= since,
    )

    total_actions = logs_q.count()
    cases_created = logs_q.filter(models.ActivityLog.action == "case_created").count()
    cases_closed = logs_q.filter(models.ActivityLog.action == "case_closed").count()
    last_activity = db.query(func.max(models.ActivityLog.timestamp)).filter(
        models.ActivityLog.user_id == user_id
    ).scalar()

    # простая текстовая характеристика — при желании доработать под формат отдела
    if total_actions == 0:
        summary = f"{target.full_name} ({target.position}) не проявлял(а) активности за последние {period_days} дн."
    else:
        summary = (
            f"{target.full_name} ({target.position}) за последние {period_days} дн. "
            f"выполнил(а) {total_actions} действий: заведено дел — {cases_created}, "
            f"закрыто дел — {cases_closed}. Последняя активность: "
            f"{last_activity.strftime('%d.%m.%Y %H:%M') if last_activity else '—'}."
        )

    return schemas.CharacteristicOut(
        user_id=target.id,
        full_name=target.full_name,
        position=target.position,
        period_days=period_days,
        total_actions=total_actions,
        cases_created=cases_created,
        cases_closed=cases_closed,
        last_activity=last_activity,
        summary_text=summary,
    )
