from autoparts_core.identity.taxonomy import detect_side, map_part_name


def test_multilingual_fender():
    for name in [
        "left front fender",
        "крыло переднее левое",
        "крило переднє ліве",
        "aripă față stânga",
        "Kotflügel vorne links",
    ]:
        m = map_part_name(name)
        assert m["matched"]
        assert m["concept_id"] == "front_fender"
        assert m["side"] == "left"


def test_headlight_uk():
    m = map_part_name("фара ліва")
    assert m["concept_id"] == "headlight"
    assert detect_side("фара ліва") == "left"
