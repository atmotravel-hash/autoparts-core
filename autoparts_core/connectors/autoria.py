"""AUTO.RIA official developer API connector.

Requires free API key from https://developers.ria.com (profile → API key).
Terms: project must include a crawlable hyperlink to https://auto.ria.com.

Rate limit (free): ~30 requests/hour — client throttles accordingly.
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import httpx

from autoparts_core.config.settings import get_settings
from autoparts_core.connectors.base import ParsedListing, RateLimitStatus, SourceConnector
from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit
from autoparts_core.security.ssrf import validate_public_url

BASE = "https://developers.ria.com"
PUBLIC_ORIGIN = "https://auto.ria.com"


class AutoRiaConnector(SourceConnector):
    source_id = "auto_ria"
    source_name = "AUTO.RIA (official API)"

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = (settings.autoria_api_key or "").strip() or None
        self._last_ok: datetime | None = None
        self._marks_cache: dict[str, int] | None = None
        self._models_cache: dict[tuple[int, str], int] = {}
        self._detail_cache: dict[str, dict[str, Any]] = {}
        self._last_call = 0.0
        # Free tier ~30/hour → ≥120s would be extreme; use gentle 2.5s between calls
        self._min_interval = float(settings.autoria_min_interval_seconds)

    def _throttle(self) -> None:
        now = time.monotonic()
        wait = self._min_interval - (now - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        if not self.api_key:
            raise RuntimeError("AUTORIA_API_KEY is not configured")
        url = f"{BASE}{path}"
        ok, reason = validate_public_url(url)
        if not ok:
            raise ValueError(reason)
        query = {"api_key": self.api_key}
        if params:
            query.update({k: v for k, v in params.items() if v is not None})
        self._throttle()
        headers = {
            "User-Agent": "AutoPartsCore/0.2.1 (+AUTO.RIA official API client; attribution: auto.ria.com)",
            "Accept": "application/json",
        }
        with httpx.Client(timeout=25.0, follow_redirects=True, headers=headers) as client:
            response = client.get(url, params=query)
        try:
            payload = response.json()
        except Exception as exc:
            raise RuntimeError(f"AUTO.RIA non-JSON response HTTP {response.status_code}") from exc
        if isinstance(payload, dict) and payload.get("error"):
            err = payload["error"]
            code = err.get("code") if isinstance(err, dict) else "ERROR"
            msg = err.get("message") if isinstance(err, dict) else str(err)
            raise RuntimeError(f"AUTO.RIA {code}: {msg}")
        if response.status_code >= 400:
            raise RuntimeError(f"AUTO.RIA HTTP {response.status_code}: {payload}")
        return payload

    def get_capabilities(self) -> ConnectorCapabilities:
        has_key = bool(self.api_key)
        return ConnectorCapabilities(
            source_id=self.source_id,
            source_name=self.source_name,
            supported_countries=["UA"],
            supported_languages=["uk", "ru", "en"],
            supported_search_modes=["vehicle_part", "oem", "part_name"],
            authentication_required=True,
            rate_limit_notes="Free tier ~30 req/hour — throttled client-side",
            access_method="OFFICIAL_API",
            terms_notes="Official developers.ria.com API. Requires free API key + crawlable link to auto.ria.com. "
            "Useful for donor cars / autos sold for parts (spareParts) and vehicle context — "
            "not a full OEM parts catalogue.",
            pagination=True,
            price_capability=True,
            availability_capability=True,
            last_successful_test=self._last_ok,
            health_status="healthy" if (has_key and self._last_ok) else ("credentials_missing" if not has_key else "untested"),
            operational=has_key,
        )

    def health_check(self) -> dict[str, Any]:
        if not self.api_key:
            return {
                "ok": False,
                "status": "credentials_missing",
                "message": "Set AUTORIA_API_KEY from https://developers.ria.com (Мій профіль).",
                "register_url": "https://developers.ria.com/",
            }
        try:
            cats = self._get("/auto/categories")
            self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
            return {
                "ok": True,
                "status": "healthy",
                "categories_sample": cats[:3] if isinstance(cats, list) else cats,
                "attribution": PUBLIC_ORIGIN,
                "is_demo": False,
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "status": "down", "message": str(exc)}

    def get_rate_limit_status(self) -> RateLimitStatus:
        return RateLimitStatus(
            remaining=None,
            limited=not bool(self.api_key),
            notes="free tier ~30/hour" if self.api_key else "no api key",
        )

    def _load_marks(self) -> dict[str, int]:
        if self._marks_cache is not None:
            return self._marks_cache
        data = self._get("/auto/categories/1/marks")
        mapping: dict[str, int] = {}
        if isinstance(data, list):
            for row in data:
                name = str(row.get("name") or "").strip().lower()
                mid = row.get("value") or row.get("marka_id") or row.get("id")
                if name and mid is not None:
                    mapping[name] = int(mid)
        self._marks_cache = mapping
        return mapping

    def _resolve_mark_id(self, make: str | None) -> int | None:
        if not make:
            return None
        marks = self._load_marks()
        key = make.strip().lower()
        if key in marks:
            return marks[key]
        # fuzzy contains
        for name, mid in marks.items():
            if key in name or name in key:
                return mid
        aliases = {"vw": "volkswagen", "mercedes": "mercedes-benz", "mb": "mercedes-benz"}
        alias = aliases.get(key)
        if alias and alias in marks:
            return marks[alias]
        return None

    def _resolve_model_id(self, mark_id: int, model: str | None) -> int | None:
        if not model:
            return None
        cache_key = (mark_id, model.strip().lower())
        if cache_key in self._models_cache:
            return self._models_cache[cache_key]
        data = self._get(f"/auto/categories/1/marks/{mark_id}/models")
        if isinstance(data, list):
            target = model.strip().lower()
            for row in data:
                name = str(row.get("name") or "").strip().lower()
                mid = row.get("value") or row.get("model_id") or row.get("id")
                if mid is None:
                    continue
                if name == target or target in name or name in target:
                    self._models_cache[cache_key] = int(mid)
                    return int(mid)
        return None

    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> list[SearchHit]:
        if not self.api_key:
            raise RuntimeError("AUTO.RIA connector needs AUTORIA_API_KEY")
        filters = filters or {}
        pagination = pagination or {}
        limit = min(int(pagination.get("limit", 20)), 50)
        page = int(pagination.get("offset", 0)) // max(limit, 1)

        # Prefer structured vehicle filters from search orchestration
        make = filters.get("make")
        model = filters.get("model")
        year = filters.get("year")
        # Parse crude make/model from free-text query if needed
        if not make and query:
            tokens = query.split()
            if tokens:
                make = tokens[0]
            if len(tokens) > 1 and not model:
                model = tokens[1]

        mark_id = self._resolve_mark_id(str(make) if make else None)
        model_id = self._resolve_model_id(mark_id, str(model) if (model and mark_id) else None) if mark_id else None

        params: dict[str, Any] = {
            "category_id": 1,
            "countpage": limit,
            "page": page,
            "status_id": 0,
            "with_photo": 1,
        }
        if mark_id is not None:
            params["marka_id[0]"] = mark_id
            params["model_id[0]"] = model_id if model_id is not None else 0
        if year:
            y = int(year)
            params["s_yers[0]"] = y - 1
            params["po_yers[0]"] = y + 1
        # Donor / for-parts vehicles when looking for parts
        if filters.get("spare_parts_donors", True):
            params["spareParts"] = 1

        countries = filters.get("country")
        if countries and "UA" not in countries:
            return []

        payload = self._get("/auto/search", params)
        self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
        # Response shape can be list-wrapped or dict
        block = payload
        if isinstance(payload, list) and payload:
            block = payload[0]
        result = (block.get("result") if isinstance(block, dict) else None) or {}
        search_result = result.get("search_result") or {}
        ids = [str(i) for i in (search_result.get("ids") or [])][:limit]

        hits: list[SearchHit] = []
        for i, auto_id in enumerate(ids):
            url = f"{PUBLIC_ORIGIN}/uk/auto_{auto_id}.html"
            # prefetch light detail into cache for fetch_listing
            try:
                detail = self._get("/auto/info", {"auto_id": auto_id})
                if isinstance(detail, list) and detail:
                    detail = detail[0]
                if isinstance(detail, dict):
                    self._detail_cache[auto_id] = detail
                    self._detail_cache[url] = detail
                    title = detail.get("title") or f"{detail.get('markName', '')} {detail.get('modelName', '')}".strip()
                else:
                    title = f"AUTO.RIA #{auto_id}"
            except Exception:
                title = f"AUTO.RIA #{auto_id}"
            hits.append(
                SearchHit(
                    url=url,
                    title=title or f"AUTO.RIA #{auto_id}",
                    rank=page * limit + i + 1,
                    snippet="AUTO.RIA · UA · official API",
                    country="UA",
                    language="uk",
                )
            )
        return hits

    def fetch_listing(self, identifier_or_url: str) -> dict[str, Any]:
        key = identifier_or_url.strip()
        if key in self._detail_cache:
            return self._detail_cache[key]
        m = re.search(r"(\d{5,})", key)
        auto_id = m.group(1) if m else key
        if auto_id in self._detail_cache:
            return self._detail_cache[auto_id]
        detail = self._get("/auto/info", {"auto_id": auto_id})
        if isinstance(detail, list) and detail:
            detail = detail[0]
        if not isinstance(detail, dict):
            raise KeyError(f"AUTO.RIA listing not found: {auto_id}")
        self._detail_cache[auto_id] = detail
        self._detail_cache[f"{PUBLIC_ORIGIN}/uk/auto_{auto_id}.html"] = detail
        self._last_ok = datetime.now(timezone.utc).replace(tzinfo=None)
        return detail

    def parse_listing(self, document: Any) -> ParsedListing:
        d = document if isinstance(document, dict) else {}
        auto_data = d.get("autoData") or {}
        auto_id = str(auto_data.get("autoId") or d.get("autoId") or "")
        mark = d.get("markName") or ""
        model = d.get("modelName") or ""
        year = auto_data.get("year")
        title = d.get("title") or f"{mark} {model} {year or ''}".strip()
        description = auto_data.get("description")
        url = d.get("linkToView") or f"{PUBLIC_ORIGIN}/uk/auto_{auto_id}.html"
        if url.startswith("/"):
            url = PUBLIC_ORIGIN + url

        # Prefer EUR then UAH then USD
        price_amount = None
        price_currency = None
        for cur in ("EUR", "UAH", "USD"):
            if d.get(cur) is not None:
                price_amount = float(d[cur])
                price_currency = cur
                break

        photos = []
        photo_data = d.get("photoData") or {}
        for key in ("seoLinkF", "seoLinkB", "seoLinkM", "seoLinkSX"):
            if photo_data.get(key):
                photos.append(photo_data[key])
                break

        phone = None
        phone_data = d.get("userPhoneData") or {}
        raw_phone = phone_data.get("phone")
        if raw_phone and "x" not in str(raw_phone).lower():
            phone = str(raw_phone)

        spare = bool((d.get("autoInfoBar") or {}).get("onRepairParts")) or bool(d.get("spareParts"))
        condition = "FOR_PARTS" if spare else "USED"

        return ParsedListing(
            source_listing_id=auto_id,
            title=title,
            canonical_url=url,
            original_url=url,
            description=description,
            condition_raw="Авто на запчастини" if spare else "Вживане авто",
            condition=condition,
            price_amount=price_amount,
            price_currency=price_currency,
            delivery_eligibility="UNKNOWN",
            country="UA",
            image_urls=photos,
            seller={
                "display_name": f"AUTO.RIA user {d.get('userId')}",
                "country": "UA",
                "city": d.get("locationCityName"),
                "seller_type": "UNKNOWN",
                "public_phone": phone,
                "marketplace_profile": None,
            },
            seller_compat_claim=f"{mark} {model} {year}".strip() if mark else None,
            availability_status="ACTIVE_UNVERIFIED" if not auto_data.get("isSold") else "SOLD_OR_UNAVAILABLE",
            extraction_confidence=0.9,
            is_demo_data=False,
            raw={"source": "auto_ria", "listing": d},
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
