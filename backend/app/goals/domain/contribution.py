import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class GoalContribution(Base):
    __tablename__ = "goal_contributions"

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            name="uq_goal_contributions_transaction_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id"),
        nullable=False,
    )

    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("transactions.id"),
    nullable=True,
    unique=True,
)

    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    goal = relationship(
        "Goal",
        back_populates="contributions",
    )

    transaction = relationship(
        "Transaction",
    )