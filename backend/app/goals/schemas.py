from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.goals.domain.models import GoalStatus


class GoalCreate(BaseModel):
    name: str
    target_amount: Decimal
    target_date: date | None = None


class GoalResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: date | None
    status: GoalStatus



class GoalProjectionRequest(BaseModel):
    monthly_contribution: Decimal = Field(
        gt=0,
    )

class GoalProjectionResponse(BaseModel):
    goal: GoalResponse

    will_reach: bool

    projected_amount: Decimal

    required_monthly: Decimal

    months_remaining: int


class GoalProgress(BaseModel):
    amount: Decimal
    transaction_id: UUID | None = None


class GoalProgressResponse(BaseModel):

    goal: GoalResponse

    saved: Decimal

    remaining: Decimal

    percent: Decimal


class GoalContributionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    goal_id: UUID
    transaction_id: UUID | None
    amount: Decimal
    created_at: datetime