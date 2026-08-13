from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db

from app.recurring.schemas import RecurringTransaction
from app.recurring.service import RecurringService

from app.users.domain.models import User

router = APIRouter(
    prefix="/recurring",
    tags=["Recurring"],
)


@router.get(
    "",
    response_model=list[RecurringTransaction],
)
def recurring_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = RecurringService(db)

    return service.recurring_transactions(current_user)