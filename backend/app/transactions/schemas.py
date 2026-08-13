from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.transactions.domain.models import TransactionType


class TransactionCreate(BaseModel):
    account_id: UUID
    category_id: UUID | None = None
    transaction_type: TransactionType
    amount: Decimal = Field(..., gt=0, description="The amount of the transaction. Must be greater than 0.")    
    description: str
    merchant: str | None = None
    transaction_date: datetime


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_id: UUID
    category_id: UUID | None
    transaction_type: TransactionType
    amount: Decimal
    description: str
    merchant: str | None
    transaction_date: datetime
    created_at: datetime
    

class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    limit: int
    offset: int


class TransactionFilter(BaseModel):
    account_id: UUID | None = None
    category_id: UUID | None = None

    transaction_type: TransactionType | None = None

    start_date: date | None = None
    end_date: date | None = None

    min_amount: Decimal | None = None
    max_amount: Decimal | None = None

    merchant: str | None = None

    description: str | None = None

class TransactionUpdate(BaseModel):
    category_id: UUID | None = None
    transaction_type: TransactionType | None = None
    amount: Decimal | None = Field(
        default=None,
        gt=0,
        description="The amount of the transaction. Must be greater than 0.",
    )
    description: str | None = None
    merchant: str | None = None
    transaction_date: datetime | None = None