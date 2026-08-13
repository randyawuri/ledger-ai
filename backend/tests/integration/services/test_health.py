from app.accounts.domain.models import Account
from app.health.service import FinancialHealthService
from tests.factories.user_factory import UserFactory


def test_health_score(db):
    user = UserFactory()

    db.add(user)
    db.flush()

    account = Account(
        user_id=user.id,
        name="Checking",
        institution="GTBank",
        currency="NGN",
        opening_balance=100000,
    )

    db.add(account)
    db.flush()

    service = FinancialHealthService(db)

    score = service.get_health(user)

    assert score["score"] >= 0