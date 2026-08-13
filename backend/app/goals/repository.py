from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.goals.domain.models import Goal
from app.goals.domain.contribution import GoalContribution


class GoalRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, goal: Goal):
        self.db.add(goal)
        return goal

    def get(self, goal_id: UUID):
        return (
            self.db.query(Goal)
            .filter(Goal.id == goal_id)
            .first()
        )

    def get_for_user(
        self,
        goal_id: UUID,
        user_id: UUID,
    ):
        return (
            self.db.query(Goal)
            .filter(
                Goal.id == goal_id,
                Goal.user_id == user_id,
            )
            .first()
        )

    def list_by_user(self, user_id: UUID):
        return (
            self.db.query(Goal)
            .filter(Goal.user_id == user_id)
            .all()
        )

    def delete(self, goal: Goal):
        self.db.delete(goal)

    def add_contribution(
        self,
        contribution: GoalContribution,
    ):
        self.db.add(contribution)
    
    def get_contribution_by_transaction(
            self,
            transaction_id: UUID,
    ) -> GoalContribution | None:
            return (
                self.db.query(GoalContribution)
                .filter(
                GoalContribution.transaction_id == transaction_id
            )
                .first()
            )


    def current_amount(
        self,
        goal_id: UUID,
    ) -> Decimal:
        return (
            self.db.query(
                func.coalesce(
                    func.sum(
                        GoalContribution.amount
                    ),
                    0,
                )
            )
            .filter(
                GoalContribution.goal_id == goal_id
            )
            .scalar()
        )