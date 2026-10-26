from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.core.models import VehicleQuery
from autoparts_core.db.session import get_session
from autoparts_core.identity.oem import normalize_oem, preserve_raw
from autoparts_core.services.search import run_search

st.set_page_config(page_title="OEM Search", layout="wide")
ensure_app_ready()
page_header("OEM Search", "Exact identifier search — similar numbers are not interchangeable")

raw = st.text_area("OEM / manufacturer numbers (one per line)", value="3G1941007A\n3G1941008A")
make = st.text_input("Make context (optional)", "Volkswagen")
model = st.text_input("Model context (optional)", "Passat")
generation = st.text_input("Generation (optional)", "B8")
year = st.number_input("Year (optional)", min_value=0, value=2017)

if st.button("Search OEM", type="primary"):
    ids = [preserve_raw(x) for x in raw.splitlines() if preserve_raw(x)]
    all_results = []
    with get_session() as session:
        for oem in ids:
            st.write(f"**Raw:** `{oem}` → **Normalized lookup:** `{normalize_oem(oem)}`")
            vq = VehicleQuery(
                make=make or None,
                model=model or None,
                generation=generation or None,
                year=int(year) or None,
                oem_number=oem,
                currency="EUR",
            )
            res = run_search(session, vq, source_ids=["fixture"])
            all_results.extend(res["results"])
            for r in res["results"]:
                fit = r.fitment.status.value if r.fitment else "—"
                ev = r.fitment.evidence_kind.value if r.fitment else "—"
                st.write(f"- {r.title} · {fit} · evidence={ev} · demo={r.is_demo_data}")
    st.success(f"{len(all_results)} offers (may include repeats across IDs)")
