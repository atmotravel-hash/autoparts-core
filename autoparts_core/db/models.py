"""SQLAlchemy persistent schema (Spec §13)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from autoparts_core.db.base import Base


def _utcnow() -> datetime:
    return datetime.utcnow()


class CountryRecord(Base):
    __tablename__ = "country_registry"

    iso_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(128))
    default_currency: Mapped[str] = mapped_column(String(3))
    languages: Mapped[str] = mapped_column(String(128), default="")
    enabled_sources: Mapped[str] = mapped_column(String(256), default="")
    delivery_region: Mapped[str] = mapped_column(String(32), default="EU")
    eu_member: Mapped[bool] = mapped_column(Boolean, default=False)
    tax_import_notes: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class Marketplace(Base):
    __tablename__ = "marketplaces"

    source_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    access_method: Mapped[str] = mapped_column(String(64))
    health_status: Mapped[str] = mapped_column(String(32), default="untested")
    operational: Mapped[bool] = mapped_column(Boolean, default=False)
    terms_notes: Mapped[str] = mapped_column(Text, default="")
    last_successful_test: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    supported_countries: Mapped[str] = mapped_column(String(512), default="")
    supported_languages: Mapped[str] = mapped_column(String(256), default="")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    make: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(64), index=True)
    generation: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    year_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    year_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class VehicleConfiguration(Base):
    __tablename__ = "vehicle_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vehicles.id"), nullable=True)
    make: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(64), index=True)
    generation: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    production_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    market_spec: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    body_style: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    engine_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    transmission: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    trim: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    drivetrain: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    steering: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    vin_derived_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Part(Base):
    __tablename__ = "parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    internal_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    canonical_name: Mapped[str] = mapped_column(String(256))
    category: Mapped[str] = mapped_column(String(64), default="unknown")
    manufacturer: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    side: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    technology: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    assembly_completeness: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    verification_status: Mapped[str] = mapped_column(String(64), default="UNCONFIRMED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class PartIdentifier(Base):
    __tablename__ = "part_identifiers"
    __table_args__ = (UniqueConstraint("raw_value", "id_type", "part_id", name="uq_part_id_raw"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)
    id_type: Mapped[str] = mapped_column(String(32))  # OEM, MFR, AFTERMARKET, RAW
    raw_value: Mapped[str] = mapped_column(String(128), index=True)
    normalized_value: Mapped[str] = mapped_column(String(128), index=True)
    source: Mapped[str] = mapped_column(String(128), default="")


class PartEquivalence(Base):
    __tablename__ = "part_equivalences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    left_identifier: Mapped[str] = mapped_column(String(128), index=True)
    right_identifier: Mapped[str] = mapped_column(String(128), index=True)
    relation: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(128))
    evidence: Mapped[str] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(64))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class FitmentRecord(Base):
    __tablename__ = "fitment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("listings.id"), nullable=True, index=True)
    part_id: Mapped[Optional[int]] = mapped_column(ForeignKey("parts.id"), nullable=True)
    vehicle_config_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vehicle_configurations.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(64), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    evidence_kind: Mapped[str] = mapped_column(String(64))
    evidence_source: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    evidence_detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    missing_attributes: Mapped[str] = mapped_column(Text, default="")
    conflicting_attributes: Mapped[str] = mapped_column(Text, default="")
    explanation: Mapped[str] = mapped_column(Text)
    provenance: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    verification_timestamp: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Seller(Base):
    __tablename__ = "sellers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    internal_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(256), index=True)
    business_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    public_phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    public_email: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    public_website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    marketplace_profile: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    public_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True, index=True)
    seller_type: Mapped[str] = mapped_column(String(32), default="UNKNOWN")
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    evidence_source: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    last_verification: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class SellerContact(Base):
    __tablename__ = "seller_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("sellers.id"), index=True)
    contact_type: Mapped[str] = mapped_column(String(32))
    value: Mapped[str] = mapped_column(String(512))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[str] = mapped_column(String(256), default="")


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (
        UniqueConstraint("source_id", "source_listing_id", name="uq_source_listing"),
        Index("ix_listings_oem", "oem_as_stated"),
        Index("ix_listings_url", "canonical_url"),
        Index("ix_listings_status", "availability_status"),
        Index("ix_listings_condition", "condition"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    internal_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("marketplaces.source_id"), index=True)
    source_listing_id: Mapped[str] = mapped_column(String(128))
    canonical_url: Mapped[str] = mapped_column(String(1024))
    original_url: Mapped[str] = mapped_column(String(1024))
    title: Mapped[str] = mapped_column(String(512))
    original_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    oem_as_stated: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    manufacturer_as_stated: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    condition: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    condition_raw: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    assembly_completeness: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    side_position: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    quantity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    visible_defects: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seller_compat_claim: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    publication_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    source_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    first_discovered: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    last_checked: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    availability_status: Mapped[str] = mapped_column(String(64), default="DISCOVERED")
    parser_version: Mapped[str] = mapped_column(String(32), default="0.1.0")
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)
    seller_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sellers.id"), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True, index=True)

    seller = relationship("Seller")
    prices = relationship("PriceObservation", back_populates="listing")
    images = relationship("ListingImage", back_populates="listing")


class ListingPartLink(Base):
    __tablename__ = "listing_part_links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    part_id: Mapped[int] = mapped_column(ForeignKey("parts.id"), index=True)
    link_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    evidence: Mapped[str] = mapped_column(Text, default="")


class ListingImage(Base):
    __tablename__ = "listing_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    public_url: Mapped[str] = mapped_column(String(1024))
    source: Mapped[str] = mapped_column(String(128), default="")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    image_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="referenced")

    listing = relationship("Listing", back_populates="images")


class PriceObservation(Base):
    __tablename__ = "price_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    price_type: Mapped[str] = mapped_column(String(32), default="item")
    vat_status: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    shipping_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    shipping_currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    destination_eligibility: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    fx_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fx_provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fx_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    converted_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    converted_currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    estimated_landed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    assumptions: Mapped[str] = mapped_column(Text, default="")
    warnings: Mapped[str] = mapped_column(Text, default="")
    observed_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, index=True)

    listing = relationship("Listing", back_populates="prices")


class ShippingOption(Base):
    __tablename__ = "shipping_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    destination_country: Mapped[str] = mapped_column(String(2))
    amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    eligibility: Mapped[str] = mapped_column(String(64), default="UNKNOWN")
    eta_text: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    evidence: Mapped[str] = mapped_column(Text, default="")


class SourcePage(Base):
    __tablename__ = "source_pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    domain: Mapped[str] = mapped_column(String(256), index=True)
    fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="queued")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_text: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(64))
    country: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    status: Mapped[str] = mapped_column(String(32), default="created")


class DiscoveryRun(Base):
    __tablename__ = "discovery_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_query_id: Mapped[Optional[int]] = mapped_column(ForeignKey("search_queries.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="running")
    report: Mapped[str] = mapped_column(Text, default="")


class ExtractionRun(Base):
    __tablename__ = "extraction_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_page_id: Mapped[Optional[int]] = mapped_column(ForeignKey("source_pages.id"), nullable=True)
    listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("listings.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")
    error_category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    detail: Mapped[str] = mapped_column(Text, default="")


class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    left_listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    right_listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"), index=True)
    outcome: Mapped[str] = mapped_column(String(64))
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    match_reasons: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    algorithm_version: Mapped[str] = mapped_column(String(32), default="0.1.0")
    review_status: Mapped[str] = mapped_column(String(32), default="pending")
    reviewer_action: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class MergeHistory(Base):
    __tablename__ = "merge_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    survivor_id: Mapped[str] = mapped_column(String(64))
    merged_id: Mapped[str] = mapped_column(String(64))
    payload_json: Mapped[str] = mapped_column(Text)
    reversed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    reversed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    __table_args__ = (UniqueConstraint("base", "quote", "as_of", "provider", name="uq_fx"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    base: Mapped[str] = mapped_column(String(3))
    quote: Mapped[str] = mapped_column(String(3))
    rate: Mapped[float] = mapped_column(Float)
    provider: Mapped[str] = mapped_column(String(64))
    as_of: Mapped[datetime] = mapped_column(DateTime)
    is_fixture: Mapped[bool] = mapped_column(Boolean, default=False)


class JobQueueItem(Base):
    __tablename__ = "job_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    payload_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class ErrorEvent(Base):
    __tablename__ = "error_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class UserSetting(Base):
    __tablename__ = "user_settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class SearchRunHistory(Base):
    __tablename__ = "search_run_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow: Mapped[str] = mapped_column(String(64))
    params_json: Mapped[str] = mapped_column(Text)
    result_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    label: Mapped[str] = mapped_column(String(256), default="")
