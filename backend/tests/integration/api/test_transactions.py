from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.auth.security import create_access_token
from app.db.session import get_db
from app.main import app

from app.merchants.service import MerchantService
from tests.factories.account_factory import AccountFactory
from tests.factories.user_factory import UserFactory


def create_user(db):
    user = UserFactory()
    db.add(user)
    db.flush()
    return user


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


def create_account(db, user):
    account = AccountFactory(user=user)
    db.add(account)
    db.flush()
    return account


def test_create_transaction(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/transactions",
            headers=auth_headers(user),
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Lunch",
                "merchant": "Chicken Republic",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert response.status_code == 201

        data = response.json()

        assert data["id"] is not None
        assert data["account_id"] == str(account.id)
        assert data["transaction_type"] == "debit"
        assert Decimal(data["amount"]) == Decimal("2500.00")
        assert data["description"] == "Lunch"
        assert data["merchant"] == "Chicken Republic"

    finally:
        app.dependency_overrides.clear()


def test_create_transaction_rejects_another_users_account(db):
    owner = create_user(db)
    other_user = create_user(db)

    account = create_account(db, owner)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/transactions",
            headers=auth_headers(other_user),
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Unauthorized transaction",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Account not found"

    finally:
        app.dependency_overrides.clear()


def test_create_transaction_requires_authentication(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/transactions",
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Lunch",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert response.status_code == 401

    finally:
        app.dependency_overrides.clear()


def test_list_transactions_only_returns_users_transactions(db):
    user = create_user(db)
    other_user = create_user(db)

    account = create_account(db, user)
    other_account = create_account(db, other_user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        headers = auth_headers(user)

        user_transaction = client.post(
            "/transactions",
            headers=headers,
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "1000.00",
                "description": "My transaction",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert user_transaction.status_code == 201

        other_transaction = client.post(
            "/transactions",
            headers=auth_headers(other_user),
            json={
                "account_id": str(other_account.id),
                "transaction_type": "debit",
                "amount": "5000.00",
                "description": "Other user's transaction",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert other_transaction.status_code == 201

        response = client.get(
            "/transactions",
            headers=headers,
        )

        print("STATUS:", response.status_code); print("BODY:", response.json()); assert response.status_code == 200

        data = response.json()

        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["description"] == "My transaction"

    finally:
        app.dependency_overrides.clear()


def test_list_transactions_filters_by_transaction_type(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        headers = auth_headers(user)

        for transaction_type, description in [
            ("credit", "Salary"),
            ("debit", "Lunch"),
            ("debit", "Transport"),
        ]:
            response = client.post(
                "/transactions",
                headers=headers,
                json={
                    "account_id": str(account.id),
                    "transaction_type": transaction_type,
                    "amount": "1000.00",
                    "description": description,
                    "transaction_date": datetime.now(UTC).isoformat(),
                },
            )

            assert response.status_code == 201

        response = client.get(
            "/transactions",
            headers=headers,
            params={"transaction_type": "debit"},
        )

        print("STATUS:", response.status_code)
        print("BODY:", response.json())

        assert response.status_code == 200

        data = response.json()

        assert len(data["items"]) == 2
        assert data["total"] == 2
        assert data["limit"] == 50
        assert data["offset"] == 0

        assert all(
            transaction["transaction_type"] == "debit"
            for transaction in data["items"]
        )

    finally:
        app.dependency_overrides.clear()


def test_create_transaction_rejects_zero_amount(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.post(
            "/transactions",
            headers=auth_headers(user),
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "0.00",
                "description": "Invalid transaction",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()

def test_get_transaction(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/transactions",
            headers=headers,
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Lunch",
                "merchant": "Chicken Republic",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert create_response.status_code == 201

        transaction_id = create_response.json()["id"]

        response = client.get(
            f"/transactions/{transaction_id}",
            headers=headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == transaction_id
        assert data["account_id"] == str(account.id)
        assert data["transaction_type"] == "debit"
        assert Decimal(data["amount"]) == Decimal("2500.00")
        assert data["description"] == "Lunch"

    finally:
        app.dependency_overrides.clear()


def test_get_transaction_rejects_another_users_transaction(db):
    owner = create_user(db)
    other_user = create_user(db)

    account = create_account(db, owner)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        create_response = client.post(
            "/transactions",
            headers=auth_headers(owner),
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Private transaction",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert create_response.status_code == 201

        transaction_id = create_response.json()["id"]

        response = client.get(
            f"/transactions/{transaction_id}",
            headers=auth_headers(other_user),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found"

    finally:
        app.dependency_overrides.clear()


def test_get_transaction_returns_404_for_unknown_transaction(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        unknown_transaction_id = (
            "00000000-0000-0000-0000-000000000000"
        )

        response = client.get(
            f"/transactions/{unknown_transaction_id}",
            headers=auth_headers(user),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found"

    finally:
        app.dependency_overrides.clear()


def test_list_transactions_filters_by_multiple_fields(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        transactions = [
            {
                "transaction_type": "debit",
                "amount": "1500.00",
                "description": "Lunch at Chicken Republic",
                "merchant": "Chicken Republic",
                "transaction_date": "2026-08-01T12:00:00Z",
            },
            {
                "transaction_type": "debit",
                "amount": "5000.00",
                "description": "Uber ride",
                "merchant": "Uber",
                "transaction_date": "2026-08-02T12:00:00Z",
            },
            {
                "transaction_type": "credit",
                "amount": "100000.00",
                "description": "Salary",
                "merchant": "Employer",
                "transaction_date": "2026-08-03T12:00:00Z",
            },
        ]

        for payload in transactions:
            payload["account_id"] = str(account.id)

            response = client.post(
                "/transactions",
                headers=headers,
                json=payload,
            )

            assert response.status_code == 201

        response = client.get(
            "/transactions",
            headers=headers,
            params={
                "transaction_type": "debit",
                "min_amount": "1000",
                "max_amount": "2000",
                "merchant": "chicken",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["description"] == "Lunch at Chicken Republic"

    finally:
        app.dependency_overrides.clear()

def test_list_transactions_supports_pagination(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        for i in range(5):
            response = client.post(
                "/transactions",
                headers=headers,
                json={
                    "account_id": str(account.id),
                    "transaction_type": "debit",
                    "amount": f"{(i + 1) * 1000}.00",
                    "description": f"Transaction {i + 1}",
                    "transaction_date": datetime.now(UTC).isoformat(),
                },
            )

            assert response.status_code == 201

        response = client.get(
            "/transactions",
            headers=headers,
            params={
                "limit": 2,
                "offset": 0,
            },
        )

        assert response.status_code == 200

        first_page = response.json()

        assert len(first_page["items"]) == 2
        assert first_page["total"] == 5
        assert first_page["limit"] == 2
        assert first_page["offset"] == 0

        response = client.get(
            "/transactions",
            headers=headers,
            params={
                "limit": 2,
                "offset": 2,
            },
        )

        assert response.status_code == 200

        second_page = response.json()

        assert len(second_page["items"]) == 2
        assert second_page["total"] == 5
        assert second_page["limit"] == 2
        assert second_page["offset"] == 2
        assert (
            first_page["items"][0]["id"]
            != second_page["items"][0]["id"]
        )
    finally:
        app.dependency_overrides.clear()

def test_list_transactions_rejects_invalid_pagination(db):
    user = create_user(db)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        response = client.get(
            "/transactions",
            headers=auth_headers(user),
            params={"limit": 0},
        )

        assert response.status_code == 422

        response = client.get(
            "/transactions",
            headers=auth_headers(user),
            params={"limit": 101},
        )

        assert response.status_code == 422

        response = client.get(
            "/transactions",
            headers=auth_headers(user),
            params={"offset": -1},
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()

def test_list_transactions_returns_pagination_metadata(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        for i in range(5):
            response = client.post(
                "/transactions",
                headers=headers,
                json={
                    "account_id": str(account.id),
                    "transaction_type": "debit",
                    "amount": "1000.00",
                    "description": f"Transaction {i}",
                    "transaction_date": datetime.now(UTC).isoformat(),
                },
            )

            assert response.status_code == 201

        response = client.get(
            "/transactions",
            headers=headers,
            params={
                "limit": 2,
                "offset": 2,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 2

    finally:
        app.dependency_overrides.clear()


def test_update_transaction(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/transactions",
            headers=headers,
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Original description",
                "merchant": "Original merchant",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert create_response.status_code == 201

        transaction_id = create_response.json()["id"]

        response = client.patch(
            f"/transactions/{transaction_id}",
            headers=headers,
            json={
                "description": "Updated description",
                "amount": "3000.00",
                "merchant": "Updated merchant",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == transaction_id
        assert Decimal(data["amount"]) == Decimal("3000.00")
        assert data["description"] == "Updated description"
        assert data["merchant"] == "Updated Merchant"

    finally:
        app.dependency_overrides.clear()


def test_update_transaction_only_changes_supplied_fields(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        create_response = client.post(
            "/transactions",
            headers=headers,
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Original description",
                "merchant": "Original merchant",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert create_response.status_code == 201

        transaction_id = create_response.json()["id"]

        response = client.patch(
            f"/transactions/{transaction_id}",
            headers=headers,
            json={
                "description": "Updated description",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["description"] == "Updated description"
        assert Decimal(data["amount"]) == Decimal("2500.00")
        assert data["merchant"] == "Original merchant"
        assert data["transaction_type"] == "debit"

    finally:
        app.dependency_overrides.clear()


def test_update_transaction_rejects_another_users_transaction(db):
    owner = create_user(db)
    other_user = create_user(db)

    account = create_account(db, owner)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)

        create_response = client.post(
            "/transactions",
            headers=auth_headers(owner),
            json={
                "account_id": str(account.id),
                "transaction_type": "debit",
                "amount": "2500.00",
                "description": "Private transaction",
                "transaction_date": datetime.now(UTC).isoformat(),
            },
        )

        assert create_response.status_code == 201

        transaction_id = create_response.json()["id"]

        response = client.patch(
            f"/transactions/{transaction_id}",
            headers=auth_headers(other_user),
            json={
                "description": "Malicious update",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found"

    finally:
        app.dependency_overrides.clear()

def test_resolve_normalizes_merchant_name(db):
    service = MerchantService(db)

    merchant = service.resolve(
        merchant="updated merchant",
        description="Some transaction",
    )

    assert merchant.name == "Updated Merchant"

def test_list_transactions_filters_by_multiple_fields(db):
    user = create_user(db)
    account = create_account(db, user)

    app.dependency_overrides[get_db] = override_db(db)

    try:
        client = TestClient(app)
        headers = auth_headers(user)

        transactions = [
            {
                "transaction_type": "debit",
                "amount": "1500.00",
                "description": "Lunch at Chicken Republic",
                "merchant": "Chicken Republic",
                "transaction_date": "2026-08-01T12:00:00Z",
            },
            {
                "transaction_type": "debit",
                "amount": "5000.00",
                "description": "Uber ride",
                "merchant": "Uber",
                "transaction_date": "2026-08-02T12:00:00Z",
            },
            {
                "transaction_type": "credit",
                "amount": "100000.00",
                "description": "Salary",
                "merchant": "Employer",
                "transaction_date": "2026-08-03T12:00:00Z",
            },
        ]

        for payload in transactions:
            payload["account_id"] = str(account.id)

            response = client.post(
                "/transactions",
                headers=headers,
                json=payload,
            )

            assert response.status_code == 201

        response = client.get(
            "/transactions",
            headers=headers,
            params={
                "transaction_type": "debit",
                "min_amount": "1000",
                "max_amount": "2000",
                "merchant": "chicken",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["description"] == "Lunch at Chicken Republic"
        assert data["items"][0]["merchant"] == "Chicken Republic"

    finally:
        app.dependency_overrides.clear()
