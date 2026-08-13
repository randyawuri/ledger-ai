from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.accounts.domain.models import Account
from app.budgets.domain.models import Budget
from app.categories.domain.models import Category
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
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

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    last_login: Mapped[datetime | None] = mapped_column(
         DateTime(timezone=True),
        nullable=True,
    )

    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    budgets: Mapped[list["Budget"]] = relationship(
        "Budget",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    automations = relationship(
        "Automation",
        back_populates="user",
    )