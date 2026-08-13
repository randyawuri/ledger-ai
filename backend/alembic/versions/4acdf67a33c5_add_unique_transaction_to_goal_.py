"""add unique transaction to goal contributions

Revision ID: 4acdf67a33c5
Revises: d933f729a3f1
Create Date: 2026-08-10 21:10:45.196039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4acdf67a33c5'
down_revision: Union[str, Sequence[str], None] = 'd933f729a3f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_goal_contributions_transaction_id",
        "goal_contributions",
        ["transaction_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_goal_contributions_transaction_id",
        "goal_contributions",
        type_="unique",
    )
