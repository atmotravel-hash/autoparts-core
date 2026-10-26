from unittest.mock import MagicMock, patch

import pytest

from autoparts_core.connectors.autoria import AutoRiaConnector
from autoparts_core.connectors.registry import get_registry, list_connectors


def test_autoria_without_key_not_operational(monkeypatch):
    monkeypatch.delenv("AUTORIA_API_KEY", raising=False)
    # reset registry singleton
    import autoparts_core.connectors.registry as reg

    reg._REGISTRY = None
    from autoparts_core.config.settings import Settings

    monkeypatch.setattr(
        "autoparts_core.connectors.autoria.get_settings",
        lambda: Settings(autoria_api_key=None),
    )
    c = AutoRiaConnector()
    caps = c.get_capabilities()
    assert caps.operational is False
    assert caps.health_status == "credentials_missing"
    hc = c.health_check()
    assert hc["ok"] is False


def test_autoria_parse_listing():
    doc = {
        "userId": 1,
        "locationCityName": "Київ",
        "EUR": 1200,
        "UAH": 55000,
        "USD": 1300,
        "title": "Volkswagen Passat B8 на запчастини",
        "markName": "Volkswagen",
        "modelName": "Passat",
        "linkToView": "/uk/auto_12345678.html",
        "userPhoneData": {"phone": "(067) 111-22-33"},
        "photoData": {"seoLinkM": "https://cdn.riastatic.com/photo.jpg", "count": 1},
        "autoData": {
            "autoId": 12345678,
            "year": 2017,
            "description": "Донор",
            "isSold": False,
            "categoryId": 1,
        },
        "autoInfoBar": {"onRepairParts": True},
    }
    parsed = AutoRiaConnector().parse_listing(doc)
    assert parsed.source_listing_id == "12345678"
    assert parsed.price_currency == "EUR"
    assert parsed.price_amount == 1200.0
    assert parsed.condition == "FOR_PARTS"
    assert parsed.country == "UA"
    assert "auto.ria.com" in parsed.canonical_url
    assert parsed.is_demo_data is False


def test_registry_excludes_autoria_by_default():
    import autoparts_core.connectors.registry as reg

    reg._REGISTRY = None
    rows = {r["source_id"]: r for r in list_connectors()}
    assert "auto_ria" not in rows


def test_deferred_catalog_lists_autoria():
    from autoparts_core.connectors.registry import load_deferred_sources

    ids = {d["id"] for d in load_deferred_sources()}
    assert "auto_ria" in ids
    assert "allegro" in ids
