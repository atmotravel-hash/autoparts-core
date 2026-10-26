"""Persist parsed listings with provenance. Idempotent on (source_id, source_listing_id)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from autoparts_core.connectors.base import ParsedListing
from autoparts_core.db.models import (
    AuditEvent,
    Listing,
    ListingImage,
    PriceObservation,
    Seller,
    ShippingOption,
)
from autoparts_core.identity.condition import normalize_completeness, normalize_condition
from autoparts_core.identity.oem import preserve_raw


def upsert_seller(session: Session, seller_data: dict, evidence_source: str) -> Seller | None:
    if not seller_data:
        return None
    name = seller_data.get("display_name") or seller_data.get("name")
    if not name:
        return None
    internal = seller_data.get("internal_id") or f"sel_{uuid.uuid4().hex[:12]}"
    existing = (
        session.query(Seller)
        .filter(
            (Seller.display_name == name)
            & (Seller.country == seller_data.get("country"))
            & (Seller.public_website == seller_data.get("public_website"))
        )
        .first()
    )
    if existing:
        return existing
    seller = Seller(
        internal_id=internal,
        display_name=name,
        business_name=seller_data.get("business_name"),
        public_phone=seller_data.get("public_phone"),
        public_email=seller_data.get("public_email"),
        public_website=seller_data.get("public_website"),
        marketplace_profile=seller_data.get("marketplace_profile"),
        city=seller_data.get("city"),
        country=seller_data.get("country"),
        seller_type=seller_data.get("seller_type", "UNKNOWN"),
        rating=seller_data.get("rating"),
        review_count=seller_data.get("review_count"),
        evidence_source=evidence_source,
        last_verification=datetime.utcnow(),
    )
    session.add(seller)
    session.flush()
    return seller


def ingest_parsed_listing(session: Session, source_id: str, parsed: ParsedListing) -> tuple[Listing, bool]:
    """Return (listing, created)."""
    existing = (
        session.query(Listing)
        .filter_by(source_id=source_id, source_listing_id=parsed.source_listing_id)
        .first()
    )
    cond, cond_raw = normalize_condition(parsed.condition_raw or parsed.condition)
    completeness, _ = normalize_completeness(parsed.assembly_completeness)

    seller = upsert_seller(session, parsed.seller, evidence_source=parsed.canonical_url)

    if existing:
        existing.title = parsed.title
        existing.last_checked = datetime.utcnow()
        existing.availability_status = parsed.availability_status
        existing.oem_as_stated = preserve_raw(parsed.oem_as_stated)
        existing.manufacturer_as_stated = preserve_raw(parsed.manufacturer_as_stated)
        existing.condition = cond.value
        existing.condition_raw = cond_raw
        existing.assembly_completeness = (
            completeness.value if hasattr(completeness, "value") else str(completeness)
        )
        listing = existing
        created = False
    else:
        listing = Listing(
            internal_id=f"lst_{uuid.uuid4().hex[:12]}",
            source_id=source_id,
            source_listing_id=parsed.source_listing_id,
            canonical_url=parsed.canonical_url,
            original_url=parsed.original_url,
            title=parsed.title,
            original_description=parsed.description,
            oem_as_stated=preserve_raw(parsed.oem_as_stated),
            manufacturer_as_stated=preserve_raw(parsed.manufacturer_as_stated),
            condition=cond.value,
            condition_raw=cond_raw or parsed.condition_raw,
            assembly_completeness=completeness.value
            if hasattr(completeness, "value")
            else str(completeness),
            side_position=parsed.side_position,
            quantity=parsed.quantity,
            visible_defects=parsed.visible_defects,
            seller_compat_claim=parsed.seller_compat_claim,
            last_checked=datetime.utcnow(),
            availability_status=parsed.availability_status,
            extraction_confidence=parsed.extraction_confidence,
            is_demo_data=parsed.is_demo_data,
            seller_id=seller.id if seller else None,
            country=parsed.country,
        )
        session.add(listing)
        session.flush()
        created = True

    # Always append price observation (preserve history)
    if parsed.price_amount is not None or parsed.shipping_amount is not None:
        session.add(
            PriceObservation(
                listing_id=listing.id,
                amount=parsed.price_amount,
                currency=parsed.price_currency,
                shipping_amount=parsed.shipping_amount,
                shipping_currency=parsed.shipping_currency or parsed.price_currency,
                destination_eligibility=parsed.delivery_eligibility,
                observed_at=datetime.utcnow(),
            )
        )

    if parsed.delivery_eligibility or parsed.shipping_amount is not None:
        session.add(
            ShippingOption(
                listing_id=listing.id,
                destination_country=parsed.seller.get("ships_to") or parsed.country or "XX",
                amount=parsed.shipping_amount,
                currency=parsed.shipping_currency or parsed.price_currency,
                eligibility=parsed.delivery_eligibility,
                eta_text=parsed.delivery_eta,
                evidence="connector_parse",
            )
        )

    for url in parsed.image_urls:
        exists_img = session.query(ListingImage).filter_by(listing_id=listing.id, public_url=url).first()
        if not exists_img:
            session.add(ListingImage(listing_id=listing.id, public_url=url, source=source_id))

    session.add(
        AuditEvent(
            action="ingest_create" if created else "ingest_update",
            entity_type="listing",
            entity_id=listing.internal_id,
            detail=json.dumps({"source_id": source_id, "url": parsed.canonical_url}),
        )
    )
    session.flush()
    return listing, created
