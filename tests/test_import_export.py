import json
from pathlib import Path

from autoparts_core.db.session import get_session, init_db
from autoparts_core.io.exporters import export_csvs, export_xlsx
from autoparts_core.io.importers import import_listings, read_tabular
import pandas as pd


def test_import_and_export(tmp_path, monkeypatch):
    db = tmp_path / "t.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    # reset engine
    import autoparts_core.db.session as sess

    sess._engine = None
    sess._SessionLocal = None
    from autoparts_core.config.settings import Settings

    monkeypatch.setattr("autoparts_core.db.session.get_settings", lambda: Settings(database_url=f"sqlite:///{db}"))
    init_db()
    df = pd.DataFrame(
        [
            {
                "title": "Test headlight",
                "canonical_url": "https://example.com/listing/99",
                "oem_as_stated": "3G1941007A",
                "price_amount": 10,
                "price_currency": "EUR",
                "country": "DE",
                "seller_name": "TestSeller",
            }
        ]
    )
    with get_session() as session:
        stats = import_listings(session, df)
        assert stats["rows_inserted"] == 1
        out = tmp_path / "out"
        summary = export_csvs(session, out)
        assert summary["reconcile_ok"]
        xlsx = tmp_path / "out.xlsx"
        xsum = export_xlsx(session, xlsx)
        assert xsum["reconcile_ok"]
        assert xlsx.exists()


def test_read_fixture_json():
    path = Path(__file__).parent / "fixtures" / "listings.json"
    data = json.loads(path.read_text())
    assert len(data) >= 5
