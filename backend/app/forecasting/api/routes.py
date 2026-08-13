from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db

from app.forecasting.schemas import CashFlowForecast, ForecastResponse
from app.forecasting.service import ForecastService

from app.users.domain.models import User


router = APIRouter(
    prefix="/forecast",
    tags=["Forecast"],
)


@router.get(
    "",
    response_model=ForecastResponse,
)
def get_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ForecastService(db)

    return service.get_forecast(current_user)