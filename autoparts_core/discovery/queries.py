"""Multilingual query generator for discovery (candidates only)."""

from __future__ import annotations

from autoparts_core.core.models import VehicleQuery
from autoparts_core.identity.taxonomy import map_part_name


PART_TRANSLATIONS = {
    "headlight": {
        "en": "headlight",
        "de": "Scheinwerfer",
        "pl": "reflektor",
        "ru": "фара",
        "uk": "фара",
        "ro": "far",
    },
    "front fender": {
        "en": "front fender",
        "de": "Kotflügel vorne",
        "pl": "błotnik przedni",
        "ru": "крыло переднее",
        "uk": "крило переднє",
        "ro": "aripă față",
    },
}

SIDE_TRANSLATIONS = {
    "left": {"en": "left", "de": "links", "pl": "lewy", "ru": "левая", "uk": "ліва", "ro": "stânga"},
    "right": {"en": "right", "de": "rechts", "pl": "prawy", "ru": "правая", "uk": "права", "ro": "dreapta"},
}


def generate_queries(vehicle: VehicleQuery, languages: list[str] | None = None) -> list[dict]:
    languages = languages or ["en", "de", "pl", "ru", "uk", "ro"]
    mapped = map_part_name(vehicle.part_name or "")
    concept = mapped.get("canonical_name") or vehicle.part_name or ""
    side = mapped.get("side")
    queries: list[dict] = []

    base_parts = [
        vehicle.make,
        vehicle.model,
        vehicle.generation,
        str(vehicle.year) if vehicle.year else None,
        vehicle.oem_number,
    ]

    for lang in languages:
        part_word = PART_TRANSLATIONS.get(concept, {}).get(lang, concept)
        side_word = SIDE_TRANSLATIONS.get(side or "", {}).get(lang, side)
        tokens = [t for t in base_parts + [side_word, part_word, "OEM" if vehicle.oem_number else None] if t]
        text = " ".join(str(t) for t in tokens)
        queries.append({"language": lang, "query": text, "purpose": "discovery_candidate"})

    if vehicle.oem_number:
        queries.insert(0, {"language": "en", "query": vehicle.oem_number, "purpose": "oem_exact"})

    # Deduplicate query text
    seen = set()
    unique = []
    for q in queries:
        if q["query"] not in seen:
            seen.add(q["query"])
            unique.append(q)
    return unique
