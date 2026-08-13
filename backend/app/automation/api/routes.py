from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db

from app.users.domain.models import User

from app.automation.schemas import (
    AutomationResponse,
    AutomationRunResponse,
)

from app.automation.service import AutomationService


router = APIRouter(
    prefix="/automation",
    tags=["Automation"],
)


@router.get(
    "",
    response_model=list[AutomationResponse],
)
def list_automations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = AutomationService(db)

    return service.list_automations(current_user)


@router.get(
    "/{automation_id}",
    response_model=AutomationResponse,
)
def get_automation(
    automation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = AutomationService(db)

    automation = service.get_automation(
        automation_id,
    )

    if automation is None:
        raise HTTPException(
            status_code=404,
            detail="Automation not found.",
        )

    if automation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden.",
        )

    return automation


@router.delete(
    "/{automation_id}",
)
def delete_automation(
    automation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = AutomationService(db)

    automation = service.get_automation(
        automation_id,
    )

    if automation is None:
        raise HTTPException(
            status_code=404,
            detail="Automation not found.",
        )

    if automation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden.",
        )

    return service.delete_automation(
        automation,
    )


@router.post(
    "/run/{transaction_id}",
    response_model=AutomationRunResponse,
)
def rerun_automation(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    from app.transactions.domain.models import Transaction

    transaction = (
        db.query(Transaction)
        .get(transaction_id)
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    if transaction.account.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Forbidden.",
        )

    service = AutomationService(db)

    executed = service.rerun_transaction(
        transaction,
    )

    return {
        "message": "Automation executed.",
        "executed_rules": len(executed),
    }