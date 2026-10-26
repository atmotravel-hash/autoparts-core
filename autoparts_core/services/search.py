"""Search orchestration across operational connectors."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from autoparts_core.connectors.registry import get_registry
from autoparts_core.core.enums import FitmentStatus
from autoparts_core.core.models import ListingView, Money, PriceBreakdown, VehicleQuery
from autoparts_core.db.models import FitmentRecord, Listing, PriceObservation, SearchRunHistory, Seller
from autoparts_core.discovery.queries import generate_queries
from autoparts_core.fitment.engine import evaluate_fitment
from autoparts_core.identity.oem import normalize_oem
from autoparts_core.pricing.landed import build_price_breakdown
from autoparts_core.services.ingestion import ingest_parsed_listing


def run_search(
    session: Session,
    vehicle: VehicleQuery,
    *,
    source_ids: list[str] | None = None,
    persist: bool = True,
) -> dict:
    registry = get_registry()
    source_ids = source_ids or ["fixture"]
    queries = generate_queries(vehicle)
    primary = queries[0]["query"] if queries else (vehicle.part_name or vehicle.oem_number or "")

    filters: dict = {}
    if vehicle.oem_number:
        filters["oem"] = vehicle.oem_number
    if vehicle.preferred_countries:
        filters["country"] = vehicle.preferred_countries
    if vehicle.condition:
        filters["condition"] = vehicle.condition.value

    all_views: list[ListingView] = []
    errors: list[dict] = []
    found = 0

    for sid in source_ids:
        connector = registry.get(sid)
        if connector is None:
            errors.append({"source": sid, "error": "unknown_source"})
            continue
        caps = connector.get_capabilities()
        if not caps.operational:
            errors.append(
                {
                    "source": sid,
                    "error": "not_operational",
                    "health": caps.health_status,
                    "message": caps.terms_notes,
                }
            )
            continue
        try:
            hits = connector.search(primary, filters=filters, pagination={"limit": 50})
            found += len(hits)
            for hit in hits:
                try:
                    doc = connector.fetch_listing(str(hit.url))
                    parsed = connector.parse_listing(doc)
                    if persist:
                        listing, _ = ingest_parsed_listing(session, sid, parsed)
                        view = listing_to_view(session, listing, vehicle)
                    else:
                        view = parsed_to_view(parsed, vehicle, sid)
                    all_views.append(view)
                except Exception as exc:  # noqa: BLE001 — isolate per listing
                    errors.append({"source": sid, "url": str(hit.url), "error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            errors.append({"source": sid, "error": str(exc)})

    # Rank: prefer better fitment, then lower landed cost when known
    def sort_key(v: ListingView):
        fit_rank = {
            FitmentStatus.VERIFIED_EXACT: 0,
            FitmentStatus.VERIFIED_COMPATIBLE: 1,
            FitmentStatus.LIKELY_COMPATIBLE: 2,
            FitmentStatus.UNCONFIRMED: 3,
            FitmentStatus.INSUFFICIENT_DATA: 4,
            FitmentStatus.INCOMPATIBLE: 5,
        }
        fr = fit_rank.get(v.fitment.status if v.fitment else FitmentStatus.INSUFFICIENT_DATA, 9)
        landed = None
        if v.price and v.price.estimated_landed and v.price.estimated_landed.amount is not None:
            landed = float(v.price.estimated_landed.amount)
        return (fr, landed if landed is not None else 1e18)

    all_views.sort(key=sort_key)

    session.add(
        SearchRunHistory(
            workflow="vehicle_part" if vehicle.make else "oem_or_name",
            params_json=vehicle.model_dump_json(),
            result_count=len(all_views),
            label=primary[:200],
        )
    )

    return {
        "query": primary,
        "queries_generated": queries,
        "found_hits": found,
        "results": all_views,
        "errors": errors,
        "demo_data_present": any(v.is_demo_data for v in all_views),
    }


def search_by_oem(session: Session, oem: str, **kwargs) -> dict:
    return run_search(session, VehicleQuery(oem_number=oem), **kwargs)


def search_by_part_name(session: Session, name: str, **kwargs) -> dict:
    return run_search(session, VehicleQuery(part_name=name), **kwargs)


def listing_to_view(session: Session, listing: Listing, vehicle: VehicleQuery | None) -> ListingView:
    seller = session.get(Seller, listing.seller_id) if listing.seller_id else None
    price_row = (
        session.query(PriceObservation)
        .filter_by(listing_id=listing.id)
        .order_by(PriceObservation.observed_at.desc())
        .first()
    )
    target = (vehicle.currency if vehicle else None) or "EUR"
    price = None
    if price_row:
        price = build_price_breakdown(
            item_amount=price_row.amount,
            item_currency=price_row.currency,
            shipping_amount=price_row.shipping_amount,
            shipping_currency=price_row.shipping_currency,
            target_currency=target,
            delivery_eligibility=price_row.destination_eligibility,
        )
        # Persist converted fields on latest observation (does not overwrite original amount)
        if price.item_converted and price.item_converted.amount is not None:
            price_row.converted_amount = float(price.item_converted.amount)
            price_row.converted_currency = target
            price_row.fx_rate = float(price.fx_rate) if price.fx_rate is not None else None
            price_row.fx_provider = price.fx_provider
            price_row.fx_timestamp = price.fx_timestamp
            if price.estimated_landed and price.estimated_landed.amount is not None:
                price_row.estimated_landed = float(price.estimated_landed.amount)
            price_row.warnings = "; ".join(price.warnings)
            price_row.assumptions = "; ".join(price.assumptions)

    fitment = evaluate_fitment(
        vehicle=vehicle,
        oem_as_stated=listing.oem_as_stated,
        title=listing.title,
        seller_claim=listing.seller_compat_claim,
    )
    # Store fitment record
    session.add(
        FitmentRecord(
            listing_id=listing.id,
            status=fitment.status.value,
            confidence=fitment.confidence,
            evidence_kind=fitment.evidence_kind.value,
            evidence_source=fitment.evidence_source,
            evidence_detail=fitment.evidence_detail,
            missing_attributes=",".join(fitment.missing_vehicle_attributes),
            conflicting_attributes=",".join(fitment.conflicting_attributes),
            explanation=fitment.explanation,
            provenance=fitment.provenance.value,
            verification_timestamp=fitment.verification_timestamp or datetime.utcnow(),
        )
    )

    image_url = listing.images[0].public_url if listing.images else None

    return ListingView(
        id=listing.internal_id,
        source_id=listing.source_id,
        title=listing.title,
        oem_as_stated=listing.oem_as_stated,
        manufacturer_as_stated=listing.manufacturer_as_stated,
        condition=listing.condition,  # type: ignore[arg-type]
        completeness=listing.assembly_completeness,  # type: ignore[arg-type]
        seller_name=seller.display_name if seller else None,
        seller_country=seller.country if seller else listing.country,
        seller_type=seller.seller_type if seller else "UNKNOWN",  # type: ignore[arg-type]
        seller_rating=seller.rating if seller else None,
        seller_phone=seller.public_phone if seller else None,
        price=price,
        fitment=fitment,
        status=listing.availability_status,  # type: ignore[arg-type]
        last_checked=listing.last_checked,
        canonical_url=listing.canonical_url,
        image_url=image_url,
        is_demo_data=listing.is_demo_data,
    )


def parsed_to_view(parsed, vehicle: VehicleQuery | None, source_id: str) -> ListingView:
    from autoparts_core.core.enums import AssemblyCompleteness, Condition, ListingStatus

    price = build_price_breakdown(
        item_amount=parsed.price_amount,
        item_currency=parsed.price_currency,
        shipping_amount=parsed.shipping_amount,
        shipping_currency=parsed.shipping_currency,
        target_currency=(vehicle.currency if vehicle else "EUR"),
        delivery_eligibility=parsed.delivery_eligibility,
    )
    fitment = evaluate_fitment(
        vehicle=vehicle,
        oem_as_stated=parsed.oem_as_stated,
        title=parsed.title,
        seller_claim=parsed.seller_compat_claim,
    )
    return ListingView(
        id=f"tmp_{parsed.source_listing_id}",
        source_id=source_id,
        title=parsed.title,
        oem_as_stated=parsed.oem_as_stated,
        manufacturer_as_stated=parsed.manufacturer_as_stated,
        condition=Condition(parsed.condition) if parsed.condition in Condition._value2member_map_ else Condition.UNKNOWN,
        completeness=AssemblyCompleteness(parsed.assembly_completeness)
        if parsed.assembly_completeness in AssemblyCompleteness._value2member_map_
        else AssemblyCompleteness.UNKNOWN,
        seller_name=(parsed.seller or {}).get("display_name"),
        seller_country=(parsed.seller or {}).get("country") or parsed.country,
        price=price,
        fitment=fitment,
        status=ListingStatus(parsed.availability_status)
        if parsed.availability_status in ListingStatus._value2member_map_
        else ListingStatus.PARSED,
        canonical_url=parsed.canonical_url,
        image_url=(parsed.image_urls or [None])[0],
        is_demo_data=parsed.is_demo_data,
    )
