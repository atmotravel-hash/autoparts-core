"""OEM / manufacturer identifier normalization.

Preserves meaningful characters. Does not strip leading zeros or suffixes
that may encode configuration. Similar numbers ≠ interchangeability.
"""

from __future__ import annotations

import re
import unicodedata


def preserve_raw(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


def normalize_oem(value: str | None) -> str | None:
    """Normalize for lookup while retaining a parallel raw value elsewhere.

    Rules:
    - Unicode NFKC
    - Uppercase Latin letters
    - Remove only whitespace and common separators (space, hyphen, underscore)
    - Keep letters, digits, and meaningful suffixes (e.g. trailing letter codes)
    - Do NOT strip leading zeros
    """
    raw = preserve_raw(value)
    if raw is None:
        return None
    text = unicodedata.normalize("NFKC", raw).upper()
    text = re.sub(r"[\s\-_./]", "", text)
    # Keep alphanumeric only after separator strip — but original raw is preserved by caller
    if not text:
        return None
    return text


def oem_lookup_keys(value: str | None) -> list[str]:
    """Generate deterministic lookup keys without claiming equivalence."""
    raw = preserve_raw(value)
    if not raw:
        return []
    keys = [raw]
    norm = normalize_oem(raw)
    if norm and norm not in keys:
        keys.append(norm)
    return keys


def superficially_similar(a: str | None, b: str | None, *, max_distance: int = 1) -> bool:
    """Detect superficial similarity — NEVER proof of interchangeability."""
    na, nb = normalize_oem(a), normalize_oem(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if abs(len(na) - len(nb)) > max_distance:
        return False
    # Hamming-ish for equal length
    if len(na) == len(nb):
        diffs = sum(x != y for x, y in zip(na, nb))
        return diffs <= max_distance
    return False
