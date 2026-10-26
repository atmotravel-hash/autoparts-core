"""Manual URL import connector with SSRF protections."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from autoparts_core.connectors.base import ParsedListing, RateLimitStatus, SourceConnector
from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit
from autoparts_core.security.ssrf import validate_public_url


class ManualImportConnector(SourceConnector):
    source_id = "manual"
    source_name = "Manual URL Import"

    def get_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            source_id=self.source_id,
            source_name=self.source_name,
            supported_countries=[],
            supported_languages=[],
            supported_search_modes=["url"],
            authentication_required=False,
            rate_limit_notes="User-driven",
            access_method="MANUAL_IMPORT",
            terms_notes="Stores user-supplied metadata; does not bypass paywalls or CAPTCHAs. "
            "Live HTTP fetch is disabled by default pending authorized access policy.",
            pagination=False,
            price_capability=False,
            availability_capability=False,
            last_successful_test=datetime.now(timezone.utc).replace(tzinfo=None),
            health_status="healthy",
            operational=True,
        )

    def health_check(self) -> dict[str, Any]:
        return {
            "ok": True,
            "status": "healthy",
            "message": "Manual import accepts validated public URLs as provenance records only "
            "(no automatic scrape of protected content).",
        }

    def get_rate_limit_status(self) -> RateLimitStatus:
        return RateLimitStatus(limited=False, notes="n/a")

    def search(self, query, filters=None, pagination=None) -> list[SearchHit]:
        return []

    def fetch_listing(self, identifier_or_url: str) -> dict[str, Any]:
        ok, reason = validate_public_url(identifier_or_url)
        if not ok:
            raise ValueError(f"URL rejected: {reason}")
        # Intentionally does not fetch remote HTML — avoids unauthorized scraping.
        parsed = urlparse(identifier_or_url)
        return {
            "url": identifier_or_url,
            "domain": parsed.netloc,
            "fetch_performed": False,
            "note": "Metadata-only import. Provide fields manually or use fixture/authorized connectors.",
        }

    def parse_listing(self, document: Any) -> ParsedListing:
        d = document if isinstance(document, dict) else {}
        url = d.get("canonical_url") or d.get("url") or ""
        ok, reason = validate_public_url(url)
        if not ok:
            raise ValueError(f"URL rejected: {reason}")
        source_listing_id = d.get("source_listing_id") or url
        return ParsedListing(
            source_listing_id=str(source_listing_id)[:120],
            title=d.get("title") or f"Manual import: {url}",
            canonical_url=url,
            original_url=d.get("original_url") or url,
            description=d.get("description"),
            oem_as_stated=d.get("oem_as_stated"),
            manufacturer_as_stated=d.get("manufacturer_as_stated"),
            condition_raw=d.get("condition_raw"),
            condition=d.get("condition", "UNKNOWN"),
            assembly_completeness=d.get("assembly_completeness", "UNKNOWN"),
            side_position=d.get("side_position"),
            price_amount=d.get("price_amount"),
            price_currency=d.get("price_currency"),
            shipping_amount=d.get("shipping_amount"),
            shipping_currency=d.get("shipping_currency"),
            delivery_eligibility=d.get("delivery_eligibility", "UNKNOWN"),
            country=d.get("country"),
            image_urls=d.get("image_urls") or [],
            seller=d.get("seller") or {},
            availability_status="ACTIVE_UNVERIFIED",
            extraction_confidence=float(d.get("extraction_confidence", 0.4)),
            is_demo_data=False,
            raw=d,
        )

    def parse_seller(self, document: Any) -> dict[str, Any]:
        d = document if isinstance(document, dict) else {}
        return d.get("seller") or {}

    def check_availability(self, listing: ParsedListing | ListingView) -> str:
        return "ACTIVE_UNVERIFIED"

    def get_price(self, listing: ParsedListing | ListingView) -> dict[str, Any]:
        if isinstance(listing, ParsedListing):
            return {
                "amount": listing.price_amount,
                "currency": listing.price_currency,
                "shipping_amount": listing.shipping_amount,
                "shipping_currency": listing.shipping_currency,
            }
        return {}
