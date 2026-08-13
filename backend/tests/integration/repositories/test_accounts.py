from app.accounts.domain.models import Account
from app.accounts.repository import AccountRepository
from tests.factories.user_factory import UserFactory


def test_create_account(db):
    user = UserFactory()

    db.add(user)
    db.commit()
    db.refresh(user)

    repo = AccountRepository(db)

    account = Account(
        name="Savings",
        institution="GTBank",
        currency="NGN",
        opening_balance=1000,
        user_id=user.id,
    )

    repo.create(account)

    db.commit()

    saved = repo.get_by_id(account.id)

    assert saved is not None
    assert saved.name == "Savings"
    assert saved.user_id == user.id