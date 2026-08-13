from decimal import Decimal

from fastapi.testclient import TestClient

from tests.factories.account_factory import AccountFactory
from tests.factories.transaction_factory import TransactionFactory
from app.auth.security import create_access_token
from app.db.session import get_db
from app.main import app
from tests.factories.user_factory import UserFactory


def create_user(db):
    user = UserFactory()
    db.add(user)
    db.flush()
    return user


def auth_headers(user):
    token = create_access_token(subject=str(user.id))

    return {
        "Authorization": f"Bearer {token}",
    }


def override_db(db):
    def _override_get_db():
        yield db

    return _override_get_db


def test_create_goal(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/goals",
            headers=auth_headers(user),
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["name"] == "Emergency Fund"
        assert Decimal(data["target_amount"]) == Decimal("100000.00")
        assert Decimal(data["current_amount"]) == Decimal("0.00")
        assert data["status"] == "active"
        assert data["target_date"] is None
        assert data["id"] is not None

    finally:
        app.dependency_overrides.clear()


def test_list_goals_only_returns_authenticated_users_goals(db):
    user = create_user(db)
    other_user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        user_headers = auth_headers(user)
        other_headers = auth_headers(other_user)

        response = client.post(
            "/goals",
            headers=user_headers,
            json={
                "name": "My Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert response.status_code == 201

        response = client.post(
            "/goals",
            headers=other_headers,
            json={
                "name": "Other User Goal",
                "target_amount": "50000.00",
            },
        )

        assert response.status_code == 201

        response = client.get(
            "/goals",
            headers=user_headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["name"] == "My Emergency Fund"

    finally:
        app.dependency_overrides.clear()


def test_get_goal_returns_owned_goal(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        response = client.get(
            f"/goals/{goal_id}",
            headers=headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == goal_id
        assert data["name"] == "Emergency Fund"

    finally:
        app.dependency_overrides.clear()


def test_get_goal_rejects_another_user(db):
    owner = create_user(db)
    other_user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        create_response = client.post(
            "/goals",
            headers=auth_headers(owner),
            json={
                "name": "Private Goal",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        response = client.get(
            f"/goals/{goal_id}",
            headers=auth_headers(other_user),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Goal not found"

    finally:
        app.dependency_overrides.clear()


def test_add_contribution(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={
                "amount": "25000.00",
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert Decimal(data["amount"]) == Decimal("25000.00")

    finally:
        app.dependency_overrides.clear()

def test_add_contribution_from_transaction(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        # Create account
        account = AccountFactory(user=user)
        db.add(account)
        db.flush()

        # Create transaction
        transaction = TransactionFactory(
            account=account,
            account_id=account.id,
            amount=Decimal("25000.00"),
        )
        db.add(transaction)
        db.flush()

        # Create goal
        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        # Link transaction to goal
        response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={
                "amount": "25000.00",
                "transaction_id": str(transaction.id),
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["goal_id"] == goal_id
        assert data["transaction_id"] == str(transaction.id)
        assert Decimal(data["amount"]) == Decimal("25000.00")

    finally:
        app.dependency_overrides.clear()


def test_goal_progress(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={"amount": "25000.00"},
        )

        assert response.status_code == 201

        response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={"amount": "15000.00"},
        )

        assert response.status_code == 201

        response = client.get(
            f"/goals/{goal_id}/progress",
            headers=headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert Decimal(data["saved"]) == Decimal("40000.00")
        assert Decimal(data["remaining"]) == Decimal("60000.00")
        assert Decimal(data["percent"]) == Decimal("40.00")
        assert data["goal"]["id"] == goal_id

    finally:
        app.dependency_overrides.clear()


def test_rejects_invalid_contribution(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={
                "amount": "0",
            },
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Contribution amount must be greater than zero"
        )

    finally:
        app.dependency_overrides.clear()


def test_delete_goal(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Delete Me",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        response = client.delete(
            f"/goals/{goal_id}",
            headers=headers,
        )

        assert response.status_code == 204
        assert response.content == b""

        response = client.get(
            f"/goals/{goal_id}",
            headers=headers,
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Goal not found"

    finally:
        app.dependency_overrides.clear()


def test_unauthenticated_request_is_rejected(db):
    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.get("/goals")

        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    finally:
        app.dependency_overrides.clear()


def test_goal_projection(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
                "target_date": "2027-03-01",
            },
        )

        assert create_response.status_code == 201

        goal_id = create_response.json()["id"]

        contribution_response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={
                "amount": "40000.00",
            },
        )

        assert contribution_response.status_code == 201

        response = client.post(
            f"/goals/{goal_id}/projection",
            headers=headers,
            json={
                "monthly_contribution": "10000.00",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["goal"]["id"] == goal_id
        assert Decimal(data["goal"]["current_amount"]) == Decimal("0.00")
        assert data["will_reach"] is True
        assert Decimal(data["projected_amount"]) > Decimal("100000.00")
        assert Decimal(data["required_monthly"]) > Decimal("0")
        assert data["months_remaining"] == 7

    finally:
        app.dependency_overrides.clear()


def test_transaction_cannot_be_linked_twice(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        account = AccountFactory(user=user)
        db.add(account)
        db.flush()

        transaction = TransactionFactory(
            account=account,
            account_id=account.id,
            amount=Decimal("25000.00"),
        )
        db.add(transaction)
        db.flush()

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201
        goal_id = create_response.json()["id"]

        first_response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={
                "amount": "25000.00",
                "transaction_id": str(transaction.id),
            },
        )

        assert first_response.status_code == 201

        second_response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={
                "amount": "25000.00",
                "transaction_id": str(transaction.id),
            },
        )

        assert second_response.status_code == 400
        assert (
            second_response.json()["detail"]
            == "Transaction is already linked to a goal"
        )

    finally:
        app.dependency_overrides.clear()

def test_contribution_cannot_exceed_transaction_amount(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        account = AccountFactory(user=user)
        db.add(account)
        db.flush()

        transaction = TransactionFactory(
            account=account,
            account_id=account.id,
            amount=Decimal("10000.00"),
        )
        db.add(transaction)
        db.flush()

        create_response = client.post(
            "/goals",
            headers=headers,
            json={
                "name": "Emergency Fund",
                "target_amount": "100000.00",
            },
        )

        assert create_response.status_code == 201
        goal_id = create_response.json()["id"]

        response = client.post(
            f"/goals/{goal_id}/contributions",
            headers=headers,
            json={
                "amount": "15000.00",
                "transaction_id": str(transaction.id),
            },
        )

        assert response.status_code == 400
        assert (
            response.json()["detail"]
            == "Contribution cannot exceed transaction amount"
        )

    finally:
        app.dependency_overrides.clear()