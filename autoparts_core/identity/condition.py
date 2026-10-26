"""Condition and assembly completeness normalization."""

from __future__ import annotations

from autoparts_core.core.enums import AssemblyCompleteness, Condition

CONDITION_MAP: list[tuple[tuple[str, ...], Condition]] = [
    (("new aftermarket", "aftermarket new", "nieuw aftermarket"), Condition.NEW_AFTERMARKET),
    (("brand new", "new", "neu", "nowy", "nou", "новый", "новий", "neuf", "nuevo"), Condition.NEW),
    (("refurbished", "reconditioned", "aufgearbeitet", "regenerowany"), Condition.REFURBISHED),
    (("for parts", "na części", "на запчасти", "pour pieces"), Condition.FOR_PARTS),
    (("damaged", "defect", "kaputt", "uszkodzony", "поврежден", "пошкоджен"), Condition.DAMAGED),
    (("salvage", "wrack", "szrot"), Condition.SALVAGE),
    (("used", "gebraucht", "używany", "uzywany", "б/у", "вживане", "second hand", "ocasion"), Condition.USED),
]

COMPLETENESS_MAP: list[tuple[tuple[str, ...], AssemblyCompleteness]] = [
    (("complete", "full assembly", "komplett", "complet"), AssemblyCompleteness.COMPLETE_ASSEMBLY),
    (("housing only", "gehäuse", "obudowa"), AssemblyCompleteness.HOUSING_ONLY),
    (("lens only", "glass only", "scheibe"), AssemblyCompleteness.LENS_ONLY),
    (("module only", "ballast only", "steuergerät"), AssemblyCompleteness.ELECTRONIC_MODULE_ONLY),
    (("bracket", "mounting only", "halter"), AssemblyCompleteness.MOUNTING_PARTS_ONLY),
    (("partial", "incomplete", "teilweise"), AssemblyCompleteness.PARTIAL_ASSEMBLY),
]


def normalize_condition(raw: str | None) -> tuple[Condition, str | None]:
    if not raw:
        return Condition.UNKNOWN, None
    text = raw.strip().lower()
    for aliases, cond in CONDITION_MAP:
        for a in aliases:
            if a in text:
                return cond, raw.strip()
    return Condition.UNKNOWN, raw.strip()


def normalize_completeness(raw: str | None) -> tuple[AssemblyCompleteness, str | None]:
    if not raw:
        return AssemblyCompleteness.UNKNOWN, None
    text = raw.strip().lower()
    for aliases, comp in COMPLETENESS_MAP:
        for a in aliases:
            if a in text:
                return comp, raw.strip()
    return AssemblyCompleteness.UNKNOWN, raw.strip()
