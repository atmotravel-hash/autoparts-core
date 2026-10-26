"""Application settings. Starts without optional API credentials."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AutoParts Intelligence"
    app_version: str = "0.2.1"
    demo_mode: bool = True
    # When true, Vehicle Search uses live GraphQL catalogs (OLX, 999.md) in addition to optional fixtures
    enable_live_graphql: bool = True
    include_fixture_in_live_search: bool = False
    database_url: str = Field(default=f"sqlite:///{ROOT / 'data' / 'autoparts.db'}")
    default_currency: str = "EUR"
    destination_country: str = "UA"
    request_timeout_seconds: float = 20.0
    max_results_per_query: int = 50
    max_pages_per_domain: int = 5
    max_concurrent_requests: int = 4
    request_delay_seconds: float = 0.5
    retry_limit: int = 3
    job_queue_max: int = 200
    listing_freshness_hours: int = 72
    log_level: str = "INFO"

    # Optional credentials — absence must not prevent startup
    brave_search_api_key: str | None = None
    ebay_app_id: str | None = None
    allegro_client_id: str | None = None
    allegro_client_secret: str | None = None
    fx_api_key: str | None = None
    vin_decode_api_key: str | None = None
    # FREE key: register at https://developers.ria.com → Мій профіль → API key
    autoria_api_key: str | None = None
    autoria_min_interval_seconds: float = 2.5


def get_settings() -> Settings:
    return Settings()
