from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.db.models import Seller
from autoparts_core.db.session import get_session

st.set_page_config(page_title="Sellers", layout="wide")
ensure_app_ready()
page_header("Sellers", "Public business contacts only — evidence-linked")

with get_session() as session:
    sellers = session.query(Seller).order_by(Seller.rating.desc()).all()
    st.dataframe(
        [
            {
                "name": s.display_name,
                "country": s.country,
                "type": s.seller_type,
                "rating": s.rating,
                "reviews": s.review_count,
                "phone": s.public_phone,
                "website": s.public_website,
                "evidence": s.evidence_source,
            }
            for s in sellers
        ],
        use_container_width=True,
        hide_index=True,
    )
