from decimal import Decimal
from uuid import UUID

from app.transactions.domain.models import TransactionType
from app.goals.domain.models import (
    Goal,
    GoalStatus,
)
from app.goals.domain.contribution import GoalContribution
from app.db.unit_of_work import UnitOfWork
from app.goals.engine import GoalEngine


class GoalService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.engine = GoalEngine()

    def create_goal(
        self,
        user,
        name,
        target_amount,
        target_date=None,
    ):
        goal = Goal(
            user_id=user.id,
            name=name,
            target_amount=target_amount,
            target_date=target_date,
            status=GoalStatus.ACTIVE,
        )

        self.uow.goals.create(goal)
        self.uow.commit()

        return goal

    def get_goal(
        self,
        goal_id: UUID,
        user_id: UUID,
    ):
        goal = self.uow.goals.get_for_user(
            goal_id,
            user_id,
        )

        if goal is None:
            raise ValueError("Goal not found")

        return goal

    def list_goals(
        self,
        user,
    ):
        return self.uow.goals.list_by_user(user.id)

    def delete_goal(
        self,
        goal_id: UUID,
        user_id: UUID,
    ):
        goal = self.uow.goals.get_for_user(
            goal_id,
            user_id,
        )

        if goal is None:
            raise ValueError("Goal not found")

        self.uow.goals.delete(goal)
        self.uow.commit()

    
    def add_contribution(
            self,
            goal_id: UUID,
            user_id: UUID,
            amount: Decimal,
            transaction_id: UUID | None = None,
    ):
            goal = self.uow.goals.get_for_user(
                 goal_id,
                 user_id,
            )

            if goal is None:
                 raise ValueError("Goal not found")

            if amount <= Decimal("0"):
                 raise ValueError(
                "Contribution amount must be greater than zero"
            )

            if transaction_id is not None:
                 transaction = self.uow.transactions.get_for_user(
                      transaction_id,
                      user_id,
                )
                 if transaction is None:
                      raise ValueError("Transaction not found")
                 
                 existing = (
                     self.uow.goals.get_contribution_by_transaction(
                          transaction_id
                        )
                )
                 
                 if existing is not None:
                      raise ValueError(
                           "Transaction is already linked to a goal"
                        )
                 
                 if amount > transaction.amount:
                      raise ValueError(
                           "Contribution cannot exceed transaction amount"
                        )
            contribution = GoalContribution(
                 goal_id=goal.id,
                 amount=amount,
                 transaction_id=transaction_id,
            )
            
            self.uow.goals.add_contribution(contribution)

            self.uow.commit()

            return contribution


    def progress(
        self,
        goal_id: UUID,
        user_id: UUID,
    ):
        goal = self.uow.goals.get_for_user(
            goal_id,
            user_id,
        )

        if goal is None:
            raise ValueError("Goal not found")

        saved = self.uow.goals.current_amount(goal.id)

        remaining = max(
            Decimal("0"),
            goal.target_amount - saved,
        )

        percent = Decimal("0")

        if goal.target_amount > 0:
            percent = (
                saved / goal.target_amount
            ) * 100

        return {
            "goal": goal,
            "saved": saved,
            "remaining": remaining,
            "percent": round(percent, 2),
        }
    

    def project_goal(
            self,
            goal_id: UUID,
            user_id: UUID,
            monthly_contribution: Decimal,
        ):
        goal = self.uow.goals.get_for_user(
            goal_id,
            user_id,
        )
        if goal is None:
            raise ValueError("Goal not found")

        if monthly_contribution < Decimal("0"):
            raise ValueError(
                "Monthly contribution cannot be negative"
            )

        if goal.target_date is None:
            raise ValueError(
                "Goal must have a target date to calculate a projection"
            )

        current_amount = self.uow.goals.current_amount(goal.id)

        projection = self.engine.project(
            current_amount=current_amount,
            target_amount=goal.target_amount,
            monthly_contribution=monthly_contribution,
            target_date=goal.target_date,
        )
        return {
            "goal": goal,
            **projection,
        }