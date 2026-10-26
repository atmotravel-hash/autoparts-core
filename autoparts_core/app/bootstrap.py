"""Shared Streamlit bootstrap: DB init, demo seed, session helpers."""

from __future__ import annotations

import streamlit as st

from autoparts_core import __version__
from autoparts_core.config.settings import get_settings
from autoparts_core.connectors.fixture import FixtureConnector
from autoparts_core.db.models import Listing
from autoparts_core.db.session import get_session, init_db
from autoparts_core.services.ingestion import ingest_parsed_listing


def ensure_app_ready() -> None:
    if st.session_state.get("_db_ready"):
        return
    init_db()
    settings = get_settings()
    if settings.demo_mode:
        with get_session() as session:
            if session.query(Listing).filter_by(is_demo_data=True).count() == 0:
                connector = FixtureConnector()
                for row in connector._listings:
                    parsed = connector.parse_listing(row)
                    ingest_parsed_listing(session, "fixture", parsed)
    st.session_state["_db_ready"] = True


def page_header(title: str, subtitle: str | None = None) -> None:
    settings = get_settings()
    cols = st.columns([4, 1])
    with cols[0]:
        st.title(title)
        if subtitle:
            st.caption(subtitle)
    with cols[1]:
        st.caption(f"v{__version__}")
        if settings.demo_mode:
            st.warning("DEMO MODE — fixture data labelled", icon="⚠️")


NAV = [
    ("Dashboard", "app/Home.py"),
    ("Vehicle Search", "pages/1_Vehicle_Search.py"),
    ("OEM Search", "pages/2_OEM_Search.py"),
    ("Part Name Search", "pages/3_Part_Name_Search.py"),
    ("Discovery", "pages/4_Discovery.py"),
    ("Listings", "pages/5_Listings.py"),
    ("Price Comparison", "pages/6_Price_Comparison.py"),
    ("Sellers", "pages/7_Sellers.py"),
    ("Duplicate Review", "pages/8_Duplicate_Review.py"),
    ("Import", "pages/9_Import.py"),
    ("Export", "pages/10_Export.py"),
    ("Source Connectors", "pages/11_Source_Connectors.py"),
    ("Jobs and Logs", "pages/12_Jobs_and_Logs.py"),
    ("Settings", "pages/13_Settings.py"),
]
