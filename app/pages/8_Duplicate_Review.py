from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.db.models import DuplicateCandidate, Listing, PriceObservation, Seller
from autoparts_core.db.session import get_session
from autoparts_core.dedupe.engine import ListingFingerprint, find_duplicates

st.set_page_config(page_title="Duplicate Review", layout="wide")
ensure_app_ready()
page_header("Duplicate Review", "Never auto-merge uncertain matches · merges reversible")

if st.button("Scan for duplicates", type="primary"):
    with get_session() as session:
        listings = session.query(Listing).all()
        fps = []
        for L in listings:
            seller = session.get(Seller, L.seller_id) if L.seller_id else None
            price = (
                session.query(PriceObservation)
                .filter_by(listing_id=L.id)
                .order_by(PriceObservation.observed_at.desc())
                .first()
            )
            fps.append(
                ListingFingerprint(
                    id=L.id,
                    source_id=L.source_id,
                    source_listing_id=L.source_listing_id,
                    canonical_url=L.canonical_url,
                    seller_id=L.seller_id,
                    seller_name=seller.display_name if seller else None,
                    oem=L.oem_as_stated,
                    title=L.title,
                    price=price.amount if price else None,
                    currency=price.currency if price else None,
                    country=L.country,
                )
            )
        matches = find_duplicates(fps)
        # clear prior auto scan pending? keep history — insert new
        inserted = 0
        for m in matches:
            exists = (
                session.query(DuplicateCandidate)
                .filter_by(left_listing_id=m.left_id, right_listing_id=m.right_id)
                .first()
            )
            if exists:
                continue
            session.add(
                DuplicateCandidate(
                    left_listing_id=m.left_id,
                    right_listing_id=m.right_id,
                    outcome=m.outcome.value,
                    match_score=m.score,
                    match_reasons=",".join(m.reasons),
                    evidence=m.evidence,
                    algorithm_version=m.algorithm_version,
                    review_status="pending",
                )
            )
            inserted += 1
        st.success(f"Scan complete — {len(matches)} signals, {inserted} new candidates stored")

with get_session() as session:
    cands = session.query(DuplicateCandidate).order_by(DuplicateCandidate.match_score.desc()).all()
    st.metric("Pending review", sum(1 for c in cands if c.review_status == "pending"))
    for c in cands:
        left = session.get(Listing, c.left_listing_id)
        right = session.get(Listing, c.right_listing_id)
        with st.container(border=True):
            cols = st.columns([3, 3, 2])
            cols[0].write(left.title if left else c.left_listing_id)
            cols[0].caption(left.canonical_url if left else "")
            cols[1].write(right.title if right else c.right_listing_id)
            cols[1].caption(right.canonical_url if right else "")
            cols[2].markdown(f"`{c.outcome}` · score {c.match_score:.2f}")
            cols[2].caption(c.match_reasons)
            a1, a2, a3 = st.columns(3)
            if a1.button("Accept match", key=f"acc_{c.id}"):
                c.review_status = "accepted"
                c.reviewer_action = "accept"
                session.commit()
                st.rerun()
            if a2.button("Reject", key=f"rej_{c.id}"):
                c.review_status = "rejected"
                c.reviewer_action = "reject"
                session.commit()
                st.rerun()
            a3.caption(f"status={c.review_status}")
