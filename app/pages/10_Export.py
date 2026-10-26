from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.db.session import get_session
from autoparts_core.io.exporters import export_csvs, export_xlsx

st.set_page_config(page_title="Export", layout="wide")
ensure_app_ready()
page_header("Export", "CSV + Excel workbook · no credentials · formula-injection safe")

out = ROOT / "exports"
if st.button("Export CSV set", type="primary"):
    with get_session() as session:
        summary = export_csvs(session, out / "csv")
    st.json(summary)
    st.caption(f"Written under {out / 'csv'}")

if st.button("Export Excel workbook"):
    path = out / "autoparts_export.xlsx"
    with get_session() as session:
        summary = export_xlsx(session, path)
    st.json(summary)
    if path.exists():
        st.download_button(
            "Download workbook",
            data=path.read_bytes(),
            file_name="autoparts_export.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
