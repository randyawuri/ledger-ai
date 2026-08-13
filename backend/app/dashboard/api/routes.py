from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.dashboard.schemas import DashboardSummary
from app.dashboard.service import DashboardService
from app.db.session import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = DashboardService(db)

    return service.get_dashboard(current_user)