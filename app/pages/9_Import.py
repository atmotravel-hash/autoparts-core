from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.db.session import get_session
from autoparts_core.io.importers import import_listings, preview_import, read_tabular

st.set_page_config(page_title="Import", layout="wide")
ensure_app_ready()
page_header("Import", "CSV / XLSX / JSON with column mapping preview")

uploaded = st.file_uploader("Upload file", type=["csv", "xlsx", "json"])
if uploaded:
    suffix = Path(uploaded.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getvalue())
        path = tmp.name
    df = read_tabular(path)
    st.write("Detected columns:", list(df.columns))
    preview = preview_import(df)
    st.json({k: preview[k] for k in ("rows_read", "missing_required_hints")})
    st.dataframe(preview["preview"], use_container_width=True)
    if st.button("Import into database", type="primary"):
        with get_session() as session:
            stats = import_listings(session, df, source_id="manual")
        st.success(stats)
else:
    st.caption("Provide title + canonical_url columns at minimum. Private IPs / localhost URLs are rejected.")
