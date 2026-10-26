from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core import __version__
from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.config.countries import QUERY_LANGUAGES, enabled_countries
from autoparts_core.config.settings import get_settings

st.set_page_config(page_title="Settings", layout="wide")
ensure_app_ready()
page_header("Settings", "Configuration · offline mode · version")

settings = get_settings()
st.write(
    {
        "app_version": __version__,
        "demo_mode": settings.demo_mode,
        "database_url": settings.database_url,
        "default_currency": settings.default_currency,
        "destination_country": settings.destination_country,
        "max_results_per_query": settings.max_results_per_query,
        "brave_search_api_key_set": bool(settings.brave_search_api_key),
        "ebay_app_id_set": bool(settings.ebay_app_id),
        "allegro_client_id_set": bool(settings.allegro_client_id),
        "fx_api_key_set": bool(settings.fx_api_key),
        "vin_decode_api_key_set": bool(settings.vin_decode_api_key),
    }
)

st.subheader("Enabled countries")
st.dataframe(
    [
        {
            "iso": c.iso_code,
            "name": c.display_name,
            "currency": c.default_currency,
            "eu": c.eu_member,
            "languages": ",".join(c.languages),
        }
        for c in enabled_countries()
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Query languages")
st.write(", ".join(QUERY_LANGUAGES))

st.info("Optional API keys are read from environment / .env. The app starts without them.")
