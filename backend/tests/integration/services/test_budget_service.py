from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.budgets.service import BudgetService
from app.categories.domain.models import TransactionType
from app.db.unit_of_work import UnitOfWork
from app.transactions.domain.models import Transaction
from tests.factories.account_factory import AccountFactory
from tests.factories.category_factory import CategoryFactory
from tests.factories.user_factory import UserFactory

def test_create_budget_for_debit_category(db):
    user = UserFactory.build()
    db.add(user)
    db.commit()
    db.refresh(user)

    category = CategoryFactory.build(
        user=user,
        user_id=user.id,
        transaction_type=TransactionType.DEBIT,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    service = BudgetService(UnitOfWork(db))

    budget = service.create_budget(
        user_id=user.id,
        category_id=category.id,
        name="Food",
        amount=Decimal("100000.00"),
    )

    assert budget.user_id == user.id
    assert budget.category_id == category.id
    assert budget.name == "Food"
    assert budget.amount == Decimal("100000.00")

def test_create_budget_rejects_category_owned_by_another_user(db):
    user = UserFactory.build()
    other_user = UserFactory.build()

    db.add_all([user, other_user])
    db.commit()

    category = CategoryFactory.build(
        user=other_user,
        user_id=other_user.id,
        transaction_type=TransactionType.DEBIT,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    service = BudgetService(UnitOfWork(db))

    with pytest.raises(ValueError, match="Category not found"):
        service.create_budget(
            user_id=user.id,
            category_id=category.id,
            name="Food",
            amount=Decimal("100000.00"),
        )

def test_create_budget_rejects_credit_category(db):
    user = UserFactory.build()

    db.add(user)
    db.commit()
    db.refresh(user)

    category = CategoryFactory.build(
        user=user,
        user_id=user.id,
        transaction_type=TransactionType.CREDIT,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    service = BudgetService(UnitOfWork(db))

    with pytest.raises(
        ValueError,
        match="Budgets can only be created for debit categories",
    ):
        service.create_budget(
            user_id=user.id,
            category_id=category.id,
            name="Salary",
            amount=Decimal("100000.00"),
        )

def test_budget_status_with_no_spending(db):
    user = UserFactory.build()
    db.add(user)
    db.commit()
    db.refresh(user)

    category = CategoryFactory.build(
        user=user,
        user_id=user.id,
        transaction_type=TransactionType.DEBIT,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    service = BudgetService(UnitOfWork(db))

    service.create_budget(
        user_id=user.id,
        category_id=category.id,
        name="Food",
        amount=Decimal("100000.00"),
    )

    results = service.budget_status(user.id)

    assert len(results) == 1

    result = results[0]

    assert result["category"] == "Food"
    assert result["budget"] == Decimal("100000.00")
    assert result["spent"] == Decimal("0")
    assert result["remaining"] == Decimal("100000.00")
    assert result["percent_used"] == 0
    assert result["status"] == "GOOD"


def test_budget_status_calculates_current_month_spending(db):
    user = UserFactory.build()
    db.add(user)
    db.commit()
    db.refresh(user)

    category = CategoryFactory.build(
        user=user,
        user_id=user.id,
        transaction_type=TransactionType.DEBIT,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    account = AccountFactory.build(
        user=user,
        user_id=user.id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    budget = BudgetService(UnitOfWork(db))

    budget.create_budget(
        user_id=user.id,
        category_id=category.id,
        name="Food",
        amount=Decimal("100000.00"),
    )

    transaction = Transaction(
        account_id=account.id,
        category_id=category.id,
        transaction_type=TransactionType.DEBIT,
        amount=Decimal("50000.00"),
        description="Food",
        merchant="Restaurant",
        transaction_date=datetime.now(UTC),
    )

    db.add(transaction)
    db.commit()

    results = budget.budget_status(user.id)

    result = results[0]

    assert result["spent"] == Decimal("50000.00")
    assert result["remaining"] == Decimal("50000.00")
    assert result["percent_used"] == 50
    assert result["status"] == "GOOD"


def test_budget_status_returns_warning_at_80_percent(db):
    user = UserFactory.build()
    db.add(user)
    db.commit()
    db.refresh(user)

    category = CategoryFactory.build(
        user=user,
        user_id=user.id,
        transaction_type=TransactionType.DEBIT,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    account = AccountFactory.build(
        user=user,
        user_id=user.id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    service = BudgetService(UnitOfWork(db))

    service.create_budget(
        user_id=user.id,
        category_id=category.id,
        name="Food",
        amount=Decimal("100000.00"),
    )

    transaction = Transaction(
        account_id=account.id,
        category_id=category.id,
        transaction_type=TransactionType.DEBIT,
        amount=Decimal("80000.00"),
        description="Food",
        merchant="Restaurant",
        transaction_date=datetime.now(UTC),
    )

    db.add(transaction)
    db.commit()

    result = service.budget_status(user.id)[0]

    assert result["spent"] == Decimal("80000.00")
    assert result["remaining"] == Decimal("20000.00")
    assert result["percent_used"] == 80
    assert result["status"] == "WARNING"


def test_budget_status_returns_over_when_budget_is_exceeded(db):
    user = UserFactory.build()
    db.add(user)
    db.commit()
    db.refresh(user)

    category = CategoryFactory.build(
        user=user,
        user_id=user.id,
        transaction_type=TransactionType.DEBIT,
    )
    db.add(category)
    db.commit()
    db.refresh(category)

    account = AccountFactory.build(
        user=user,
        user_id=user.id,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    service = BudgetService(UnitOfWork(db))

    service.create_budget(
        user_id=user.id,
        category_id=category.id,
        name="Food",
        amount=Decimal("100000.00"),
    )

    transaction = Transaction(
        account_id=account.id,
        category_id=category.id,
        transaction_type=TransactionType.DEBIT,
        amount=Decimal("120000.00"),
        description="Food",
        merchant="Restaurant",
        transaction_date=datetime.now(UTC),
    )

    db.add(transaction)
    db.commit()

    result = service.budget_status(user.id)[0]

    assert result["spent"] == Decimal("120000.00")
    assert result["remaining"] == Decimal("-20000.00")
    assert result["percent_used"] == 120
    assert result["status"] == "OVER"