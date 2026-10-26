from autoparts_core.core.enums import DuplicateOutcome
from autoparts_core.dedupe.engine import ListingFingerprint, compare_listings


def _fp(**kwargs):
    base = dict(
        id=1,
        source_id="fixture",
        source_listing_id="a",
        canonical_url="https://example.com/a",
        seller_id=1,
        seller_name="S",
        oem="3G1941007A",
        title="Headlight left VW Passat B8",
        price=214.0,
        currency="EUR",
        country="DE",
    )
    base.update(kwargs)
    return ListingFingerprint(**base)


def test_exact_url_duplicate():
    a = _fp(id=1)
    b = _fp(id=2, source_listing_id="b")
    m = compare_listings(a, b)
    assert m.outcome == DuplicateOutcome.EXACT_DUPLICATE


def test_oem_alone_not_duplicate():
    a = _fp(id=1, seller_id=1, title="Offer A different words entirely xyz")
    b = _fp(
        id=2,
        source_listing_id="other",
        canonical_url="https://example.com/other",
        seller_id=2,
        seller_name="Other",
        title="Completely unrelated title abc",
        price=999.0,
        country="PL",
    )
    m = compare_listings(a, b)
    assert m.outcome == DuplicateOutcome.NOT_DUPLICATE
    assert "oem_alone_insufficient" in m.reasons
