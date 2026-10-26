"""Parameterized JSON-LD catalog connectors.

Product scope keeps Prom/Flagma as dedicated modules.
This registry builder stays empty (former Bazar.bg removed from scope).
"""

from __future__ import annotations

from typing import Any

from autoparts_core.connectors.base import SourceConnector

JSONLD_MARKETS: dict[str, dict[str, Any]] = {}


def build_jsonld_catalog_connectors() -> dict[str, SourceConnector]:
    return {}
