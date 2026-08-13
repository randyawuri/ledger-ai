from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.merchants.service import MerchantService
from app.users.domain.models import User

router = APIRouter(
    prefix="/merchants",
    tags=["Merchants"],
)


@router.get("")
def merchant_spending(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return MerchantService(db).spending(current_user)