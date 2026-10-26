from autoparts_core.connectors.fixture import FixtureConnector
from autoparts_core.connectors.registry import list_connectors
from autoparts_core.core.models import VehicleQuery
from autoparts_core.db.session import get_session, init_db
from autoparts_core.services.search import run_search


def test_fixture_operational():
    c = FixtureConnector()
    caps = c.get_capabilities()
    assert caps.operational
    assert caps.health_status == "healthy"
    hits = c.search("Passat headlight")
    assert hits
    doc = c.fetch_listing(str(hits[0].url))
    parsed = c.parse_listing(doc)
    assert parsed.is_demo_data


def test_hassle_sources_not_in_active_registry():
    rows = {r["source_id"]: r for r in list_connectors()}
    for sid in ("ebay", "allegro", "autodoc", "ovoko", "auto_ria", "brave_search"):
        assert sid not in rows


def test_search_persists(tmp_path, monkeypatch):
    db = tmp_path / "s.db"
    import autoparts_core.db.session as sess

    sess._engine = None
    sess._SessionLocal = None
    from autoparts_core.config.settings import Settings

    monkeypatch.setattr("autoparts_core.db.session.get_settings", lambda: Settings(database_url=f"sqlite:///{db}"))
    init_db()
    with get_session() as session:
        res = run_search(
            session,
            VehicleQuery(
                make="Volkswagen",
                model="Passat",
                generation="B8",
                year=2017,
                part_name="headlight",
                oem_number="3G1941007A",
                currency="EUR",
            ),
            source_ids=["fixture"],
        )
        assert res["results"]
        assert res["demo_data_present"]
        assert any(r.fitment and r.fitment.status.value == "VERIFIED_EXACT" for r in res["results"])
