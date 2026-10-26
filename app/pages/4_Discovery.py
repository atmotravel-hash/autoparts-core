from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.core.models import VehicleQuery
from autoparts_core.discovery.queries import generate_queries

st.set_page_config(page_title="Discovery", layout="wide")
ensure_app_ready()
page_header("Discovery", "Query generation only — results are candidate URLs, not confirmed listings")

st.info("Brave Search / live discovery providers are **not configured**. This page shows generated queries only.")

make = st.text_input("Make", "Volkswagen")
model = st.text_input("Model", "Passat")
generation = st.text_input("Generation", "B8")
year = st.number_input("Year", value=2017)
part = st.text_input("Part", "headlight")
oem = st.text_input("OEM", "3G1941007A")

if st.button("Generate queries"):
    qs = generate_queries(
        VehicleQuery(make=make, model=model, generation=generation, year=int(year), part_name=part, oem_number=oem)
    )
    st.dataframe(qs, use_container_width=True)
    st.caption("Controls for crawl depth / concurrency are reserved for when an authorized search provider is wired.")
