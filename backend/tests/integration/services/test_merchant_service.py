from app.merchants.service import MerchantService


def test_resolve_creates_new_merchant(db):
    service = MerchantService(db)

    merchant = service.resolve(
        merchant="NETFLIX NG",
        description="Netflix subscription",
    )

    assert merchant.id is not None
    assert merchant.name == "Netflix"


def test_resolve_returns_existing_merchant(db):
    service = MerchantService(db)

    first = service.resolve(
        merchant="NETFLIX",
        description="Netflix subscription",
    )

    second = service.resolve(
        merchant="NETFLIX NG",
        description="Netflix subscription",
    )

    assert first.id == second.id
    assert second.name == "Netflix"


def test_resolve_uses_description_when_merchant_missing(db):
    service = MerchantService(db)

    merchant = service.resolve(
        merchant=None,
        description="UBER TRIP 12345",
    )

    assert merchant.name == "Uber"