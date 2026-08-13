from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.categories.domain.models import TransactionType


class CategoryCreate(BaseModel):
    name: str
    transaction_type: TransactionType
    icon: str = "folder"
    color: str = "#4F46E5"


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    transaction_type: TransactionType
    icon: str
    color: str