from autoparts_core.core.models import VehicleQuery
from autoparts_core.discovery.queries import generate_queries


def test_generate_multilingual():
    qs = generate_queries(
        VehicleQuery(
            make="Volkswagen",
            model="Passat",
            generation="B8",
            year=2017,
            part_name="headlight",
            oem_number="3G1941007A",
        )
    )
    texts = [q["query"] for q in qs]
    assert any("3G1941007A" == t for t in texts)
    assert any("Scheinwerfer" in t for t in texts)
    assert any("фара" in t for t in texts)
