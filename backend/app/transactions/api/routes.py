from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.transactions.schemas import (
    TransactionCreate,
    TransactionResponse,
    TransactionFilter,
    TransactionListResponse,
    TransactionUpdate,
    TransactionType,
)
from app.transactions.service import TransactionService
from app.users.domain.models import User

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TransactionService(db)

    try:
        return service.create(
            payload=transaction,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )



@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TransactionService(db)

    transaction = service.get_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return transaction

@router.get(
    "",
    response_model=TransactionListResponse,
)
def get_transactions(
    account_id: UUID | None = None,
    category_id: UUID | None = None,
    transaction_type: TransactionType | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    min_amount: Decimal| None = None,
    max_amount: Decimal | None = None,
    merchant: str | None = None,
    description: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TransactionService(db)

    filters = TransactionFilter(
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        merchant=merchant,
        description=description,
    )

    return service.search_transactions(
        current_user,
        filters,
        limit=limit,
        offset=offset,
    )

@router.patch(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def update_transaction(
    transaction_id: UUID,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TransactionService(db)

    updated_transaction = service.update_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
        payload=transaction,
    )

    if updated_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return updated_transaction