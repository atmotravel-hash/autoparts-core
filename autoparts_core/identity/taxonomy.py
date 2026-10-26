"""Multilingual part-name taxonomy and synonyms."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PartConcept:
    concept_id: str
    canonical_en: str
    category: str
    aliases: tuple[str, ...]
    default_side_required: bool = False
    default_position: str | None = None


PART_CONCEPTS: tuple[PartConcept, ...] = (
    PartConcept(
        "headlight",
        "headlight",
        "lighting",
        (
            "headlight",
            "headlamp",
            "scheinwerfer",
            "reflektor",
            "фара",
            "фари",
            "far",
            "faruri",
            "phare",
            "faro",
            "koplamp",
            "světlomet",
            "svetlomet",
        ),
        default_side_required=True,
        default_position="front",
    ),
    PartConcept(
        "front_fender",
        "front fender",
        "body",
        (
            "front fender",
            "front wing",
            "left front fender",
            "left front wing",
            "kotflügel",
            "kotflugel",
            "błotnik",
            "blotnik",
            "крыло",
            "крило",
            "aripă",
            "aripa",
            "aile",
            "parafango",
            "guardabarros",
        ),
        default_side_required=True,
        default_position="front",
    ),
    PartConcept(
        "bumper",
        "bumper",
        "body",
        ("bumper", "stoßstange", "stossstange", "zderzak", "бампер", "bamper", "bara", "pare-chocs"),
        default_position="front",
    ),
    PartConcept(
        "side_mirror",
        "side mirror",
        "body",
        ("side mirror", "wing mirror", "außenspiegel", "aussenspiegel", "lusterko", "зеркало", "дзеркало", "oglinde"),
        default_side_required=True,
    ),
)

SIDE_ALIASES = {
    "left": (
        "left",
        "lh",
        "links",
        "lewy",
        "lewa",
        "левая",
        "левый",
        "левое",
        "ліва",
        "лівий",
        "ліве",
        "stânga",
        "stanga",
        "gauche",
        "sinistro",
        "izquierdo",
    ),
    "right": (
        "right",
        "rh",
        "rechts",
        "prawy",
        "prawa",
        "правая",
        "правый",
        "правое",
        "права",
        "правий",
        "праве",
        "dreapta",
        "droite",
        "destro",
        "derecho",
    ),
}


def resolve_part_concept(text: str | None) -> PartConcept | None:
    if not text:
        return None
    lowered = text.strip().lower()
    for concept in PART_CONCEPTS:
        for alias in concept.aliases:
            if alias in lowered or lowered == alias:
                return concept
    return None


def detect_side(text: str | None) -> str | None:
    if not text:
        return None
    lowered = text.strip().lower()
    for side, aliases in SIDE_ALIASES.items():
        for a in aliases:
            # word-ish match
            if re_word_in(a, lowered):
                return side
    return None


def re_word_in(needle: str, haystack: str) -> bool:
    import re

    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack, flags=re.IGNORECASE) is not None


def map_part_name(text: str) -> dict:
    concept = resolve_part_concept(text)
    side = detect_side(text)
    return {
        "input": text,
        "concept_id": concept.concept_id if concept else None,
        "canonical_name": concept.canonical_en if concept else None,
        "category": concept.category if concept else None,
        "side": side,
        "position": concept.default_position if concept else None,
        "matched": concept is not None,
    }
