from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db

from app.insights.schemas import Insight
from app.insights.service import InsightService

from app.users.domain.models import User

router = APIRouter(
    prefix="/insights",
    tags=["Insights"],
)


@router.get(
    "",
    response_model=list[Insight],
)
def get_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = InsightService(db)

    return service.get_insights(current_user)