from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.categories.schemas import (
    CategoryCreate,
    CategoryResponse,
)
from app.categories.service import CategoryService
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.users.domain.models import User

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)

    return service.create_category(
        user=current_user,
        name=category.name,
        transaction_type=category.transaction_type,
        icon=category.icon,
        color=category.color,
    )


@router.get(
    "",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)

    return service.get_categories(current_user)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)

    category = service.get_category(
        current_user,
        category_id,
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category