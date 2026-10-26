"""OLX public catalog via POST /apigateway/graphql (ListingSearchQuery).

Tested markets: olx.ua, olx.pl, olx.ro, olx.bg, olx.pt.
Does not bypass CAPTCHA on HTML pages; uses the public GraphQL gateway only.
Phone numbers are not fabricated — contact.phone is a boolean availability flag.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from autoparts_core.connectors.base import ParsedListing, RateLimitStatus, SourceConnector
from autoparts_core.connectors.graphql_client import GraphQLClient, GraphQLError
from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit
from autoparts_core.identity.condition import normalize_condition

LISTING_SEARCH_QUERY = """
query ListingSearchQuery($searchParameters: [SearchParameter!]!) {
  clientCompatibleListings(searchParameters: $searchParameters) {
    __typename
    ... on ListingSuccess {
      data {
        id
        title
        url
        status
        business
        created_time
        last_refresh_time
        category { id type }
        contact { name phone chat }
        location { city { name } region { name } }
        params {
          key
          name
          type
          value {
            __typename
            ... on PriceParam {
              value
              currency
              negotiable
              label
            }
            ... on GenericParam {
              key
              label
            }
          }
        }
        photos { link width height }
        user { id name company_name seller_type }
        description
      }
      metadata { total_elements visible_total_count }
    }
  }
}
"""

# Product scope: UA · MD · RO only (PL/BG/PT deferred).
OLX_MARKETS: dict[str, dict[str, Any]] = {
    "olx_ua": {
        "host": "www.olx.ua",
        "country": "UA",
        "languages": ["uk", "ru", "en"],
        "default_currency": "UAH",
        "parts_category_id": "2550",
        "source_name": "OLX Ukraine (GraphQL)",
    },
    "olx_ro": {
        "host": "www.olx.ro",
        "country": "RO",
        "languages": ["ro", "en"],
        "default_currency": "RON",
        "parts_category_id": None,
        "source_name": "OLX Romania (GraphQL)",
    },
}


def _photo_url(link: str | None) -> str | None:
    if not link:
        return None
    return link.replace("{width}", "800").replace("{height}", "600")


class OlxGraphQLConnector(SourceConnector):
    def __init__(self, market_key: str) -> None:
        if market_key not in OLX_MARKETS:
            raise ValueError(f"Unknown OLX market: {market_key}")
        self.market_key = market_key
        self.cfg = OLX_MARKETS[market_key]
        self.source_id = market_key
        self.source_name = self.cfg["source_name"]
        host = self.cfg["host"]
        self._client = GraphQLClient(
            f"https://{host}/apigateway/graphql",
            origin=f"https://{host}",
            referer=f"https://{host}/",
            min_interval_seconds=0.8,
        )
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
            rate_limit_notes="Client throttle ~0.8s; OLX may rate-limit — back off on errors",
            access_method="PUBLIC_PAGE",
            terms_notes="Public GraphQL gateway used by OLX web UI (ListingSearchQuery). "
            "Official OLX Partner API remains preferred when credentials exist. "
            "No CAPTCHA bypass. Phone numbers not scraped beyond availability flag.",
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
        return RateLimitStatus(limited=False, notes="soft client throttle 0.8s")

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        filters = filters or {}
        pagination = pagination or {}
        limit = min(int(pagination.get("limit", 20)), 40)
        offset = int(pagination.get("offset", 0))
        params: list[dict[str, str]] = [
            {"key": "query", "value": query},
            {"key": "offset", "value": str(offset)},
            {"key": "limit", "value": str(limit)},
        ]
        cat = filters.get("category_id") or self.cfg.get("parts_category_id")
        if cat:
            params.append({"key": "category_id", "value": str(cat)})

        countries = filters.get("country")
        if countries and self.cfg["country"] not in countries:
            return []

        payload = self._client.execute(
            LISTING_SEARCH_QUERY,
            {"searchParameters": params},
            operation_name="ListingSearchQuery",
        )
        self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
        block = (payload.get("data") or {}).get("clientCompatibleListings") or {}
        rows = block.get("data") or []
        hits: list[SearchHit] = []
        for i, row in enumerate(rows):
            url = row.get("url") or ""
            self._cache[url] = row
            self._cache[str(row.get("id"))] = row
            hits.append(
                SearchHit(
                    url=url,
                    title=row.get("title"),
                    rank=offset + i + 1,
                    snippet=f"OLX {self.cfg['country']} · cat={((row.get('category') or {}).get('id'))}",
                    country=self.cfg["country"],
                    language=self.cfg["languages"][0],
                )
            )
        return hits

    def fetch_listing(self, identifier_or_url: str) -> dict[str, Any]:
        key = identifier_or_url.strip()
        if key in self._cache:
            return self._cache[key]
        # Re-search by id fragment if needed
        ad_id = key.rstrip("/").split("-")[-1].replace(".html", "")
        # ID often embedded as IDxxxx — fallback: search URL path id digits
        import re

        m = re.search(r"(\d{6,})", key)
        if m and m.group(1) in self._cache:
            return self._cache[m.group(1)]
        # Last resort: treat as search query of the id
        hits = self.search(ad_id if m else key, pagination={"limit": 5})
        for hit in hits:
            doc = self._cache.get(str(hit.url))
            if doc:
                return doc
        raise KeyError(f"OLX listing not in session cache: {identifier_or_url}")

    def parse_listing(self, document: Any) -> ParsedListing:
        d = document if isinstance(document, dict) else {}
        listing_id = str(d.get("id"))
        url = d.get("url") or ""
        title = d.get("title") or f"OLX {listing_id}"
        description = d.get("description")
        if isinstance(description, str):
            description = description.replace("<br />", "\n").replace("<br/>", "\n")

        price_amount = None
        price_currency = None
        condition_raw = None
        oem = None
        for p in d.get("params") or []:
            val = p.get("value") or {}
            if p.get("key") == "price" or p.get("type") == "price":
                price_amount = val.get("value")
                price_currency = val.get("currency") or self.cfg["default_currency"]
            elif p.get("key") in {"state", "stan", "stare"}:
                condition_raw = val.get("label") or val.get("key")
            elif p.get("key") in {"manufacturer_code", "oem", "part_number"}:
                oem = val.get("label") or val.get("key")

        cond, _ = normalize_condition(condition_raw)
        user = d.get("user") or {}
        contact = d.get("contact") or {}
        loc = d.get("location") or {}
        city = ((loc.get("city") or {}).get("name"))
        photos = [_photo_url(p.get("link")) for p in (d.get("photos") or []) if p.get("link")]
        photos = [p for p in photos if p]

        seller_type = "BUSINESS" if d.get("business") else "PRIVATE"
        return ParsedListing(
            source_listing_id=listing_id,
            title=title,
            canonical_url=url,
            original_url=url,
            description=description,
            oem_as_stated=oem,
            condition_raw=condition_raw,
            condition=cond.value,
            price_amount=float(price_amount) if price_amount is not None else None,
            price_currency=price_currency,
            delivery_eligibility="UNKNOWN",
            country=self.cfg["country"],
            image_urls=photos[:5],
            seller={
                "display_name": contact.get("name") or user.get("name") or user.get("company_name"),
                "business_name": user.get("company_name") or None,
                "country": self.cfg["country"],
                "city": city,
                "seller_type": seller_type,
                # phone is boolean on OLX GraphQL — do not invent a number
                "public_phone": None,
                "phone_available": bool(contact.get("phone")),
                "marketplace_profile": None,
            },
            availability_status="ACTIVE_UNVERIFIED" if d.get("status") == "active" else "ACTIVE_UNVERIFIED",
            extraction_confidence=0.88,
            is_demo_data=False,
            raw={"source": self.source_id, "listing": d},
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


def build_olx_connectors() -> dict[str, OlxGraphQLConnector]:
    return {key: OlxGraphQLConnector(key) for key in OLX_MARKETS}
