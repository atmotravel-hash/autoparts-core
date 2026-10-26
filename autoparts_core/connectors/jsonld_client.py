"""HTTP client for public catalog HTML that embeds schema.org Product JSON-LD.

Used when a marketplace exposes product cards in search HTML (no API key).
Does not bypass CAPTCHA, Cloudflare challenges, or auth walls.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from autoparts_core.security.ssrf import validate_public_url

_LD_SCRIPT_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class JsonLdError(Exception):
    message: str
    status_code: int | None = None
    payload: Any = None

    def __str__(self) -> str:  # pragma: no cover
        return self.message


@dataclass
class RateLimiter:
    min_interval_seconds: float = 0.8
    _last: float = field(default=0.0, init=False)

    def wait(self) -> None:
        now = time.monotonic()
        delta = now - self._last
        if delta < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - delta)
        self._last = time.monotonic()


def extract_jsonld_products(html: str) -> list[dict[str, Any]]:
    """Parse Product nodes from application/ld+json blocks."""
    products: list[dict[str, Any]] = []
    for block in _LD_SCRIPT_RE.findall(html or ""):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        _collect_products(data, products)
    return products


def _is_product_type(value: Any) -> bool:
    if value == "Product":
        return True
    if isinstance(value, list) and "Product" in value:
        return True
    return False


def _collect_products(node: Any, out: list[dict[str, Any]]) -> None:
    if isinstance(node, list):
        for item in node:
            _collect_products(item, out)
        return
    if not isinstance(node, dict):
        return
    if _is_product_type(node.get("@type")):
        out.append(node)
    for graph_item in node.get("@graph") or []:
        _collect_products(graph_item, out)
    if node.get("@type") == "ItemList":
        for el in node.get("itemListElement") or []:
            if isinstance(el, dict):
                _collect_products(el.get("item") or el, out)


def normalize_offer(product: dict[str, Any]) -> dict[str, Any]:
    """Flatten Product.offers into a single offer dict."""
    offers = product.get("offers")
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    if not isinstance(offers, dict):
        offers = {}
    return offers


def offer_availability(product: dict[str, Any]) -> str:
    offers = normalize_offer(product)
    raw = str(offers.get("availability") or "")
    low = raw.lower()
    if "outofstock" in low or "soldout" in low:
        return "SOLD"
    if "instock" in low or "limitedavailability" in low or "onlineonly" in low:
        return "ACTIVE_UNVERIFIED"
    return "ACTIVE_UNVERIFIED"


def offer_price(product: dict[str, Any]) -> tuple[float | None, str | None]:
    offers = normalize_offer(product)
    amount = offers.get("price")
    currency = offers.get("priceCurrency")
    if amount is None:
        return None, (str(currency).upper() if currency else None)
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return None, (str(currency).upper() if currency else None)
    return value, (str(currency).upper() if currency else None)


def product_images(product: dict[str, Any], *, limit: int = 5) -> list[str]:
    image = product.get("image")
    urls: list[str] = []
    if isinstance(image, str):
        urls.append(image)
    elif isinstance(image, list):
        for item in image:
            if isinstance(item, str):
                urls.append(item)
            elif isinstance(item, dict) and item.get("url"):
                urls.append(str(item["url"]))
    return urls[:limit]


def product_brand(product: dict[str, Any]) -> str | None:
    brand = product.get("brand")
    if isinstance(brand, str):
        return brand
    if isinstance(brand, dict):
        name = brand.get("name")
        return str(name) if name else None
    return None


class JsonLdHtmlClient:
    def __init__(
        self,
        *,
        origin: str,
        timeout: float = 25.0,
        min_interval_seconds: float = 0.8,
        user_agent: str | None = None,
    ) -> None:
        origin_url = origin.rstrip("/") + "/"
        ok, reason = validate_public_url(origin_url)
        if not ok:
            raise ValueError(f"Origin rejected: {reason}")
        self.origin = origin.rstrip("/")
        self.timeout = timeout
        self.limiter = RateLimiter(min_interval_seconds=min_interval_seconds)
        self.headers = {
            "User-Agent": user_agent
            or "AutoPartsCore/0.2 (+public JSON-LD catalog client; respectful rate limits)",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "uk-UA,uk;q=0.9,ru;q=0.8,en;q=0.7",
            "Referer": self.origin + "/",
        }

    def get_html(self, url: str) -> str:
        ok, reason = validate_public_url(url)
        if not ok:
            raise JsonLdError(f"URL rejected: {reason}")
        self.limiter.wait()
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True, headers=self.headers) as client:
                response = client.get(url)
        except httpx.HTTPError as exc:
            raise JsonLdError(f"Network error: {exc}") from exc

        text_head = response.text[:300].lower()
        ctype = (response.headers.get("content-type") or "").lower()
        if "just a moment" in text_head or (
            "text/html" in ctype and "captcha" in text_head and response.status_code in {403, 503}
        ):
            raise JsonLdError(
                "Access challenge/CAPTCHA encountered — refusing to bypass",
                status_code=response.status_code,
            )
        if response.status_code >= 400:
            raise JsonLdError(
                f"HTTP {response.status_code} from catalog page",
                status_code=response.status_code,
                payload=response.text[:400],
            )
        return response.text

    def fetch_products(self, url: str) -> list[dict[str, Any]]:
        return extract_jsonld_products(self.get_html(url))
