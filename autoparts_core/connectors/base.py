"""Provider-neutral connector interface (Spec §5)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from autoparts_core.core.models import ConnectorCapabilities, ListingView, SearchHit


@dataclass
class RateLimitStatus:
    remaining: int | None = None
    reset_at: datetime | None = None
    limited: bool = False
    notes: str = ""


@dataclass
class ParsedListing:
    source_listing_id: str
    title: str
    canonical_url: str
    original_url: str
    description: str | None = None
    oem_as_stated: str | None = None
    manufacturer_as_stated: str | None = None
    condition_raw: str | None = None
    condition: str = "UNKNOWN"
    assembly_completeness: str = "UNKNOWN"
    side_position: str | None = None
    quantity: int | None = None
    visible_defects: str | None = None
    seller_compat_claim: str | None = None
    price_amount: float | None = None
    price_currency: str | None = None
    shipping_amount: float | None = None
    shipping_currency: str | None = None
    delivery_eligibility: str = "UNKNOWN"
    delivery_eta: str | None = None
    country: str | None = None
    image_urls: list[str] = field(default_factory=list)
    seller: dict[str, Any] = field(default_factory=dict)
    availability_status: str = "PARSED"
    extraction_confidence: float = 0.0
    is_demo_data: bool = False
    raw: dict[str, Any] = field(default_factory=dict)


class SourceConnector(ABC):
    """Every connector must implement this contract."""

    source_id: str
    source_name: str

    @abstractmethod
    def get_capabilities(self) -> ConnectorCapabilities: ...

    @abstractmethod
    def health_check(self) -> dict[str, Any]: ...

    @abstractmethod
    def get_rate_limit_status(self) -> RateLimitStatus: ...

    @abstractmethod
    def search(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        pagination: dict[str, Any] | None = None,
    ) -> list[SearchHit]: ...

    @abstractmethod
    def fetch_listing(self, identifier_or_url: str) -> Any: ...

    @abstractmethod
    def parse_listing(self, document: Any) -> ParsedListing: ...

    @abstractmethod
    def parse_seller(self, document: Any) -> dict[str, Any]: ...

    @abstractmethod
    def check_availability(self, listing: ParsedListing | ListingView) -> str: ...

    @abstractmethod
    def get_price(self, listing: ParsedListing | ListingView) -> dict[str, Any]: ...
