from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.db.models import Listing, PriceObservation
from autoparts_core.db.session import get_session
from autoparts_core.pricing.landed import build_price_breakdown

st.set_page_config(page_title="Price Comparison", layout="wide")
ensure_app_ready()
page_header("Price Comparison", "Item · shipping · unknowns · estimated landed")

currency = st.selectbox("Compare in", ["EUR", "USD", "UAH", "MDL", "PLN"], index=0)
mode = st.radio(
    "Mode",
    ["Item price only", "Item + known shipping", "Estimated landed cost"],
    horizontal=True,
)

rows = []
with get_session() as session:
    listings = session.query(Listing).limit(100).all()
    for L in listings:
        price = (
            session.query(PriceObservation)
            .filter_by(listing_id=L.id)
            .order_by(PriceObservation.observed_at.desc())
            .first()
        )
        if not price:
            continue
        br = build_price_breakdown(
            item_amount=price.amount,
            item_currency=price.currency,
            shipping_amount=price.shipping_amount,
            shipping_currency=price.shipping_currency,
            target_currency=currency,
            delivery_eligibility=price.destination_eligibility,
        )
        display = None
        if mode == "Item price only" and br.item_converted:
            display = br.item_converted.amount
        elif mode == "Item + known shipping":
            if br.item_converted and br.shipping_converted:
                display = br.item_converted.amount + br.shipping_converted.amount
            elif br.item_converted:
                display = br.item_converted.amount
        else:
            display = br.estimated_landed.amount if br.estimated_landed else None
        rows.append(
            {
                "title": L.title,
                "country": L.country,
                "original": f"{price.currency} {price.amount}",
                "compare_value": float(display) if display is not None else None,
                "delivery": br.delivery_eligibility.value,
                "unknowns": ", ".join(br.unknown_cost_components) or "—",
                "warnings": "; ".join(br.warnings[:2]),
                "demo": L.is_demo_data,
                "fx_provider": br.fx_provider,
            }
        )

rows = sorted(rows, key=lambda r: (r["compare_value"] is None, r["compare_value"] or 0))
st.dataframe(rows, use_container_width=True, hide_index=True)
st.caption("Lowest compare_value among known costs is not labelled 'best' when unknowns remain.")
