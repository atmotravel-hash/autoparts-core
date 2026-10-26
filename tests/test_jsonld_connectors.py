from unittest.mock import MagicMock, patch

import pytest

from autoparts_core.connectors.flagma_ua import FlagmaUaConnector
from autoparts_core.connectors.jsonld_client import (
    JsonLdError,
    JsonLdHtmlClient,
    extract_jsonld_products,
    offer_price,
)
from autoparts_core.connectors.prom_ua import PromUaConnector
from autoparts_core.connectors.registry import default_live_source_ids, list_connectors, load_source_catalog


SAMPLE_HTML = """
<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org/","@type":"Product","name":"Фара Passat B8",
 "url":"https://prom.ua/ua/m1234567890123456789-fara.html",
 "sku":"OEM-1","brand":{"@type":"Brand","name":"VAG"},
 "image":["https://images.prom.ua/1.jpg"],
 "offers":{"@type":"Offer","price":"1500","priceCurrency":"UAH",
   "availability":"http://schema.org/InStock",
   "url":"https://prom.ua/ua/m1234567890123456789-fara.html"}}
</script>
</head></html>
"""

FLAGMA_PRODUCT = {
    "@type": "Product",
    "name": "Passat b8 фара",
    "description": "Нова фара",
    "image": ["https://img01.flagma.ua/photo/x.jpg"],
    "offers": {
        "@type": "Offer",
        "url": "https://flagma.ua/uk/passat-b8-fara-o16771097.html",
        "price": 6000,
        "priceCurrency": "uah",
    },
}


def test_extract_jsonld_products():
    products = extract_jsonld_products(SAMPLE_HTML)
    assert len(products) == 1
    amount, currency = offer_price(products[0])
    assert amount == 1500.0
    assert currency == "UAH"


def test_product_scope_ua_md_ro_only():
    catalog = {s["id"]: s for s in load_source_catalog()}
    assert catalog["prom_ua"]["status"] == "operational"
    assert catalog["flagma_ua"]["status"] == "operational"
    assert catalog["prom_md"]["status"] == "operational"
    assert catalog["olx_ro"]["status"] == "operational"
    assert catalog["nine99_md"]["status"] == "operational"
    live = set(default_live_source_ids())
    assert live == {
        "olx_ua",
        "prom_ua",
        "flagma_ua",
        "nine99_md",
        "prom_md",
        "olx_ro",
    }
    assert "bazar_bg" not in live
    assert "olx_pl" not in live


def test_registry_scope():
    rows = {r["source_id"]: r for r in list_connectors()}
    assert rows["prom_ua"]["operational"] is True
    assert rows["flagma_ua"]["operational"] is True
    assert rows["prom_md"]["operational"] is True
    assert "bazar_bg" not in rows
    assert "olx_pl" not in rows
    assert "olx_bg" not in rows
    assert "olx_pt" not in rows
    assert "autodoc" not in rows
    assert "ebay" not in rows


def test_prom_parse_listing():
    products = extract_jsonld_products(SAMPLE_HTML)
    parsed = PromUaConnector().parse_listing(products[0])
    assert parsed.source_listing_id == "1234567890123456789"
    assert parsed.price_amount == 1500.0
    assert parsed.country == "UA"


def test_flagma_parse_listing():
    parsed = FlagmaUaConnector().parse_listing(FLAGMA_PRODUCT)
    assert parsed.source_listing_id == "16771097"
    assert parsed.price_currency == "UAH"


def test_itemlist_extract_still_works():
    html = """
    <script type="application/ld+json">
    {"@type":"ItemList","itemListElement":[{"@type":"ListItem","item":
      {"@type":"Product","name":"X","url":"https://example.com/a",
       "offers":{"@type":"Offer","price":10,"priceCurrency":"UAH"}}}]}
    </script>
    """
    products = extract_jsonld_products(html)
    assert len(products) == 1


def test_jsonld_client_refuses_captcha_html():
    client = JsonLdHtmlClient(origin="https://example.com")
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.headers = {"content-type": "text/html"}
    mock_resp.text = "<html>Just a moment...</html>"
    with patch("httpx.Client") as client_cls:
        inst = client_cls.return_value.__enter__.return_value
        inst.get.return_value = mock_resp
        with pytest.raises(JsonLdError, match="CAPTCHA"):
            client.get_html("https://example.com/search")


def test_jsonld_client_rejects_ssrf():
    with pytest.raises(ValueError):
        JsonLdHtmlClient(origin="http://127.0.0.1")


@pytest.mark.live
def test_live_prom_ua_search():
    import os

    if os.environ.get("RUN_LIVE_GRAPHQL") != "1":
        pytest.skip("live catalog disabled")
    c = PromUaConnector()
    hits = c.search("фара Passat B8", pagination={"limit": 3})
    assert hits
