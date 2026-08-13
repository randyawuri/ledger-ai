from decimal import Decimal

from app.goals.domain.contribution import GoalContribution
from app.goals.domain.models import Goal, GoalStatus
from app.goals.repository import GoalRepository
from tests.factories.user_factory import UserFactory


def create_user(db):
    user = UserFactory()
    db.add(user)
    db.flush()
    return user


def make_goal(user_id):
    return Goal(
        user_id=user_id,
        name="Emergency Fund",
        target_amount=Decimal("100000.00"),
        status=GoalStatus.ACTIVE,
    )


def test_create_goal(db):
    user = create_user(db)
    repository = GoalRepository(db)
    
    goal = make_goal(user.id)

    repository.create(goal)
    db.flush()

    result = repository.get(goal.id)

    assert result is not None
    assert result.id == goal.id
    assert result.user_id == user.id
    assert result.name == "Emergency Fund"
    assert result.target_amount == Decimal("100000.00")


def test_get_for_user_returns_owned_goal(db):
    user = create_user(db)
    repository = GoalRepository(db)

    goal = make_goal(user.id)

    repository.create(goal)
    db.flush()

    result = repository.get_for_user(goal.id, user.id)

    assert result is not None
    assert result.id == goal.id


def test_get_for_user_does_not_return_another_users_goal(db):
    owner = create_user(db)
    other_user = create_user(db)
    
    repository = GoalRepository(db)

    goal = make_goal(owner.id)

    repository.create(goal)
    db.flush()

    result = repository.get_for_user(
        goal.id,
        other_user.id,
    )

    assert result is None


def test_list_by_user_only_returns_owned_goals(db):
    user = create_user(db)
    other_user = create_user(db)

    repository = GoalRepository(db)

    goal_one = make_goal(user.id)
    goal_two = make_goal(user.id)
    other_goal = make_goal(other_user.id)

    repository.create(goal_one)
    repository.create(goal_two)
    repository.create(other_goal)

    db.flush()

    results = repository.list_by_user(user.id)

    assert len(results) == 2
    assert {goal.id for goal in results} == {
        goal_one.id,
        goal_two.id,
    }


def test_delete_goal(db):
    user = create_user(db)
    repository = GoalRepository(db)

    goal = make_goal(user.id)

    repository.create(goal)
    db.flush()

    repository.delete(goal)
    db.flush()

    result = repository.get(goal.id)

    assert result is None


def test_current_amount_returns_zero_without_contributions(db):
    user = create_user(db)
    repository = GoalRepository(db)

    goal = make_goal(user.id)

    repository.create(goal)
    db.flush()

    result = repository.current_amount(goal.id)

    assert result == Decimal("0")


def test_add_contribution_and_current_amount(db):
    user = create_user(db)
    repository = GoalRepository(db)

    goal = make_goal(user.id)

    repository.create(goal)
    db.flush()

    contribution_one = GoalContribution(
        goal_id=goal.id,
        amount=Decimal("25000.00"),
    )

    contribution_two = GoalContribution(
        goal_id=goal.id,
        amount=Decimal("15000.00"),
    )

    repository.add_contribution(contribution_one)
    repository.add_contribution(contribution_two)

    db.flush()

    result = repository.current_amount(goal.id)

    assert result == Decimal("40000.00")