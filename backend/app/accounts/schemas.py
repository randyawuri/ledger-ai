from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AccountCreate(BaseModel):
    name: str
    institution: str
    currency: str = "NGN"
    opening_balance: Decimal = Decimal("0")


class AccountResponse(BaseModel):
    id: UUID
    name: str
    institution: str
    currency: str
    opening_balance: Decimal

    model_config = {
        "from_attributes": True
    }

class AccountBalanceResponse(BaseModel):
    account_id: UUID
    opening_balance: Decimal
    total_income: Decimal
    total_expenses: Decimal
    current_balance: Decimal