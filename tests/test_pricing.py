from decimal import Decimal

from autoparts_core.pricing.fx import convert, get_rate
from autoparts_core.pricing.landed import build_price_breakdown


def test_fx_fixture_warning():
    amount, quote, warnings = convert(Decimal("100"), "EUR", "USD", allow_fixture=True)
    assert amount is not None
    assert quote is not None
    assert quote.is_fixture
    assert any("fixture" in w.lower() for w in warnings)


def test_missing_rate_not_guessed():
    amount, quote, warnings = convert(Decimal("100"), "EUR", "ZZZ", allow_fixture=True)
    assert amount is None
    assert quote is None
    assert warnings


def test_unknown_shipping_not_zero():
    br = build_price_breakdown(item_amount=100, item_currency="EUR", shipping_amount=None)
    assert "shipping" in br.unknown_cost_components
    assert any("not treated as zero" in w.lower() for w in br.warnings)
    assert br.estimated_landed is not None
    assert br.estimated_landed.amount == Decimal("100")


def test_identity_rate():
    q = get_rate("EUR", "EUR")
    assert q is not None
    assert q.rate == Decimal("1")
