from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class MerchantResponse(BaseModel):
    id: UUID
    name: str
    total_spent: Decimal
    transactions: int

    class Config:
        from_attributes = True