from autoparts_core.identity.oem import normalize_oem, preserve_raw, superficially_similar


def test_preserve_leading_zeros_and_suffix():
    assert preserve_raw(" 03G1941007A ") == "03G1941007A"
    assert normalize_oem("3G1 941 007 A") == "3G1941007A"
    assert normalize_oem("3G1941007A") == "3G1941007A"


def test_similar_not_proof():
    assert superficially_similar("3G1941007A", "3G1941007B")
    # caller must not treat this as equivalence — function only detects similarity
