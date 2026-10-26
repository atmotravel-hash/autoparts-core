"""999.md public catalog via POST https://999.md/graphql (tested)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from autoparts_core.connectors.base import ParsedListing, RateLimitStatus, SourceConnector
from autoparts_core.connectors.graphql_client import GraphQLClient, GraphQLError
from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit
from autoparts_core.identity.condition import normalize_condition

# Auto parts / dismantling category subtree on 999.md
PARTS_CATEGORY_ID = 5001
PARTS_SUBCATEGORY_ID = 674  # Piese și dezmembrare auto

SEARCH_QUERY = """
query SearchAds($input: Ads_SearchInput!) {
  searchAds(input: $input) {
    count
    ads {
      id
      title
      posted
      state
      subCategory { id title { translated } url }
      owner { id login }
    }
  }
}
"""

ADVERT_QUERY = """
query Advert($input: AdvertInput!) {
  advert(input: $input) {
    id
    title
    posted
    state
    subCategory { id title { translated } url }
    owner { id login }
    groups(placement: VIEW_ONE_DEFAULT) {
      title
      controls {
        type
        title
        option_title
        feature { id type value }
      }
    }
  }
}
"""


class Nine99MdConnector(SourceConnector):
    source_id = "nine99_md"
    source_name = "999.md (Moldova GraphQL catalog)"

    def __init__(self) -> None:
        self._client = GraphQLClient(
            "https://999.md/graphql",
            origin="https://999.md",
            referer="https://999.md/",
            min_interval_seconds=0.7,
        )
        self._last_ok: datetime | None = None

    def get_capabilities(self) -> ConnectorCapabilities:
        return ConnectorCapabilities(
            source_id=self.source_id,
            source_name=self.source_name,
            supported_countries=["MD"],
            supported_languages=["ro", "ru", "en"],
            supported_search_modes=["vehicle_part", "oem", "part_name"],
            authentication_required=False,
            rate_limit_notes="Client-side delay ~0.7s; respect site load",
            access_method="PUBLIC_PAGE",
            terms_notes="Uses the same public GraphQL catalog endpoint as the website UI. "
            "No CAPTCHA bypass. Public listing fields only.",
            pagination=True,
            price_capability=True,
            availability_capability=True,
            last_successful_test=self._last_ok,
            health_status="healthy" if self._last_ok else "untested",
            operational=True,
        )

    def health_check(self) -> dict[str, Any]:
        try:
            payload = self._client.execute("{ __typename }")
            self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
            return {"ok": True, "status": "healthy", "typename": payload.get("data"), "is_demo": False}
        except GraphQLError as exc:
            return {"ok": False, "status": "down", "message": str(exc)}

    def get_rate_limit_status(self) -> RateLimitStatus:
        return RateLimitStatus(limited=False, notes="soft client throttle 0.7s")

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        filters = filters or {}
        pagination = pagination or {}
        limit = min(int(pagination.get("limit", 20)), 40)
        skip = int(pagination.get("offset", 0))
        input_obj: dict[str, Any] = {
            "query": query,
            "pagination": {"skip": skip, "limit": limit},
            "categoryId": PARTS_CATEGORY_ID,
        }
        # Prefer spare-parts subcategory unless caller overrides
        if filters.get("subcategory_id"):
            input_obj["subCategoryId"] = int(filters["subcategory_id"])
        else:
            input_obj["subCategoryId"] = PARTS_SUBCATEGORY_ID

        payload = self._client.execute(SEARCH_QUERY, {"input": input_obj})
        self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
        ads = (((payload.get("data") or {}).get("searchAds") or {}).get("ads")) or []
        hits: list[SearchHit] = []
        for i, ad in enumerate(ads):
            ad_id = str(ad["id"])
            url = f"https://999.md/ro/transport/spare-parts-for-cars/{ad_id}"
            sub = ad.get("subCategory") or {}
            hits.append(
                SearchHit(
                    url=url,
                    title=ad.get("title"),
                    rank=i + 1 + skip,
                    snippet=f"999.md · {(sub.get('title') or {}).get('translated') or 'parts'} · MD",
                    country="MD",
                    language="ro",
                )
            )
        return hits

    def fetch_listing(self, identifier_or_url: str) -> dict[str, Any]:
        ad_id = identifier_or_url.rstrip("/").split("/")[-1]
        if ad_id.startswith("http"):
            ad_id = ad_id.rstrip("/").split("/")[-1]
        payload = self._client.execute(ADVERT_QUERY, {"input": {"id": str(ad_id)}})
        self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
        advert = (payload.get("data") or {}).get("advert")
        if not advert:
            raise KeyError(f"999.md advert not found: {ad_id}")
        return advert

    def parse_listing(self, document: Any) -> ParsedListing:
        d = document if isinstance(document, dict) else {}
        ad_id = str(d.get("id"))
        title = d.get("title") or f"999.md #{ad_id}"
        sub = d.get("subCategory") or {}
        sub_url = sub.get("url") or "transport/spare-parts-for-cars"
        url = f"https://999.md/ro/{sub_url}/{ad_id}"
        owner = d.get("owner") or {}

        price_amount = None
        price_currency = None
        description = None
        condition_raw = None
        region = None
        for group in d.get("groups") or []:
            for control in group.get("controls") or []:
                feat = control.get("feature") or {}
                ftype = feat.get("type")
                value = feat.get("value") or {}
                if ftype == "FEATURE_PRICE" and isinstance(value, dict):
                    price_amount = value.get("value")
                    unit = (value.get("unit") or value.get("measurement") or "").upper()
                    price_currency = unit.replace("UNIT_", "") if unit.startswith("UNIT_") else unit or "EUR"
                elif ftype == "FEATURE_BODY":
                    description = value.get("translated") if isinstance(value, dict) else str(value)
                elif ftype == "FEATURE_OPTIONS" and control.get("title") in {"Regiune", "Регион", "Region"}:
                    region = value.get("translated") if isinstance(value, dict) else None
                elif control.get("title") in {"Stare", "Состояние", "Condition", "Starea"}:
                    condition_raw = value.get("translated") if isinstance(value, dict) else None

        cond, _ = normalize_condition(condition_raw)
        return ParsedListing(
            source_listing_id=ad_id,
            title=title,
            canonical_url=url,
            original_url=url,
            description=description,
            condition_raw=condition_raw,
            condition=cond.value,
            price_amount=float(price_amount) if price_amount is not None else None,
            price_currency=price_currency,
            delivery_eligibility="UNKNOWN",
            country="MD",
            seller={
                "display_name": owner.get("login"),
                "country": "MD",
                "seller_type": "UNKNOWN",
                "city": region,
                "marketplace_profile": f"https://999.md/ro/profile/{owner.get('id')}" if owner.get("id") else None,
            },
            availability_status="ACTIVE_UNVERIFIED"
            if d.get("state") == "AD_STATE_PUBLIC"
            else "ACTIVE_UNVERIFIED",
            extraction_confidence=0.85,
            is_demo_data=False,
            raw={"source": "nine99_md", "advert": d},
        )

    def parse_seller(self, document: Any) -> dict[str, Any]:
        return self.parse_listing(document).seller

    def check_availability(self, listing: ParsedListing | ListingView) -> str:
        if isinstance(listing, ParsedListing):
            return listing.availability_status
        return listing.status.value if listing.status else "UNKNOWN"

    def get_price(self, listing: ParsedListing | ListingView) -> dict[str, Any]:
        if isinstance(listing, ParsedListing):
            return {
                "amount": listing.price_amount,
                "currency": listing.price_currency,
            }
        return {}
