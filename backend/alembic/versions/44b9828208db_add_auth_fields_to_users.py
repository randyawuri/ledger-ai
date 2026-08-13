"""add auth fields to users

Revision ID: 44b9828208db
Revises: 77a4adbe02a9
Create Date: 2026-08-05 17:39:51.852310
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "44b9828208db"
down_revision: Union[str, Sequence[str], None] = "77a4adbe02a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "last_login",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # Remove defaults so new inserts rely on the ORM/model defaults
    op.alter_column("users", "is_active", server_default=None)
    op.alter_column("users", "is_verified", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("users", "last_login")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "is_active")