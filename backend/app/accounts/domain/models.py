from decimal import Decimal
import uuid
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"

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

    name: Mapped[str] = mapped_column(String(100))

    institution: Mapped[str] = mapped_column(String(100))

    currency: Mapped[str] = mapped_column(String(3), default="NGN")

    opening_balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0.00"),
        )
    
    user = relationship(
    "User",
    back_populates="accounts",
    )

    transactions = relationship(
    "Transaction",
    back_populates="account",
    )