from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class BudgetCreate(BaseModel):
    category_id: UUID
    name: str
    amount: Decimal


class BudgetResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    category_id: UUID
    name: str
    amount: Decimal

class BudgetStatus(BaseModel):
    category: str
    budget: Decimal
    spent: Decimal
    remaining: Decimal
    percent_used: float
    status: str

