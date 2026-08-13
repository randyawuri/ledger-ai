from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.goals.schemas import (
    GoalContributionResponse,
    GoalCreate,
    GoalProgress,
    GoalProgressResponse,
    GoalProjectionRequest,
    GoalProjectionResponse,
    GoalResponse,
)
from app.goals.service import GoalService
from app.users.domain.models import User
from app.db.unit_of_work import UnitOfWork


router = APIRouter(
    prefix="/goals",
    tags=["Goals"],
)


@router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GoalService(UnitOfWork(db))

    try:
        return service.create_goal(
            user=current_user,
            name=goal.name,
            target_amount=goal.target_amount,
            target_date=goal.target_date,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[GoalResponse],
)
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GoalService(UnitOfWork(db))

    return service.list_goals(current_user)


@router.get(
    "/{goal_id}",
    response_model=GoalResponse,
)
def get_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GoalService(UnitOfWork(db))

    try:
        return service.get_goal(
            goal_id=goal_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_goal(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GoalService(UnitOfWork(db))

    try:
        service.delete_goal(
            goal_id=goal_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{goal_id}/contributions",
    response_model=GoalContributionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_contribution(
    goal_id: UUID,
    contribution: GoalProgress,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GoalService(UnitOfWork(db))

    try:
        return service.add_contribution(
            goal_id=goal_id,
            user_id=current_user.id,
            amount=contribution.amount,
            transaction_id=contribution.transaction_id,
)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{goal_id}/projection",
    response_model=GoalProjectionResponse,
)
def project_goal(
    goal_id: UUID,
    projection: GoalProjectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GoalService(UnitOfWork(db))

    try:
        return service.project_goal(
        goal_id=goal_id,
        user_id=current_user.id,
        monthly_contribution=projection.monthly_contribution,
    )
    except ValueError as e:
        if str(e) == "Goal not found":
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e),
    )


@router.get(
    "/{goal_id}/progress",
    response_model=GoalProgressResponse,
)
def get_goal_progress(
    goal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = GoalService(UnitOfWork(db))

    try:
        return service.progress(
            goal_id=goal_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    