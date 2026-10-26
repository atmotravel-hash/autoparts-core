"""Prom.ua public catalog via search HTML Product JSON-LD (tested).

No API key. Uses the same public search pages as the website UI.
Does not bypass CAPTCHA/Cloudflare.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus

from autoparts_core.connectors.base import ParsedListing, RateLimitStatus, SourceConnector
from autoparts_core.connectors.jsonld_client import (
    JsonLdError,
    JsonLdHtmlClient,
    normalize_offer,
    offer_availability,
    offer_price,
    product_brand,
    product_images,
)
from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit
from autoparts_core.identity.condition import normalize_condition

_ID_RE = re.compile(r"/m(\d+)-", re.IGNORECASE)


class PromUaConnector(SourceConnector):
    source_id = "prom_ua"
    source_name = "Prom.ua Ukraine (JSON-LD catalog)"

    def __init__(self) -> None:
        self._client = JsonLdHtmlClient(
            origin="https://prom.ua",
            min_interval_seconds=0.9,
        )
        self._last_ok: datetime | None = None
        self._cache: dict[str, dict[str, Any]] = {}

    def get_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            source_id=self.source_id,
            source_name=self.source_name,
            supported_countries=["UA"],
            supported_languages=["uk", "ru", "en"],
            supported_search_modes=["vehicle_part", "oem", "part_name"],
            authentication_required=False,
            rate_limit_notes="Client throttle ~0.9s; public HTML search only",
            access_method="PUBLIC_PAGE",
            terms_notes="Reads schema.org Product JSON-LD embedded in public Prom.ua search/detail HTML. "
            "No CAPTCHA bypass. Merchant contact phones not scraped beyond public product fields.",
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

    def _search_url(self, query: str, *, page: int = 1) -> str:
        # Public UA search UI
        base = f"https://prom.ua/ua/search?search_term={quote_plus(query)}"
        if page > 1:
            return f"{base}&page={page}"
        return base

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        filters = filters or {}
        pagination = pagination or {}
        countries = filters.get("country")
        if countries and "UA" not in countries:
            return []

        limit = min(int(pagination.get("limit", 20)), 40)
        offset = int(pagination.get("offset", 0))
        page = max(1, offset // 10 + 1)

        products = self._client.fetch_products(self._search_url(query, page=page))
        self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)

        hits: list[SearchHit] = []
        for i, product in enumerate(products[:limit]):
            offers = normalize_offer(product)
            url = str(product.get("url") or offers.get("url") or "")
            if not url:
                continue
            listing_id = self._listing_id(url, product)
            self._cache[url] = product
            self._cache[listing_id] = product
            price, currency = offer_price(product)
            snippet_bits = ["Prom.ua UA"]
            if price is not None:
                snippet_bits.append(f"{price:g} {currency or 'UAH'}")
            brand = product_brand(product)
            if brand:
                snippet_bits.append(brand)
            hits.append(
                SearchHit(
                    url=url,
                    title=product.get("name"),
                    rank=offset + i + 1,
                    snippet=" · ".join(snippet_bits),
                    country="UA",
                    language="uk",
                )
            )
        return hits

    def fetch_listing(self, identifier_or_url: str) -> dict[str, Any]:
        key = identifier_or_url.strip()
        if key in self._cache:
            return self._cache[key]
        m = _ID_RE.search(key)
        if m and m.group(1) in self._cache:
            return self._cache[m.group(1)]

        if key.startswith("http"):
            products = self._client.fetch_products(key)
            if products:
                product = products[0]
                url = str(product.get("url") or key)
                lid = self._listing_id(url, product)
                self._cache[url] = product
                self._cache[lid] = product
                return product
            raise KeyError(f"No Product JSON-LD on Prom page: {key}")

        # Treat as search / id probe
        hits = self.search(key, pagination={"limit": 5})
        for hit in hits:
            doc = self._cache.get(str(hit.url))
            if doc:
                return doc
        raise KeyError(f"Prom listing not found: {identifier_or_url}")

    def parse_listing(self, document: Any) -> ParsedListing:
        d = document if isinstance(document, dict) else {}
        offers = normalize_offer(d)
        url = str(d.get("url") or offers.get("url") or "")
        listing_id = self._listing_id(url, d)
        title = str(d.get("name") or f"Prom {listing_id}")
        description = d.get("description")
        if isinstance(description, str):
            description = description.strip()
        else:
            description = None

        price_amount, price_currency = offer_price(d)
        if price_currency is None and price_amount is not None:
            price_currency = "UAH"

        sku = d.get("sku")
        oem = str(sku) if sku else None
        manufacturer = product_brand(d)
        cond, _ = normalize_condition(None)

        return ParsedListing(
            source_listing_id=listing_id,
            title=title,
            canonical_url=url,
            original_url=url,
            description=description,
            oem_as_stated=oem,
            manufacturer_as_stated=manufacturer,
            condition_raw=None,
            condition=cond.value,
            price_amount=price_amount,
            price_currency=price_currency,
            delivery_eligibility="UNKNOWN",
            country="UA",
            image_urls=product_images(d),
            seller={
                "display_name": None,
                "business_name": None,
                "country": "UA",
                "city": None,
                "seller_type": "BUSINESS",
                "public_phone": None,
                "marketplace_profile": None,
            },
            availability_status=offer_availability(d),
            extraction_confidence=0.86,
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

    @staticmethod
    def _listing_id(url: str, product: dict[str, Any]) -> str:
        m = _ID_RE.search(url or "")
        if m:
            return m.group(1)
        sku = product.get("sku")
        if sku:
            return str(sku)
        return url.rstrip("/").split("/")[-1] or "unknown"
