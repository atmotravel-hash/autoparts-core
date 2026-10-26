"""Parameterized JSON-LD catalog connectors (public search HTML)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

from autoparts_core.connectors.base import ParsedListing, RateLimitStatus, SourceConnector
from autoparts_core.connectors.jsonld_client import (
    JsonLdHtmlClient,
    normalize_offer,
    offer_availability,
    offer_price,
    product_brand,
    product_images,
)
from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit
from autoparts_core.identity.condition import normalize_condition

# Product scope: UA · MD · RO only (bazar_bg deferred).
JSONLD_MARKETS: dict[str, dict[str, Any]] = {
    "prom_md": {
        "source_name": "Prom.md Moldova (JSON-LD catalog)",
        "origin": "https://prom.md",
        "country": "MD",
        "languages": ["ro", "ru", "en"],
        "default_currency": "MDL",
        "search_url": "https://prom.md/search?search_term={query}",
        "id_regex": r"/p(\d+)-",
        "seller_type": "BUSINESS",
        "confidence": 0.86,
        "terms": "Prom-group public search HTML Product JSON-LD.",
    },
}


class JsonLdCatalogConnector(SourceConnector):
    def __init__(self, market_key: str) -> None:
        if market_key not in JSONLD_MARKETS:
            raise ValueError(f"Unknown JSON-LD market: {market_key}")
        self.market_key = market_key
        self.cfg = JSONLD_MARKETS[market_key]
        self.source_id = market_key
        self.source_name = self.cfg["source_name"]
        self._id_re = re.compile(self.cfg["id_regex"], re.IGNORECASE)
        self._client = JsonLdHtmlClient(origin=self.cfg["origin"], min_interval_seconds=0.9)
        self._last_ok: datetime | None = None
        self._cache: dict[str, dict[str, Any]] = {}

    def get_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            source_id=self.source_id,
            source_name=self.source_name,
            supported_countries=[self.cfg["country"]],
            supported_languages=list(self.cfg["languages"]),
            supported_search_modes=["vehicle_part", "oem", "part_name"],
            authentication_required=False,
            rate_limit_notes="Client throttle ~0.9s",
            access_method="PUBLIC_PAGE",
            terms_notes=self.cfg["terms"] + " No CAPTCHA bypass.",
            pagination=True,
            price_capability=True,
            availability_capability=True,
            last_successful_test=self._last_ok,
            health_status="healthy" if self._last_ok else "untested",
            operational=True,
        )

    def health_check(self) -> dict[str, Any]:
        try:
            hits = self.search("passat", pagination={"limit": 1})
            self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
            return {"ok": True, "status": "healthy", "sample_hits": len(hits), "is_demo": False}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "status": "down", "message": str(exc)}

    def get_rate_limit_status(self) -> RateLimitStatus:
        return RateLimitStatus(limited=False, notes="soft client throttle 0.9s")

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        filters = filters or {}
        pagination = pagination or {}
        countries = filters.get("country")
        if countries and self.cfg["country"] not in countries:
            return []
        limit = min(int(pagination.get("limit", 20)), 40)
        offset = int(pagination.get("offset", 0))
        url = self.cfg["search_url"].format(query=quote_plus(query))
        products = self._client.fetch_products(url)
        self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
        hits: list[SearchHit] = []
        for i, product in enumerate(products[:limit]):
            offers = normalize_offer(product)
            canon = str(product.get("url") or offers.get("url") or "")
            if canon.startswith("//"):
                canon = "https:" + canon
            if not canon:
                continue
            lid = self._listing_id(canon, product)
            self._cache[canon] = product
            self._cache[lid] = product
            price, currency = offer_price(product)
            snippet = self.cfg["origin"].replace("https://", "")
            if price is not None:
                snippet += f" · {price:g} {(currency or self.cfg['default_currency']).upper()}"
            hits.append(
                SearchHit(
                    url=canon,
                    title=product.get("name"),
                    rank=offset + i + 1,
                    snippet=snippet,
                    country=self.cfg["country"],
                    language=self.cfg["languages"][0],
                )
            )
        return hits

    def fetch_listing(self, identifier_or_url: str) -> dict[str, Any]:
        key = identifier_or_url.strip()
        if key in self._cache:
            return self._cache[key]
        m = self._id_re.search(key)
        if m and m.group(1) in self._cache:
            return self._cache[m.group(1)]
        if key.startswith("http") or key.startswith("//"):
            url = ("https:" + key) if key.startswith("//") else key
            products = self._client.fetch_products(url)
            if not products:
                raise KeyError(f"No Product JSON-LD: {key}")
            product = products[0]
            offers = normalize_offer(product)
            canon = str(product.get("url") or offers.get("url") or url)
            if canon.startswith("//"):
                canon = "https:" + canon
            lid = self._listing_id(canon, product)
            self._cache[canon] = product
            self._cache[lid] = product
            return product
        hits = self.search(key, pagination={"limit": 5})
        for hit in hits:
            doc = self._cache.get(str(hit.url))
            if doc:
                return doc
        raise KeyError(f"Listing not found: {identifier_or_url}")

    def parse_listing(self, document: Any) -> ParsedListing:
        d = document if isinstance(document, dict) else {}
        offers = normalize_offer(d)
        url = str(d.get("url") or offers.get("url") or "")
        if url.startswith("//"):
            url = "https:" + url
        listing_id = self._listing_id(url, d)
        title = str(d.get("name") or f"{self.source_id} {listing_id}")
        description = d.get("description")
        if isinstance(description, str):
            description = description.strip()
        else:
            description = None
        price_amount, price_currency = offer_price(d)
        if price_currency:
            price_currency = price_currency.upper()
        elif price_amount is not None:
            price_currency = self.cfg["default_currency"]
        seller_node = offers.get("seller") if isinstance(offers, dict) else None
        seller_name = None
        if isinstance(seller_node, dict):
            seller_name = seller_node.get("name")
        images = [("https:" + i) if i.startswith("//") else i for i in product_images(d)]
        cond, _ = normalize_condition(None)
        sku = d.get("sku")
        return ParsedListing(
            source_listing_id=listing_id,
            title=title,
            canonical_url=url,
            original_url=url,
            description=description,
            oem_as_stated=str(sku) if sku else None,
            manufacturer_as_stated=product_brand(d),
            condition=cond.value,
            price_amount=price_amount,
            price_currency=price_currency,
            country=self.cfg["country"],
            image_urls=images,
            seller={
                "display_name": seller_name,
                "business_name": seller_name if self.cfg["seller_type"] == "BUSINESS" else None,
                "country": self.cfg["country"],
                "seller_type": self.cfg["seller_type"],
                "public_phone": None,
                "marketplace_profile": seller_node.get("url") if isinstance(seller_node, dict) else None,
            },
            availability_status=offer_availability(d),
            extraction_confidence=float(self.cfg["confidence"]),
            is_demo_data=False,
            raw={"source": self.source_id, "product": d},
        )

    def parse_seller(self, document: Any) -> dict[str, Any]:
        return self.parse_listing(document).seller

    def check_availability(self, listing: ParsedListing | ListingView) -> str:
        if isinstance(listing, ParsedListing):
            return listing.availability_status
        return listing.status.value if listing.status else "UNKNOWN"

    def get_price(self, listing: ParsedListing | ListingView) -> dict[str, Any]:
        if isinstance(listing, ParsedListing):
            return {"amount": listing.price_amount, "currency": listing.price_currency}
        return {}

    def _listing_id(self, url: str, product: dict[str, Any]) -> str:
        m = self._id_re.search(url or "")
        if m:
            return m.group(1)
        sku = product.get("sku")
        if sku:
            return str(sku)
        return url.rstrip("/").split("/")[-1].replace(".html", "") or "unknown"


def build_jsonld_catalog_connectors() -> dict[str, JsonLdCatalogConnector]:
    return {key: JsonLdCatalogConnector(key) for key in JSONLD_MARKETS}
