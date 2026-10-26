"""Offline fixture connector — clearly labelled demo data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from autoparts_core.connectors.base import ParsedListing, RateLimitStatus, SourceConnector
from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "tests" / "fixtures"


class FixtureConnector(SourceConnector):
    source_id = "fixture"
    source_name = "Offline Fixture Source"

    def __init__(self) -> None:
        self._listings = self._load()

    def _load(self) -> list[dict[str, Any]]:
        path = FIXTURES_DIR / "listings.json"
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def get_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            source_id=self.source_id,
            source_name=self.source_name,
            supported_countries=["DE", "PL", "LT", "UA", "MD"],
            supported_languages=["en", "de", "pl", "uk", "ro", "ru"],
            supported_search_modes=["vehicle_part", "oem", "part_name"],
            authentication_required=False,
            rate_limit_notes="Local fixtures only",
            access_method="FIXTURE",
            terms_notes="DEMO DATA — never present as live current listings",
            pagination=True,
            price_capability=True,
            availability_capability=True,
            last_successful_test=datetime.now(timezone.utc).replace(tzinfo=None),
            health_status="healthy",
            operational=True,
        )

    def health_check(self) -> dict[str, Any]:
        return {
            "ok": True,
            "status": "healthy",
            "message": f"Fixture connector loaded {len(self._listings)} demo listings",
            "is_demo": True,
        }

    def get_rate_limit_status(self) -> RateLimitStatus:
        return RateLimitStatus(remaining=None, limited=False, notes="local")

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        q = query.lower().strip()
        filters = filters or {}
        hits: list[SearchHit] = []
        for i, row in enumerate(self._listings):
            blob = " ".join(
                str(row.get(k) or "")
                for k in ("title", "oem_as_stated", "manufacturer_as_stated", "make", "model", "part_name")
            ).lower()
            if q and q not in blob and not all(tok in blob for tok in q.split() if len(tok) > 2):
                # soft match: any significant token
                tokens = [t for t in q.replace(",", " ").split() if len(t) > 2]
                if tokens and not any(t in blob for t in tokens):
                    continue
            if filters.get("oem"):
                oem = (row.get("oem_as_stated") or "").upper().replace(" ", "")
                if filters["oem"].upper().replace(" ", "") not in oem:
                    continue
            if filters.get("country") and row.get("country") not in filters["country"]:
                continue
            if filters.get("condition") and filters["condition"] != "Any":
                if row.get("condition") != filters["condition"]:
                    continue
            hits.append(
                SearchHit(
                    url=row["canonical_url"],
                    title=row["title"],
                    rank=i + 1,
                    snippet=f"DEMO · {row.get('oem_as_stated') or 'no OEM'} · {row.get('country')}",
                    country=row.get("country"),
                    language=row.get("language", "en"),
                )
            )
        limit = (pagination or {}).get("limit", 50)
        return hits[:limit]

    def fetch_listing(self, identifier_or_url: str) -> dict[str, Any]:
        for row in self._listings:
            if row["canonical_url"] == identifier_or_url or row["source_listing_id"] == identifier_or_url:
                return row
        raise KeyError(f"Fixture listing not found: {identifier_or_url}")

    def parse_listing(self, document: Any) -> ParsedListing:
        d = document if isinstance(document, dict) else {}
        return ParsedListing(
            source_listing_id=d["source_listing_id"],
            title=d["title"],
            canonical_url=d["canonical_url"],
            original_url=d.get("original_url", d["canonical_url"]),
            description=d.get("description"),
            oem_as_stated=d.get("oem_as_stated"),
            manufacturer_as_stated=d.get("manufacturer_as_stated"),
            condition_raw=d.get("condition_raw"),
            condition=d.get("condition", "UNKNOWN"),
            assembly_completeness=d.get("assembly_completeness", "UNKNOWN"),
            side_position=d.get("side_position"),
            quantity=d.get("quantity", 1),
            visible_defects=d.get("visible_defects"),
            seller_compat_claim=d.get("seller_compat_claim"),
            price_amount=d.get("price_amount"),
            price_currency=d.get("price_currency"),
            shipping_amount=d.get("shipping_amount"),
            shipping_currency=d.get("shipping_currency"),
            delivery_eligibility=d.get("delivery_eligibility", "UNKNOWN"),
            delivery_eta=d.get("delivery_eta"),
            country=d.get("country"),
            image_urls=d.get("image_urls") or [],
            seller=d.get("seller") or {},
            availability_status=d.get("availability_status", "ACTIVE_UNVERIFIED"),
            extraction_confidence=float(d.get("extraction_confidence", 0.9)),
            is_demo_data=True,
            raw=d,
        )

    def parse_seller(self, document: Any) -> dict[str, Any]:
        d = document if isinstance(document, dict) else {}
        return d.get("seller") or {}

    def check_availability(self, listing: ParsedListing | ListingView) -> str:
        if isinstance(listing, ParsedListing):
            return listing.availability_status
        return listing.status.value if listing.status else "UNKNOWN"

    def get_price(self, listing: ParsedListing | ListingView) -> dict[str, Any]:
        if isinstance(listing, ParsedListing):
            return {
                "amount": listing.price_amount,
                "currency": listing.price_currency,
                "shipping_amount": listing.shipping_amount,
                "shipping_currency": listing.shipping_currency,
            }
        return {}
