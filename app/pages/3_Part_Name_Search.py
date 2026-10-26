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
from autoparts_core.identity.taxonomy import map_part_name
from autoparts_core.services.search import run_search

st.set_page_config(page_title="Part Name Search", layout="wide")
ensure_app_ready()
page_header("Part Name Search", "Multilingual aliases → canonical concepts")

examples = [
    "left front fender",
    "left front wing",
    "крыло переднее левое",
    "крило переднє ліве",
    "aripă față stânga",
    "błotnik przedni lewy",
    "Kotflügel vorne links",
    "фара левая",
]
name = st.text_input("Part name", value="фара ліва")
st.caption("Examples: " + " · ".join(examples[:4]) + " …")

mapped = map_part_name(name)
st.json(mapped)

if st.button("Search", type="primary"):
    with get_session() as session:
        from autoparts_core.services.search import resolve_default_sources

        res = run_search(
            session,
            VehicleQuery(part_name=name, make="Volkswagen", model="Passat", generation="B8", year=2017),
            source_ids=resolve_default_sources(),
        )
    st.write(f"{len(res['results'])} results")
    for r in res["results"]:
        st.write(f"- {r.title} · fitment={r.fitment.status.value if r.fitment else '—'} · demo={r.is_demo_data}")
