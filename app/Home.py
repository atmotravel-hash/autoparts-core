"""AutoParts Intelligence — Dashboard entry point."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.connectors.registry import list_connectors
from autoparts_core.db.models import DuplicateCandidate, Listing, Seller
from autoparts_core.db.session import get_session

st.set_page_config(
    page_title="AutoParts Intelligence",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_app_ready()
page_header("AutoParts Intelligence", "Find. Compare. Buy. — Europe · Moldova · Ukraine")

st.sidebar.markdown("### Navigation")
st.sidebar.caption("John Doe — Pro Plan (local MVP)")
st.sidebar.info(
    "Live GraphQL catalogs enabled: **OLX UA/PL/RO** + **999.md**. "
    "AUTODOC/Ovoko/Allegro remain blocked or credential-gated — no CAPTCHA bypass. "
    "Fixture rows stay labelled as demo."
)

with get_session() as session:
    listings = session.query(Listing).count()
    demo = session.query(Listing).filter_by(is_demo_data=True).count()
    sellers = session.query(Seller).count()
    dups = session.query(DuplicateCandidate).filter_by(review_status="pending").count()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Listings", listings)
c2.metric("Demo listings", demo)
c3.metric("Sellers", sellers)
c4.metric("Duplicates pending", dups)

st.subheader("Connector health")
rows = list_connectors()
st.dataframe(
    [
        {
            "source": r["source_id"],
            "name": r["source_name"],
            "operational": r["operational"],
            "health": r["health_status"],
            "access": r["access_method"],
        }
        for r in rows
    ],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Start here")
st.markdown(
    """
1. Open **Vehicle Search** and run the Passat B8 headlight demo query.
2. Review fitment evidence labels — title-only never becomes VERIFIED_EXACT.
3. Use **Import** / **Export** for CSV/XLSX workflows.
4. Check **Source Connectors** for which integrations remain untested.
"""
)
