"""Database engine and session helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from autoparts_core.config.settings import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        settings = get_settings()
        url = settings.database_url
        if url.startswith("sqlite:///"):
            path = Path(url.replace("sqlite:///", "", 1))
            path.parent.mkdir(parents=True, exist_ok=True)
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, future=True, connect_args=connect_args)
        if url.startswith("sqlite"):

            @event.listens_for(_engine, "connect")
            def _fk_on(dbapi_conn, _):  # type: ignore[no-untyped-def]
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def init_db() -> None:
    from autoparts_core.db import models  # noqa: F401
    from autoparts_core.db.base import Base

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    _seed_reference_data()


def _seed_reference_data() -> None:
    from autoparts_core.config.countries import COUNTRY_REGISTRY
    from autoparts_core.db.models import CountryRecord, Marketplace

    with get_session() as session:
        if session.query(CountryRecord).count() == 0:
            for c in COUNTRY_REGISTRY.values():
                session.add(
                    CountryRecord(
                        iso_code=c.iso_code,
                        display_name=c.display_name,
                        default_currency=c.default_currency,
                        languages=",".join(c.languages),
                        enabled_sources=",".join(c.enabled_sources),
                        delivery_region=c.delivery_region,
                        eu_member=c.eu_member,
                        tax_import_notes=c.tax_import_notes,
                        enabled=c.enabled,
                    )
                )
        if session.query(Marketplace).filter_by(source_id="fixture").count() == 0:
            session.add(
                Marketplace(
                    source_id="fixture",
                    name="Offline Fixture Source",
                    access_method="FIXTURE",
                    health_status="healthy",
                    operational=True,
                    terms_notes="Clearly labelled demo data — never presented as live",
                )
            )
        if session.query(Marketplace).filter_by(source_id="manual").count() == 0:
            session.add(
                Marketplace(
                    source_id="manual",
                    name="Manual URL Import",
                    access_method="MANUAL_IMPORT",
                    health_status="healthy",
                    operational=True,
                    terms_notes="User-supplied URLs only; SSRF protections apply",
                )
            )
        live_markets = [
            ("nine99_md", "999.md Moldova", "PUBLIC_PAGE", "MD", "GraphQL POST /graphql — tested"),
            ("olx_ua", "OLX Ukraine", "PUBLIC_PAGE", "UA", "GraphQL POST /apigateway/graphql — tested"),
            ("olx_ro", "OLX Romania", "PUBLIC_PAGE", "RO", "GraphQL POST /apigateway/graphql — tested"),
            ("prom_ua", "Prom.ua", "PUBLIC_PAGE", "UA", "Product JSON-LD on public search HTML"),
            ("flagma_ua", "Flagma.ua", "PUBLIC_PAGE", "UA", "Product JSON-LD on public search HTML"),
            ("prom_md", "Prom.md", "PUBLIC_PAGE", "MD", "Product JSON-LD on public search HTML"),
            (
                "auto_ria",
                "AUTO.RIA",
                "OFFICIAL_API",
                "UA",
                "developers.ria.com — needs AUTORIA_API_KEY; attribution https://auto.ria.com",
            ),
        ]
        for sid, name, access, countries, notes in live_markets:
            if session.query(Marketplace).filter_by(source_id=sid).count() == 0:
                session.add(
                    Marketplace(
                        source_id=sid,
                        name=name,
                        access_method=access,
                        health_status="healthy",
                        operational=True,
                        supported_countries=countries,
                        terms_notes=notes,
                    )
                )
        session.commit()


@contextmanager
def get_session() -> Iterator[Session]:
    get_engine()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
