from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.db.models import Listing, Seller
from autoparts_core.db.session import get_session

st.set_page_config(page_title="Listings", layout="wide")
ensure_app_ready()
page_header("Listings", "Persistent listings with provenance")

with get_session() as session:
    q = session.query(Listing)
    demo_only = st.checkbox("Demo only", value=False)
    if demo_only:
        q = q.filter_by(is_demo_data=True)
    rows = q.order_by(Listing.id.desc()).limit(200).all()
    data = []
    for L in rows:
        seller = session.get(Seller, L.seller_id) if L.seller_id else None
        data.append(
            {
                "id": L.internal_id,
                "title": L.title,
                "oem": L.oem_as_stated,
                "condition": L.condition,
                "status": L.availability_status,
                "country": L.country,
                "seller": seller.display_name if seller else None,
                "source": L.source_id,
                "demo": L.is_demo_data,
                "url": L.canonical_url,
                "last_checked": L.last_checked.isoformat() if L.last_checked else None,
            }
        )
st.dataframe(data, use_container_width=True, hide_index=True)
