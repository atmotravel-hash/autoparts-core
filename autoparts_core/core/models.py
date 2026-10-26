"""Pydantic domain models used across services (not ORM)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from autoparts_core.core.enums import (
    AssemblyCompleteness,
    Condition,
    DataProvenance,
    DeliveryEligibility,
    EvidenceKind,
    FitmentStatus,
    IdentifierRelation,
    ListingStatus,
    SellerType,
)


class Money(BaseModel):
    amount: Decimal | None = None
    currency: str | None = None


class FitmentResult(BaseModel):
    status: FitmentStatus
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_kind: EvidenceKind
    evidence_source: str | None = None
    evidence_detail: str | None = None
    missing_vehicle_attributes: list[str] = Field(default_factory=list)
    conflicting_attributes: list[str] = Field(default_factory=list)
    explanation: str
    verification_timestamp: datetime | None = None
    provenance: DataProvenance = DataProvenance.UNKNOWN


class IdentifierLink(BaseModel):
    left_raw: str
    right_raw: str
    relation: IdentifierRelation
    source: str
    evidence: str
    verification_status: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime


class PriceBreakdown(BaseModel):
    item_original: Money
    item_converted: Money | None = None
    shipping_original: Money | None = None
    shipping_converted: Money | None = None
    known_taxes_fees: Money | None = None
    estimated_landed: Money | None = None
    unknown_cost_components: list[str] = Field(default_factory=list)
    fx_rate: Decimal | None = None
    fx_provider: str | None = None
    fx_timestamp: datetime | None = None
    delivery_eligibility: DeliveryEligibility = DeliveryEligibility.UNKNOWN
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class VehicleQuery(BaseModel):
    make: str | None = None
    model: str | None = None
    generation: str | None = None
    year: int | None = None
    production_date: str | None = None
    market_spec: str | None = None
    body_style: str | None = None
    engine_code: str | None = None
    trim: str | None = None
    part_name: str | None = None
    oem_number: str | None = None
    condition: Condition | None = None
    preferred_countries: list[str] = Field(default_factory=list)
    destination_country: str | None = None
    currency: str = "EUR"
    vin: str | None = None
    budget: Decimal | None = None


class ListingView(BaseModel):
    """UI-facing listing projection with provenance labels."""

    id: str
    source_id: str
    title: str
    oem_as_stated: str | None = None
    manufacturer_as_stated: str | None = None
    condition: Condition = Condition.UNKNOWN
    completeness: AssemblyCompleteness = AssemblyCompleteness.UNKNOWN
    seller_name: str | None = None
    seller_country: str | None = None
    seller_type: SellerType = SellerType.UNKNOWN
    seller_rating: float | None = None
    seller_phone: str | None = None
    price: PriceBreakdown | None = None
    fitment: FitmentResult | None = None
    status: ListingStatus = ListingStatus.DISCOVERED
    last_checked: datetime | None = None
    canonical_url: str | None = None
    image_url: str | None = None
    is_demo_data: bool = False
    raw_fields: dict[str, Any] = Field(default_factory=dict)


class ConnectorCapabilities(BaseModel):
    source_id: str
    source_name: str
    supported_countries: list[str]
    supported_languages: list[str]
    supported_search_modes: list[str]
    authentication_required: bool
    rate_limit_notes: str
    access_method: str
    terms_notes: str
    pagination: bool
    price_capability: bool
    availability_capability: bool
    last_successful_test: datetime | None = None
    health_status: str  # untested | healthy | degraded | down | credentials_missing
    operational: bool = False


class SearchHit(BaseModel):
    url: HttpUrl | str
    title: str | None = None
    rank: int | None = None
    snippet: str | None = None
    country: str | None = None
    language: str | None = None
