from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.health.schemas import FinancialHealthResponse
from app.health.service import FinancialHealthService
from app.users.domain.models import User

router = APIRouter(
    prefix="/health",
    tags=["Financial Health"],
)


@router.get(
    "",
    response_model=FinancialHealthResponse,
)
def get_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = FinancialHealthService(db)

    return service.get_health(current_user)