"""Connector registry — only zero-hassle, tested sources by default."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from autoparts_core.connectors.base import SourceConnector
from autoparts_core.connectors.fixture import FixtureConnector
from autoparts_core.connectors.manual import ManualImportConnector
from autoparts_core.connectors.nine99_md import Nine99MdConnector
from autoparts_core.connectors.olx_graphql import build_olx_connectors


_REGISTRY: dict[str, SourceConnector] | None = None
_CATALOG: list[dict[str, Any]] | None = None


def _yaml() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "config" / "sources.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_source_catalog() -> list[dict[str, Any]]:
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = list(_yaml().get("sources") or [])
    return _CATALOG


def load_deferred_sources() -> list[dict[str, Any]]:
    return list(_yaml().get("deferred_sources") or [])


def default_live_source_ids() -> list[str]:
    return list(_yaml().get("default_live_source_ids") or [])


def get_registry() -> dict[str, SourceConnector]:
    """Active connectors only (no stub noise for blocked/credential sources)."""
    global _REGISTRY
    if _REGISTRY is None:
        fixture = FixtureConnector()
        manual = ManualImportConnector()
        nine = Nine99MdConnector()
        olx = build_olx_connectors()
        _REGISTRY = {
            fixture.source_id: fixture,
            manual.source_id: manual,
            nine.source_id: nine,
            **olx,
        }
        # Optional: AUTO.RIA only if explicitly enabled AND key present
        from autoparts_core.config.settings import get_settings

        settings = get_settings()
        if settings.enable_autoria and settings.autoria_api_key:
            from autoparts_core.connectors.autoria import AutoRiaConnector

            autoria = AutoRiaConnector()
            _REGISTRY[autoria.source_id] = autoria
    return _REGISTRY


def list_connectors() -> list[dict]:
    return [c.get_capabilities().model_dump() for c in get_registry().values()]


def operational_source_ids(*, include_fixture: bool = False) -> list[str]:
    ids = []
    for sid, connector in get_registry().items():
        caps = connector.get_capabilities()
        if not caps.operational:
            continue
        if sid == "fixture" and not include_fixture:
            continue
        if sid == "manual":
            continue
        ids.append(sid)
    return ids
