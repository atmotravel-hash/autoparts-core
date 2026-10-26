"""Connector registry. Never mark operational without a successful test."""

from __future__ import annotations

from autoparts_core.connectors.base import SourceConnector
from autoparts_core.connectors.fixture import FixtureConnector
from autoparts_core.connectors.manual import ManualImportConnector


_REGISTRY: dict[str, SourceConnector] | None = None


def get_registry() -> dict[str, SourceConnector]:
    global _REGISTRY
    if _REGISTRY is None:
        fixture = FixtureConnector()
        manual = ManualImportConnector()
        _REGISTRY = {
            fixture.source_id: fixture,
            manual.source_id: manual,
            # Candidate stubs — not operational
            "ebay": UntestedStubConnector("ebay", "eBay (authorized API required)"),
            "allegro": UntestedStubConnector("allegro", "Allegro (authorized API required)"),
            "brave_search": UntestedStubConnector("brave_search", "Brave Search API (key required)"),
        }
    return _REGISTRY


class UntestedStubConnector(SourceConnector):
    """Placeholder for candidates that have not been tested."""

    def __init__(self, source_id: str, source_name: str) -> None:
        self.source_id = source_id
        self.source_name = source_name

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
            terms_notes="Not tested. Credentials absent. Do not claim operational.",
            pagination=False,
            price_capability=False,
            availability_capability=False,
            last_successful_test=None,
            health_status="credentials_missing",
            operational=False,
        )

    def health_check(self):
        return {
            "ok": False,
            "status": "credentials_missing",
            "message": f"{self.source_name} has not been tested in this environment.",
        }

    def get_rate_limit_status(self):
        from autoparts_core.connectors.base import RateLimitStatus

        return RateLimitStatus(limited=True, notes="No credentials")

    def search(self, query, filters=None, pagination=None):
        raise RuntimeError(f"Connector {self.source_id} is not operational (untested / no credentials)")

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
