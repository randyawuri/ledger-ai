import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class Category(Base):
    __tablename__ = "categories"

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

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        SqlEnum(
            TransactionType,
            name="transaction_type_enum",
        ),
        nullable=False,
    )

    icon: Mapped[str] = mapped_column(
        String(50),
        default="folder",
    )

    color: Mapped[str] = mapped_column(
        String(20),
        default="#4F46E5",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship(
        "User",
        back_populates="categories",
    )

    transactions = relationship(
        "Transaction",
        back_populates="category",
    )