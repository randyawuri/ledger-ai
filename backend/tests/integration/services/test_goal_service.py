from decimal import Decimal

import pytest

from app.db.unit_of_work import UnitOfWork
from app.goals.domain.models import GoalStatus
from app.goals.service import GoalService

from tests.factories.account_factory import AccountFactory
from tests.factories.transaction_factory import TransactionFactory
from tests.factories.user_factory import UserFactory


def create_user(db):
    user = UserFactory()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_create_goal(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    assert goal.id is not None
    assert goal.user_id == user.id
    assert goal.name == "Emergency Fund"
    assert goal.target_amount == Decimal("100000.00")
    assert goal.status == GoalStatus.ACTIVE


def test_list_goals_only_returns_users_goals(db):
    user = create_user(db)
    other_user = create_user(db)

    service = GoalService(UnitOfWork(db))

    service.create_goal(
        user=user,
        name="Goal One",
        target_amount=Decimal("100000.00"),
    )

    service.create_goal(
        user=other_user,
        name="Other Goal",
        target_amount=Decimal("50000.00"),
    )

    goals = service.list_goals(user)

    assert len(goals) == 1
    assert goals[0].name == "Goal One"


def test_get_goal_returns_owned_goal(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    result = service.get_goal(
        goal_id=goal.id,
        user_id=user.id,
    )

    assert result.id == goal.id


def test_get_goal_rejects_wrong_user(db):
    owner = create_user(db)
    other_user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=owner,
        name="Private Goal",
        target_amount=Decimal("100000.00"),
    )

    with pytest.raises(ValueError, match="Goal not found"):
        service.get_goal(
            goal_id=goal.id,
            user_id=other_user.id,
        )


def test_delete_goal(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Delete Me",
        target_amount=Decimal("100000.00"),
    )

    service.delete_goal(
        goal_id=goal.id,
        user_id=user.id,
    )

    with pytest.raises(ValueError, match="Goal not found"):
        service.get_goal(
            goal_id=goal.id,
            user_id=user.id,
        )


def test_add_contribution(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    contribution = service.add_contribution(
        goal_id=goal.id,
        user_id=user.id,
        amount=Decimal("25000.00"),
    )

    assert contribution.id is not None
    assert contribution.goal_id == goal.id
    assert contribution.amount == Decimal("25000.00")


def test_rejects_zero_contribution(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    with pytest.raises(
        ValueError,
        match="Contribution amount must be greater than zero",
    ):
        service.add_contribution(
            goal_id=goal.id,
            user_id=user.id,
            amount=Decimal("0"),
        )


def test_rejects_negative_contribution(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    with pytest.raises(
        ValueError,
        match="Contribution amount must be greater than zero",
    ):
        service.add_contribution(
            goal_id=goal.id,
            user_id=user.id,
            amount=Decimal("-100.00"),
        )


def test_progress_calculation(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    service.add_contribution(
        goal_id=goal.id,
        user_id=user.id,
        amount=Decimal("25000.00"),
    )

    service.add_contribution(
        goal_id=goal.id,
        user_id=user.id,
        amount=Decimal("15000.00"),
    )

    result = service.progress(
        goal_id=goal.id,
        user_id=user.id,
    )

    assert result["saved"] == Decimal("40000.00")
    assert result["remaining"] == Decimal("60000.00")
    assert result["percent"] == Decimal("40.00")
    assert result["goal"].id == goal.id


def test_progress_cannot_exceed_remaining_amount(db):
    user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Small Goal",
        target_amount=Decimal("10000.00"),
    )

    service.add_contribution(
        goal_id=goal.id,
        user_id=user.id,
        amount=Decimal("15000.00"),
    )

    result = service.progress(
        goal_id=goal.id,
        user_id=user.id,
    )

    assert result["saved"] == Decimal("15000.00")
    assert result["remaining"] == Decimal("0")
    assert result["percent"] == Decimal("150.00")


def test_progress_rejects_wrong_user(db):
    owner = create_user(db)
    other_user = create_user(db)

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=owner,
        name="Private Goal",
        target_amount=Decimal("100000.00"),
    )

    with pytest.raises(ValueError, match="Goal not found"):
        service.progress(
            goal_id=goal.id,
            user_id=other_user.id,
        )


def test_add_contribution_from_transaction(db):
    user = create_user(db)

    account = AccountFactory(user=user)

    transaction = TransactionFactory(
        account=account,
        amount=Decimal("40000.00"),
    )

    db.add(account)
    db.add(transaction)
    db.flush()

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    contribution = service.add_contribution(
        goal_id=goal.id,
        user_id=user.id,
        amount=Decimal("40000.00"),
        transaction_id=transaction.id,
    )

    assert contribution.id is not None
    assert contribution.goal_id == goal.id
    assert contribution.transaction_id == transaction.id
    assert contribution.amount == Decimal("40000.00")


def test_cannot_link_another_users_transaction(db):
    user = create_user(db)
    other_user = create_user(db)

    account = AccountFactory(user=other_user)

    transaction = TransactionFactory(
        account=account,
        amount=Decimal("40000.00"),
    )

    db.add(account)
    db.add(transaction)
    db.flush()

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    with pytest.raises(
        ValueError,
        match="Transaction not found",
    ):
        service.add_contribution(
            goal_id=goal.id,
            user_id=user.id,
            amount=Decimal("40000.00"),
            transaction_id=transaction.id,
        )


def test_transaction_cannot_be_linked_twice(db):
    user = create_user(db)

    account = AccountFactory(user=user)

    transaction = TransactionFactory(
        account=account,
        amount=Decimal("40000.00"),
    )

    db.add(account)
    db.add(transaction)
    db.flush()

    service = GoalService(UnitOfWork(db))

    goal_one = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    goal_two = service.create_goal(
        user=user,
        name="Vacation",
        target_amount=Decimal("200000.00"),
    )

    service.add_contribution(
        goal_id=goal_one.id,
        user_id=user.id,
        amount=Decimal("40000.00"),
        transaction_id=transaction.id,
    )

    with pytest.raises(
        ValueError,
        match="Transaction is already linked to a goal",
    ):
        service.add_contribution(
            goal_id=goal_two.id,
            user_id=user.id,
            amount=Decimal("40000.00"),
            transaction_id=transaction.id,
        )


def test_contribution_cannot_exceed_transaction_amount(db):
    user = create_user(db)

    account = AccountFactory(user=user)

    transaction = TransactionFactory(
        account=account,
        amount=Decimal("10000.00"),
    )

    db.add(account)
    db.add(transaction)
    db.flush()

    service = GoalService(UnitOfWork(db))

    goal = service.create_goal(
        user=user,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
    )

    with pytest.raises(
        ValueError,
        match="Contribution cannot exceed transaction amount",
    ):
        service.add_contribution(
            goal_id=goal.id,
            user_id=user.id,
            amount=Decimal("15000.00"),
            transaction_id=transaction.id,
        )