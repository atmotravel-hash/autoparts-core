from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.connectors.registry import (
    get_registry,
    list_connectors,
    load_deferred_sources,
    load_source_catalog,
)

st.set_page_config(page_title="Source Connectors", layout="wide")
ensure_app_ready()
page_header("Source Connectors", "Только рабочие источники без ключей и CAPTCHA")

st.subheader("Активные (в поиске)")
for row in list_connectors():
    with st.container(border=True):
        st.markdown(f"**{row['source_name']}** (`{row['source_id']}`)")
        c1, c2, c3 = st.columns(3)
        c1.write(f"Operational: **{row['operational']}**")
        c2.write(f"Health: **{row['health_status']}**")
        c3.write(row["access_method"])
        if st.button("Health check", key=f"hc_{row['source_id']}"):
            st.json(get_registry()[row["source_id"]].health_check())

st.subheader("Каталог активных")
st.dataframe(load_source_catalog(), use_container_width=True, hide_index=True)

st.subheader("Отсеяно (гемор — не в MVP)")
st.caption("Ключи, OAuth, Cloudflare, партнёрки, низкие лимиты — код/идеи отложены.")
st.dataframe(load_deferred_sources(), use_container_width=True, hide_index=True)
