from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class AutomationStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"


class AutomationBase(BaseModel):
    rule_name: str
    action: str
    payload: dict | None = None


class AutomationCreate(AutomationBase):
    transaction_id: UUID | None = None


class AutomationResponse(AutomationBase):
    id: UUID
    transaction_id: UUID | None
    status: AutomationStatus
    created_at: datetime
    executed_at: datetime | None

    model_config = {
        "from_attributes": True,
    }


class AutomationRunResponse(BaseModel):
    message: str
    executed_rules: int


class AutomationListResponse(BaseModel):
    automations: list[AutomationResponse]