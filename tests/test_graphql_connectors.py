import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from autoparts_core.connectors.graphql_client import GraphQLClient, GraphQLError
from autoparts_core.connectors.nine99_md import Nine99MdConnector
from autoparts_core.connectors.olx_graphql import OlxGraphQLConnector
from autoparts_core.connectors.registry import default_live_source_ids, list_connectors, load_source_catalog
from autoparts_core.security.ssrf import validate_public_url


def test_catalog_lists_live_graphql_sources():
    catalog = {s["id"]: s for s in load_source_catalog()}
    assert catalog["nine99_md"]["status"] == "operational"
    assert catalog["olx_ua"]["status"] == "operational"
    assert "olx_pl" in default_live_source_ids()


def test_registry_marks_live_connectors_operational():
    rows = {r["source_id"]: r for r in list_connectors()}
    assert rows["nine99_md"]["operational"] is True
    assert rows["olx_ua"]["operational"] is True
    assert rows["olx_pl"]["operational"] is True
    assert rows["olx_ro"]["operational"] is True
    assert rows["autodoc"]["operational"] is False


def test_graphql_client_rejects_ssrf():
    with pytest.raises(ValueError):
        GraphQLClient("http://127.0.0.1/graphql")


def test_graphql_client_refuses_captcha_html():
    client = GraphQLClient("https://example.com/graphql")
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.headers = {"content-type": "text/html"}
    mock_resp.text = "<html>Just a moment...</html>"
    mock_resp.json.side_effect = ValueError("no json")
    with patch("httpx.Client") as client_cls:
        inst = client_cls.return_value.__enter__.return_value
        inst.post.return_value = mock_resp
        with pytest.raises(GraphQLError, match="CAPTCHA"):
            client.execute("{ __typename }")


def test_nine99_parse_listing():
    fixture = {
        "id": "105003823",
        "title": "Passat B8 molding",
        "state": "AD_STATE_PUBLIC",
        "subCategory": {"id": 674, "title": {"translated": "Piese"}, "url": "transport/spare-parts-for-cars"},
        "owner": {"id": "abc", "login": "seller1"},
        "groups": [
            {
                "title": "Preț",
                "controls": [
                    {
                        "type": "CONTROL_TYPE_PRICE",
                        "title": "Preț",
                        "feature": {
                            "id": 2,
                            "type": "FEATURE_PRICE",
                            "value": {"value": 55, "unit": "UNIT_EUR"},
                        },
                    }
                ],
            }
        ],
    }
    parsed = Nine99MdConnector().parse_listing(fixture)
    assert parsed.price_amount == 55.0
    assert parsed.price_currency == "EUR"
    assert parsed.country == "MD"
    assert parsed.is_demo_data is False
    assert "105003823" in parsed.canonical_url


def test_olx_parse_listing():
    doc = {
        "id": 767151946,
        "title": "фара Passat B8",
        "url": "https://www.olx.ua/d/uk/obyavlenie/fara-IDPUTgu.html",
        "status": "active",
        "business": True,
        "description": "Test<br />line",
        "category": {"id": 2550, "type": "automotive"},
        "contact": {"name": "Seller", "phone": True, "chat": True},
        "location": {"city": {"name": "Kyiv"}, "region": {"name": "Kyiv"}},
        "params": [
            {
                "key": "price",
                "type": "price",
                "value": {"__typename": "PriceParam", "value": 350, "currency": "UAH", "label": "350 грн."},
            },
            {
                "key": "state",
                "value": {"__typename": "GenericParam", "key": "used", "label": "Вживане"},
            },
        ],
        "photos": [{"link": "https://cdn.example/img;s={width}x{height}"}],
        "user": {"id": 1, "name": "Seller", "company_name": "Shop"},
    }
    parsed = OlxGraphQLConnector("olx_ua").parse_listing(doc)
    assert parsed.price_amount == 350.0
    assert parsed.price_currency == "UAH"
    assert parsed.seller.get("phone_available") is True
    assert parsed.seller.get("public_phone") is None  # never fabricate
    assert parsed.image_urls[0].endswith("800x600")
    assert parsed.is_demo_data is False


@pytest.mark.live
def test_live_olx_ua_search():
    """Opt-in: RUN_LIVE_GRAPHQL=1 pytest -m live"""
    import os

    if os.environ.get("RUN_LIVE_GRAPHQL") != "1":
        pytest.skip("live GraphQL disabled")
    c = OlxGraphQLConnector("olx_ua")
    hits = c.search("фара Passat B8", pagination={"limit": 3})
    assert hits
    doc = c.fetch_listing(str(hits[0].url))
    parsed = c.parse_listing(doc)
    assert parsed.title
    assert parsed.canonical_url.startswith("http")


@pytest.mark.live
def test_live_999_search():
    import os

    if os.environ.get("RUN_LIVE_GRAPHQL") != "1":
        pytest.skip("live GraphQL disabled")
    c = Nine99MdConnector()
    hits = c.search("far Passat", pagination={"limit": 3})
    assert isinstance(hits, list)
    # may be empty for narrow query; health check must pass
    assert c.health_check()["ok"] is True
