from unittest.mock import MagicMock, patch

import pytest

from autoparts_core.connectors.flagma_ua import FlagmaUaConnector
from autoparts_core.connectors.jsonld_catalog import JsonLdCatalogConnector
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


def test_catalog_includes_ua_jsonld_sources():
    catalog = {s["id"]: s for s in load_source_catalog()}
    assert catalog["prom_ua"]["status"] == "operational"
    assert catalog["flagma_ua"]["status"] == "operational"
    assert catalog["bazar_bg"]["status"] == "operational"
    assert catalog["satu_kz"]["status"] == "operational"
    assert catalog["deal_by"]["status"] == "operational"
    assert "prom_ua" in default_live_source_ids()
    assert "flagma_ua" in default_live_source_ids()
    assert "bazar_bg" in default_live_source_ids()


def test_registry_includes_prom_and_flagma():
    rows = {r["source_id"]: r for r in list_connectors()}
    assert rows["prom_ua"]["operational"] is True
    assert rows["flagma_ua"]["operational"] is True
    assert rows["bazar_bg"]["operational"] is True
    assert rows["satu_kz"]["operational"] is True
    assert rows["deal_by"]["operational"] is True
    assert "rozetka" not in rows


def test_prom_parse_listing():
    products = extract_jsonld_products(SAMPLE_HTML)
    parsed = PromUaConnector().parse_listing(products[0])
    assert parsed.source_listing_id == "1234567890123456789"
    assert parsed.price_amount == 1500.0
    assert parsed.price_currency == "UAH"
    assert parsed.country == "UA"
    assert parsed.manufacturer_as_stated == "VAG"
    assert parsed.oem_as_stated == "OEM-1"
    assert parsed.is_demo_data is False
    assert parsed.canonical_url.startswith("https://prom.ua/")


def test_flagma_parse_listing():
    parsed = FlagmaUaConnector().parse_listing(FLAGMA_PRODUCT)
    assert parsed.source_listing_id == "16771097"
    assert parsed.price_amount == 6000.0
    assert parsed.price_currency == "UAH"
    assert parsed.country == "UA"
    assert parsed.is_demo_data is False


BAZAR_ITEMLIST_HTML = """
<script type="application/ld+json">
{"@type":"ItemList","itemListElement":[{
  "@type":"ListItem","position":1,
  "item":{"@type":"Product","name":"Фар Passat B6",
    "url":"https://bazar.bg/obiava-54470098/far-passat",
    "image":"//cdn.example/a.webp",
    "offers":{"@type":"Offer","price":50,"priceCurrency":"EUR",
      "seller":{"@type":"Organization","name":"User 1","url":"https://bazar.bg/ads/user/1"}}}
}]}
</script>
"""


def test_bazar_itemlist_extract_and_parse():
    products = extract_jsonld_products(BAZAR_ITEMLIST_HTML)
    assert len(products) == 1
    parsed = JsonLdCatalogConnector("bazar_bg").parse_listing(products[0])
    assert parsed.source_listing_id == "54470098"
    assert parsed.price_amount == 50.0
    assert parsed.price_currency == "EUR"
    assert parsed.country == "BG"
    assert parsed.image_urls[0].startswith("https://")
    assert parsed.seller.get("display_name") == "User 1"


def test_satu_parse_listing():
    doc = {
        "@type": "Product",
        "name": "Фара Passat",
        "url": "https://satu.kz/p127273259-fara.html",
        "sku": "X1",
        "offers": {"@type": "Offer", "price": "1000", "priceCurrency": "KZT", "url": "https://satu.kz/p127273259-fara.html"},
    }
    parsed = JsonLdCatalogConnector("satu_kz").parse_listing(doc)
    assert parsed.source_listing_id == "127273259"
    assert parsed.price_amount == 1000.0
    assert parsed.price_currency == "KZT"
    assert parsed.country == "KZ"


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
    doc = c.fetch_listing(str(hits[0].url))
    parsed = c.parse_listing(doc)
    assert parsed.title
    assert parsed.price_amount is not None
    assert parsed.canonical_url.startswith("https://prom.ua/")


@pytest.mark.live
def test_live_flagma_ua_search():
    import os

    if os.environ.get("RUN_LIVE_GRAPHQL") != "1":
        pytest.skip("live catalog disabled")
    c = FlagmaUaConnector()
    hits = c.search("фара Passat", pagination={"limit": 3})
    assert hits
    doc = c.fetch_listing(str(hits[0].url))
    parsed = c.parse_listing(doc)
    assert parsed.title
    assert parsed.canonical_url.startswith("https://flagma.ua/")


@pytest.mark.live
def test_live_bazar_bg_search():
    import os

    if os.environ.get("RUN_LIVE_GRAPHQL") != "1":
        pytest.skip("live catalog disabled")
    c = JsonLdCatalogConnector("bazar_bg")
    hits = c.search("фар Passat", pagination={"limit": 3})
    assert hits
    parsed = c.parse_listing(c.fetch_listing(str(hits[0].url)))
    assert parsed.price_amount is not None
    assert parsed.canonical_url.startswith("https://bazar.bg/")


@pytest.mark.live
def test_live_satu_kz_search():
    import os

    if os.environ.get("RUN_LIVE_GRAPHQL") != "1":
        pytest.skip("live catalog disabled")
    c = JsonLdCatalogConnector("satu_kz")
    hits = c.search("фара passat", pagination={"limit": 3})
    assert hits
    parsed = c.parse_listing(c.fetch_listing(str(hits[0].url)))
    assert parsed.price_amount is not None
