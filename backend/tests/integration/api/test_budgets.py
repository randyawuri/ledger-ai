from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.auth.security import create_access_token
from app.common.enums import TransactionType
from app.db.session import get_db
from app.main import app
from app.transactions.domain.models import Transaction
from tests.factories.account_factory import AccountFactory
from tests.factories.category_factory import CategoryFactory
from tests.factories.user_factory import UserFactory


def create_user(db):
    user = UserFactory()
    db.add(user)
    db.flush()
    return user


def create_category(db, user, transaction_type=TransactionType.DEBIT, name="Food"):
    category = CategoryFactory.build(
        user=user,
        user_id=user.id,
        transaction_type=transaction_type,
        name=name,
    )
    db.add(category)
    db.flush()
    return category


def create_account(db, user):
    account = AccountFactory.build(
        user=user,
        user_id=user.id,
    )
    db.add(account)
    db.flush()
    return account


def auth_headers(user):
    token = create_access_token(
        subject=str(user.id),
    )

    return {
        "Authorization": f"Bearer {token}",
    }


def override_db(db):
    def _override_get_db():
        yield db

    return _override_get_db


def test_create_budget(db):
    user = create_user(db)
    category = create_category(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/budgets",
            headers=auth_headers(user),
            json={
                "category_id": str(category.id),
                "name": "Food",
                "amount": "100000.00",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["category_id"] == str(category.id)
        assert data["name"] == "Food"
        assert Decimal(data["amount"]) == Decimal("100000.00")

    finally:
        app.dependency_overrides.clear()


def test_create_budget_rejects_another_users_category(db):
    user = create_user(db)
    other_user = create_user(db)

    category = create_category(db, other_user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/budgets",
            headers=auth_headers(user),
            json={
                "category_id": str(category.id),
                "name": "Unauthorized",
                "amount": "100000.00",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Category not found"

    finally:
        app.dependency_overrides.clear()


def test_create_budget_rejects_credit_category(db):
    user = create_user(db)

    category = create_category(
        db,
        user,
        transaction_type=TransactionType.CREDIT,
        name="Salary",
    )

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/budgets",
            headers=auth_headers(user),
            json={
                "category_id": str(category.id),
                "name": "Salary",
                "amount": "100000.00",
            },
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Budgets can only be created for debit categories"
        )

    finally:
        app.dependency_overrides.clear()


def test_create_budget_requires_authentication(db):
    user = create_user(db)
    category = create_category(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/budgets",
            json={
                "category_id": str(category.id),
                "name": "Food",
                "amount": "100000.00",
            },
        )

        assert response.status_code == 401

    finally:
        app.dependency_overrides.clear()


def test_list_budgets_only_returns_users_budgets(db):
    user = create_user(db)
    other_user = create_user(db)

    user_category = create_category(
        db,
        user,
        name="My Food",
    )
    other_category = create_category(
        db,
        other_user,
        name="Other Food",
    )

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        user_headers = auth_headers(user)

        response = client.post(
            "/budgets",
            headers=user_headers,
            json={
                "category_id": str(user_category.id),
                "name": "My Food Budget",
                "amount": "100000.00",
            },
        )

        assert response.status_code == 201

        response = client.post(
            "/budgets",
            headers=auth_headers(other_user),
            json={
                "category_id": str(other_category.id),
                "name": "Other Food Budget",
                "amount": "50000.00",
            },
        )

        assert response.status_code == 201

        response = client.get(
            "/budgets",
            headers=user_headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["name"] == "My Food Budget"
        assert data[0]["category_id"] == str(user_category.id)

    finally:
        app.dependency_overrides.clear()


def test_list_budgets_requires_authentication(db):
    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.get("/budgets")

        assert response.status_code == 401

    finally:
        app.dependency_overrides.clear()


def test_budget_status_returns_current_month_spending(db):
    user = create_user(db)
    category = create_category(db, user)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        headers = auth_headers(user)

        response = client.post(
            "/budgets",
            headers=headers,
            json={
                "category_id": str(category.id),
                "name": "Food",
                "amount": "100000.00",
            },
        )

        assert response.status_code == 201

        transaction = Transaction(
            account_id=account.id,
            category_id=category.id,
            transaction_type=TransactionType.DEBIT,
            amount=Decimal("50000.00"),
            description="Restaurant",
            merchant="Restaurant",
            transaction_date=datetime.now(UTC),
        )

        db.add(transaction)
        db.commit()

        response = client.get(
            "/budgets/status",
            headers=headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1

        result = data[0]

        assert result["category"] == "Food"
        assert Decimal(result["budget"]) == Decimal("100000.00")
        assert Decimal(result["spent"]) == Decimal("50000.00")
        assert Decimal(result["remaining"]) == Decimal("50000.00")
        assert result["percent_used"] == 50
        assert result["status"] == "GOOD"

    finally:
        app.dependency_overrides.clear()


def test_budget_status_requires_authentication(db):
    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.get("/budgets/status")

        assert response.status_code == 401

    finally:
        app.dependency_overrides.clear()
