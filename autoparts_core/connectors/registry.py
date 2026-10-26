"""Connector registry. Never mark operational without a successful test."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from autoparts_core.connectors.autoria import AutoRiaConnector
from autoparts_core.connectors.base import SourceConnector
from autoparts_core.connectors.fixture import FixtureConnector
from autoparts_core.connectors.manual import ManualImportConnector
from autoparts_core.connectors.nine99_md import Nine99MdConnector
from autoparts_core.connectors.olx_graphql import build_olx_connectors


_REGISTRY: dict[str, SourceConnector] | None = None
_CATALOG: list[dict[str, Any]] | None = None


def load_source_catalog() -> list[dict[str, Any]]:
    global _CATALOG
    if _CATALOG is None:
        path = Path(__file__).resolve().parents[1] / "config" / "sources.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        _CATALOG = list(data.get("sources") or [])
    return _CATALOG


def default_live_source_ids() -> list[str]:
    path = Path(__file__).resolve().parents[1] / "config" / "sources.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(data.get("default_live_source_ids") or [])


def get_registry() -> dict[str, SourceConnector]:
    global _REGISTRY
    if _REGISTRY is None:
        fixture = FixtureConnector()
        manual = ManualImportConnector()
        nine = Nine99MdConnector()
        olx = build_olx_connectors()
        autoria = AutoRiaConnector()
        _REGISTRY = {
            fixture.source_id: fixture,
            manual.source_id: manual,
            nine.source_id: nine,
            **olx,
            autoria.source_id: autoria,
            # Candidate stubs — not operational
            "ebay": UntestedStubConnector("ebay", "eBay (authorized API required)"),
            "allegro": UntestedStubConnector("allegro", "Allegro (authorized API required)"),
            "brave_search": UntestedStubConnector("brave_search", "Brave Search API (key required)"),
            "autodoc": UntestedStubConnector(
                "autodoc",
                "AUTODOC (Cloudflare challenge — authorized access required)",
                health="blocked_challenge",
            ),
            "ovoko": UntestedStubConnector(
                "ovoko",
                "Ovoko/RRR (Cloudflare / partner API required)",
                health="blocked_challenge",
            ),
        }
    return _REGISTRY


class UntestedStubConnector(SourceConnector):
    """Placeholder for candidates that have not been tested or lack credentials."""

    def __init__(self, source_id: str, source_name: str, *, health: str = "credentials_missing") -> None:
        self.source_id = source_id
        self.source_name = source_name
        self._health = health

    def get_capabilities(self):
        from autoparts_core.core.models import ConnectorCapabilities

        return ConnectorCapabilities(
            source_id=self.source_id,
            source_name=self.source_name,
            supported_countries=[],
            supported_languages=[],
            supported_search_modes=[],
            authentication_required=True,
            rate_limit_notes="Unknown until authorized access is configured",
            access_method="OFFICIAL_API",
            terms_notes="Not operational. See config/sources.yaml.",
            pagination=False,
            price_capability=False,
            availability_capability=False,
            last_successful_test=None,
            health_status=self._health,
            operational=False,
        )

    def health_check(self):
        return {
            "ok": False,
            "status": self._health,
            "message": f"{self.source_name} is not operational in this build.",
        }

    def get_rate_limit_status(self):
        from autoparts_core.connectors.base import RateLimitStatus

        return RateLimitStatus(limited=True, notes="No credentials / blocked")

    def search(self, query, filters=None, pagination=None):
        raise RuntimeError(f"Connector {self.source_id} is not operational")

    def fetch_listing(self, identifier_or_url: str):
        raise RuntimeError(f"Connector {self.source_id} is not operational")

    def parse_listing(self, document):
        raise RuntimeError(f"Connector {self.source_id} is not operational")

    def parse_seller(self, document):
        raise RuntimeError(f"Connector {self.source_id} is not operational")

    def check_availability(self, listing):
        raise RuntimeError(f"Connector {self.source_id} is not operational")

    def get_price(self, listing):
        raise RuntimeError(f"Connector {self.source_id} is not operational")


def list_connectors() -> list[dict]:
    out = []
    for c in get_registry().values():
        caps = c.get_capabilities()
        out.append(caps.model_dump())
    return out


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
