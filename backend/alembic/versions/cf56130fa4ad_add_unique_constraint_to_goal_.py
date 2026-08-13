"""add unique constraint to goal contributions transaction

Revision ID: cf56130fa4ad
Revises: 4acdf67a33c5
Create Date: 2026-08-10 22:25:00.292063

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cf56130fa4ad"
down_revision: Union[str, Sequence[str], None] = "4acdf67a33c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CONSTRAINT_NAME = "uq_goal_contributions_transaction_id"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    constraints = inspector.get_unique_constraints("goal_contributions")

    existing = {
        constraint["name"]
        for constraint in constraints
    }

    if CONSTRAINT_NAME not in existing:
        op.create_unique_constraint(
            CONSTRAINT_NAME,
            "goal_contributions",
            ["transaction_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    constraints = inspector.get_unique_constraints("goal_contributions")

    existing = {
        constraint["name"]
        for constraint in constraints
    }

    if CONSTRAINT_NAME in existing:
        op.drop_constraint(
            CONSTRAINT_NAME,
            "goal_contributions",
            type_="unique",
        )