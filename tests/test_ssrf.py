from autoparts_core.security.ssrf import sanitize_export_cell, validate_public_url


def test_block_localhost():
    ok, reason = validate_public_url("http://localhost/admin")
    assert not ok


def test_block_private_ip():
    ok, _ = validate_public_url("http://127.0.0.1/x")
    assert not ok
    ok, _ = validate_public_url("http://192.168.1.1/x")
    assert not ok
    ok, _ = validate_public_url("http://169.254.169.254/latest/meta-data")
    assert not ok


def test_block_file_scheme():
    ok, _ = validate_public_url("file:///etc/passwd")
    assert not ok


def test_allow_public_https():
    ok, reason = validate_public_url("https://example.com/listing/1")
    assert ok, reason


def test_formula_injection():
    assert sanitize_export_cell("=CMD()") == "'=CMD()"
    assert sanitize_export_cell("normal") == "normal"
