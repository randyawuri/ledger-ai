from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.budgets.schemas import (
    BudgetCreate,
    BudgetResponse,
    BudgetStatus,
)
from app.budgets.service import BudgetService
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.db.unit_of_work import UnitOfWork
from app.users.domain.models import User

router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
)


@router.post(
    "",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uow = UnitOfWork(db)
    service = BudgetService(uow)

    try:
        return service.create_budget(
            current_user.id,
            budget.category_id,
            budget.name,
            budget.amount,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[BudgetResponse],
)
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uow = UnitOfWork(db)
    service = BudgetService(uow)

    return service.get_budgets(current_user.id)


@router.get(
    "/status",
    response_model=list[BudgetStatus],
)
def budget_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    uow = UnitOfWork(db)
    service = BudgetService(uow)

    return service.budget_status(current_user.id)