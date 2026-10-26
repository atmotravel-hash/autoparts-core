"""Fitment evidence engine.

AI may parse text and explain evidence. AI must NOT independently declare
VERIFIED_EXACT based only on title, visual similarity, or LLM guess.
"""

from __future__ import annotations

from datetime import datetime

from autoparts_core.core.enums import DataProvenance, EvidenceKind, FitmentStatus
from autoparts_core.core.models import FitmentResult, VehicleQuery
from autoparts_core.identity.oem import normalize_oem


# Minimal trusted catalogue: OEM -> vehicle configs (fixture evidence only)
TRUSTED_OEM_CATALOGUE: dict[str, dict] = {
    "3G1941007A": {
        "make": "Volkswagen",
        "model": "Passat",
        "generation": "B8",
        "years": (2014, 2019),
        "side": "left",
        "part": "headlight",
        "technology": "LED",
        "source": "fixture_oem_catalogue_v1",
    },
    "3G1941008A": {
        "make": "Volkswagen",
        "model": "Passat",
        "generation": "B8",
        "years": (2014, 2019),
        "side": "right",
        "part": "headlight",
        "technology": "LED",
        "source": "fixture_oem_catalogue_v1",
    },
}


def evaluate_fitment(
    *,
    vehicle: VehicleQuery | None,
    oem_as_stated: str | None,
    title: str | None,
    seller_claim: str | None = None,
    catalogue: dict[str, dict] | None = None,
) -> FitmentResult:
    catalogue = catalogue if catalogue is not None else TRUSTED_OEM_CATALOGUE
    now = datetime.utcnow()
    missing: list[str] = []
    conflicts: list[str] = []

    if vehicle is None:
        return FitmentResult(
            status=FitmentStatus.INSUFFICIENT_DATA,
            confidence=0.0,
            evidence_kind=EvidenceKind.UNKNOWN,
            explanation="No vehicle configuration provided.",
            missing_vehicle_attributes=["make", "model", "year"],
            verification_timestamp=now,
            provenance=DataProvenance.UNKNOWN,
        )

    for attr in ("make", "model"):
        if not getattr(vehicle, attr, None):
            missing.append(attr)

    oem_norm = normalize_oem(oem_as_stated)
    catalog_hit = catalogue.get(oem_norm) if oem_norm else None

    if catalog_hit and vehicle.make and vehicle.model:
        make_ok = vehicle.make.lower() == catalog_hit["make"].lower()
        model_ok = vehicle.model.lower() == catalog_hit["model"].lower()
        year_ok = True
        if vehicle.year is not None:
            y0, y1 = catalog_hit["years"]
            year_ok = y0 <= vehicle.year <= y1
            if not year_ok:
                conflicts.append(f"year {vehicle.year} outside {y0}-{y1}")
        gen_ok = True
        if vehicle.generation:
            gen_ok = vehicle.generation.upper() == str(catalog_hit.get("generation", "")).upper()
            if not gen_ok:
                conflicts.append("generation mismatch")
        if make_ok and model_ok and year_ok and gen_ok and not conflicts:
            return FitmentResult(
                status=FitmentStatus.VERIFIED_EXACT,
                confidence=0.98,
                evidence_kind=EvidenceKind.OEM_CATALOG,
                evidence_source=catalog_hit["source"],
                evidence_detail=f"OEM {oem_as_stated} matched trusted catalogue for "
                f"{catalog_hit['make']} {catalog_hit['model']} {catalog_hit.get('generation')}",
                explanation="Exact OEM catalogue match for the requested vehicle configuration.",
                verification_timestamp=now,
                provenance=DataProvenance.VERIFIED_FACT,
            )
        if make_ok and model_ok and not conflicts:
            return FitmentResult(
                status=FitmentStatus.VERIFIED_COMPATIBLE,
                confidence=0.87,
                evidence_kind=EvidenceKind.SIMILAR_MODEL,
                evidence_source=catalog_hit["source"],
                evidence_detail="Catalogue make/model match; generation/year partially aligned",
                conflicting_attributes=conflicts,
                missing_vehicle_attributes=missing,
                explanation="Compatible per catalogue with incomplete generation/year confirmation.",
                verification_timestamp=now,
                provenance=DataProvenance.VERIFIED_FACT,
            )
        if conflicts:
            return FitmentResult(
                status=FitmentStatus.INCOMPATIBLE,
                confidence=0.22,
                evidence_kind=EvidenceKind.OEM_CATALOG,
                evidence_source=catalog_hit["source"],
                evidence_detail="; ".join(conflicts),
                conflicting_attributes=conflicts,
                explanation="Catalogue evidence conflicts with the requested vehicle attributes.",
                verification_timestamp=now,
                provenance=DataProvenance.VERIFIED_FACT,
            )

    # Part number present but not in trusted catalogue
    if oem_norm:
        return FitmentResult(
            status=FitmentStatus.LIKELY_COMPATIBLE if _title_mentions_vehicle(title, vehicle) else FitmentStatus.UNCONFIRMED,
            confidence=0.68 if _title_mentions_vehicle(title, vehicle) else 0.45,
            evidence_kind=EvidenceKind.PART_NUMBER if oem_norm else EvidenceKind.TITLE_ONLY,
            evidence_source="listing_fields",
            evidence_detail="OEM stated on listing but not verified in trusted catalogue",
            missing_vehicle_attributes=missing,
            explanation="Part number present without authoritative catalogue confirmation. "
            "Not declared as exact fitment.",
            verification_timestamp=now,
            provenance=DataProvenance.SELLER_CLAIM,
        )

    # Title-only — never VERIFIED_EXACT
    if _title_mentions_vehicle(title, vehicle):
        return FitmentResult(
            status=FitmentStatus.UNCONFIRMED,
            confidence=0.45,
            evidence_kind=EvidenceKind.TITLE_ONLY,
            evidence_source="listing_title",
            evidence_detail="Title similarity only — insufficient for exact fitment",
            explanation="Title mentions vehicle terms. Exact fitment cannot be declared from title alone.",
            verification_timestamp=now,
            provenance=DataProvenance.AI_INFERENCE,
        )

    if seller_claim:
        return FitmentResult(
            status=FitmentStatus.UNCONFIRMED,
            confidence=0.35,
            evidence_kind=EvidenceKind.SELLER_CLAIM,
            evidence_source="seller",
            evidence_detail=seller_claim[:500],
            explanation="Seller compatibility claim only — not independently verified.",
            verification_timestamp=now,
            provenance=DataProvenance.SELLER_CLAIM,
        )

    return FitmentResult(
        status=FitmentStatus.INSUFFICIENT_DATA,
        confidence=0.1,
        evidence_kind=EvidenceKind.UNKNOWN,
        missing_vehicle_attributes=missing or ["identifiers", "catalogue_evidence"],
        explanation="Insufficient evidence to assess fitment.",
        verification_timestamp=now,
        provenance=DataProvenance.UNKNOWN,
    )


def _title_mentions_vehicle(title: str | None, vehicle: VehicleQuery) -> bool:
    if not title:
        return False
    t = title.lower()
    make = (vehicle.make or "").lower()
    model = (vehicle.model or "").lower()
    gen = (vehicle.generation or "").lower()
    hits = 0
    if make and make in t:
        hits += 1
    if model and model in t:
        hits += 1
    if gen and gen.lower() in t:
        hits += 1
    if vehicle.year and str(vehicle.year) in t:
        hits += 1
    return hits >= 2
