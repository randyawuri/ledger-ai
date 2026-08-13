from datetime import date
from decimal import Decimal

from app.goals.engine import GoalEngine


def test_project_goal_will_reach_target():
    engine = GoalEngine()

    result = engine.project(
        current_amount=Decimal("40000.00"),
        target_amount=Decimal("100000.00"),
        monthly_contribution=Decimal("10000.00"),
        target_date=date(2027, 3, 1),
        today=date(2026, 3, 1),
    )

    assert result["will_reach"] is True
    assert result["projected_amount"] == Decimal("160000.00")
    assert result["required_monthly"] == Decimal("5000.00")
    assert result["months_remaining"] == 12


def test_project_goal_will_not_reach_target():
    engine = GoalEngine()

    result = engine.project(
        current_amount=Decimal("40000.00"),
        target_amount=Decimal("100000.00"),
        monthly_contribution=Decimal("5000.00"),
        target_date=date(2026, 9, 1),
        today=date(2026, 3, 1),
    )

    assert result["will_reach"] is False
    assert result["projected_amount"] == Decimal("70000.00")
    assert result["required_monthly"] == Decimal("10000.00")
    assert result["months_remaining"] == 6


def test_project_goal_already_reached():
    engine = GoalEngine()

    result = engine.project(
        current_amount=Decimal("120000.00"),
        target_amount=Decimal("100000.00"),
        monthly_contribution=Decimal("5000.00"),
        target_date=date(2027, 3, 1),
    )

    assert result["will_reach"] is True
    assert result["required_monthly"] == Decimal("0.00")


def test_project_goal_with_zero_monthly_contribution():
    engine = GoalEngine()

    result = engine.project(
        current_amount=Decimal("40000.00"),
        target_amount=Decimal("100000.00"),
        monthly_contribution=Decimal("0.00"),
        target_date=date(2027, 3, 1),
        today=date(2026, 3, 1),
    )

    assert result["will_reach"] is False
    assert result["projected_amount"] == Decimal("40000.00")
    assert result["required_monthly"] == Decimal("5000.00")
    assert result["months_remaining"] == 12


def test_project_goal_target_date_today_uses_one_month():
    engine = GoalEngine()

    result = engine.project(
        current_amount=Decimal("40000.00"),
        target_amount=Decimal("50000.00"),
        monthly_contribution=Decimal("10000.00"),
        target_date=date.today(),
    )

    assert result["months_remaining"] == 1
    assert result["projected_amount"] == Decimal("50000.00")
    assert result["will_reach"] is True


def test_project_goal_target_date_in_past_uses_one_month():
    engine = GoalEngine()

    result = engine.project(
        current_amount=Decimal("40000.00"),
        target_amount=Decimal("50000.00"),
        monthly_contribution=Decimal("5000.00"),
        target_date=date(2020, 1, 1),
    )

    assert result["months_remaining"] == 1
    assert result["projected_amount"] == Decimal("45000.00")
    assert result["will_reach"] is False