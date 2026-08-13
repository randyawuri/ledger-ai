import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import func

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class AutomationStatus(str, Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"


class Automation(Base):
    __tablename__ = "automations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id"),
        nullable=True,
    )

    rule_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    status: Mapped[AutomationStatus] = mapped_column(
        SqlEnum(
            AutomationStatus,
            name="automation_status_enum",
        ),
        default=AutomationStatus.PENDING,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    #
    # Relationships
    #

    user = relationship(
        "User",
        back_populates="automations",
    )

    transaction = relationship(
        "Transaction",
    )