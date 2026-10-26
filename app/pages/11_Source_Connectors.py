from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.connectors.registry import get_registry, list_connectors, load_source_catalog

st.set_page_config(page_title="Source Connectors", layout="wide")
ensure_app_ready()
page_header("Source Connectors", "GraphQL catalogs + candidates — never mark operational without a test")

st.subheader("Registered connectors")
for row in list_connectors():
    with st.container(border=True):
        st.markdown(f"### {row['source_name']} (`{row['source_id']}`)")
        c1, c2, c3 = st.columns(3)
        c1.write(f"Operational: **{row['operational']}**")
        c2.write(f"Health: **{row['health_status']}**")
        c3.write(f"Access: {row['access_method']}")
        st.caption(row["terms_notes"])
        st.write(
            {
                "countries": row["supported_countries"],
                "languages": row["supported_languages"],
                "modes": row["supported_search_modes"],
                "auth_required": row["authentication_required"],
                "last_successful_test": row["last_successful_test"],
            }
        )
        if st.button("Run health check", key=f"hc_{row['source_id']}"):
            connector = get_registry()[row["source_id"]]
            st.json(connector.health_check())

st.subheader("Full source catalog (config/sources.yaml)")
st.dataframe(load_source_catalog(), use_container_width=True, hide_index=True)

st.info(
    "AUTODOC / Ovoko / Allegro HTML GraphQL probes hit Cloudflare/CAPTCHA — "
    "we do **not** bypass challenges. Use official APIs when credentials are available."
)
