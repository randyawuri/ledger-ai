from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.schemas import (
    AnalyticsResponse,
    MonthlyTrend,
)
from app.analytics.service import AnalyticsService
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.users.domain.models import User


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "",
    response_model=AnalyticsResponse,
)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return service.get_analytics(current_user.id)


@router.get(
    "/trends",
    response_model=list[MonthlyTrend],
)
def monthly_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnalyticsService(db)
    return service.monthly_trends(current_user.id)