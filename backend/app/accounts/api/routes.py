from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.accounts.schemas import (
    AccountCreate,
    AccountResponse,
    AccountBalanceResponse,
)
from app.accounts.service import AccountService
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.users.domain.models import User
router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)

@router.post(
    "",
    response_model=AccountResponse,
)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)

    return service.create_account(
        user_id=current_user.id,
        name=account.name,
        institution=account.institution,
        currency=account.currency,
        opening_balance=account.opening_balance,
    )
@router.get(
    "",
    response_model=list[AccountResponse],
)
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)
    return service.get_accounts(current_user.id)


@router.get(
    "/{account_id}/balance",
    response_model=AccountBalanceResponse,
)
def get_account_balance(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AccountService(db)

    balance = service.get_account_balance(
        current_user,
        account_id,
    )

    if balance is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return balance
