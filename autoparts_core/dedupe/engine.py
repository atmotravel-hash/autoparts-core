"""Duplicate detection — deterministic first, probabilistic second.

A shared OEM does NOT make two offers duplicate listings.
A shared seller does NOT prove same physical item.
"""

from __future__ import annotations

from dataclasses import dataclass

from autoparts_core.core.enums import DuplicateOutcome
from autoparts_core.identity.oem import normalize_oem


@dataclass
class ListingFingerprint:
    id: int
    source_id: str
    source_listing_id: str
    canonical_url: str
    seller_id: int | None
    seller_name: str | None
    oem: str | None
    title: str
    price: float | None
    currency: str | None
    country: str | None
    image_hash: str | None = None


@dataclass
class DuplicateMatch:
    left_id: int
    right_id: int
    outcome: DuplicateOutcome
    score: float
    reasons: list[str]
    evidence: str
    algorithm_version: str = "0.1.0"


def compare_listings(a: ListingFingerprint, b: ListingFingerprint) -> DuplicateMatch:
    if a.id == b.id:
        return DuplicateMatch(a.id, b.id, DuplicateOutcome.NOT_DUPLICATE, 0.0, ["same_row"], "identity")

    reasons: list[str] = []
    score = 0.0

    # Level A — exact listing duplicate
    if a.source_id == b.source_id and a.source_listing_id == b.source_listing_id:
        return DuplicateMatch(
            a.id,
            b.id,
            DuplicateOutcome.EXACT_DUPLICATE,
            1.0,
            ["same_source_listing_id"],
            "Level A exact source id",
        )
    if a.canonical_url and a.canonical_url == b.canonical_url:
        return DuplicateMatch(
            a.id,
            b.id,
            DuplicateOutcome.EXACT_DUPLICATE,
            1.0,
            ["same_canonical_url"],
            "Level A exact URL",
        )

    # Level B signals
    if a.seller_id and a.seller_id == b.seller_id:
        score += 0.25
        reasons.append("same_seller_id")
    elif a.seller_name and b.seller_name and a.seller_name.lower() == b.seller_name.lower():
        score += 0.15
        reasons.append("same_seller_name")

    na, nb = normalize_oem(a.oem), normalize_oem(b.oem)
    if na and nb and na == nb:
        score += 0.2
        reasons.append("same_oem")  # NOT sufficient alone

    if _title_similarity(a.title, b.title) >= 0.85:
        score += 0.25
        reasons.append("similar_title")

    if a.price is not None and b.price is not None and a.currency == b.currency:
        if a.price == b.price:
            score += 0.15
            reasons.append("same_price")
        elif abs(a.price - b.price) / max(a.price, b.price) < 0.05:
            score += 0.08
            reasons.append("similar_price")

    if a.country and a.country == b.country:
        score += 0.05
        reasons.append("same_country")

    if a.image_hash and b.image_hash and a.image_hash == b.image_hash:
        score += 0.3
        reasons.append("same_image_hash")

    # Shared OEM alone must not become EXACT/HIGH without more evidence
    if reasons == ["same_oem"]:
        return DuplicateMatch(
            a.id,
            b.id,
            DuplicateOutcome.NOT_DUPLICATE,
            score,
            reasons + ["oem_alone_insufficient"],
            "Shared OEM without other signals — distinct offers possible",
        )

    if score >= 0.85:
        outcome = DuplicateOutcome.HIGH_CONFIDENCE_DUPLICATE
    elif score >= 0.55:
        outcome = DuplicateOutcome.POSSIBLE_DUPLICATE
    elif score >= 0.4:
        outcome = DuplicateOutcome.NEEDS_REVIEW
    else:
        outcome = DuplicateOutcome.NOT_DUPLICATE

    return DuplicateMatch(
        a.id,
        b.id,
        outcome,
        round(score, 3),
        reasons,
        f"score={score:.3f}; reasons={','.join(reasons)}",
    )


def _title_similarity(a: str, b: str) -> float:
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def find_duplicates(items: list[ListingFingerprint]) -> list[DuplicateMatch]:
    matches: list[DuplicateMatch] = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            m = compare_listings(items[i], items[j])
            if m.outcome != DuplicateOutcome.NOT_DUPLICATE:
                matches.append(m)
    return matches
