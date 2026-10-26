"""Workflow A — Search by vehicle and part."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from autoparts_core.app.bootstrap import ensure_app_ready, page_header
from autoparts_core.config.countries import enabled_countries
from autoparts_core.core.enums import Condition
from autoparts_core.core.models import VehicleQuery
from autoparts_core.db.session import get_session
from autoparts_core.services.search import run_search

st.set_page_config(page_title="Vehicle Search", layout="wide")
ensure_app_ready()
page_header("Vehicle Search", "Vehicle + Part · OEM · Part Name · VIN (optional)")

tabs = st.tabs(["Vehicle + Part", "Help"])
countries = enabled_countries()
country_labels = {c.iso_code: f"{c.display_name} ({c.iso_code})" for c in countries}

with tabs[0]:
    with st.form("vehicle_search"):
        r1 = st.columns(5)
        make = r1[0].selectbox("Make", ["Volkswagen", "BMW", "Audi", "Skoda", "Toyota"], index=0)
        model = r1[1].selectbox("Model", ["Passat", "Golf", "3 Series", "A4", "Octavia"], index=0)
        generation = r1[2].selectbox("Generation", ["B8 (2014–2023)", "B7", "Mk7", "F30", "B9"], index=0)
        year = r1[3].selectbox("Year", list(range(2024, 2009, -1)), index=7)
        part = r1[4].selectbox("Part", ["Headlight", "Front fender", "Bumper", "Side mirror"], index=0)

        r2 = st.columns(4)
        oem = r2[0].text_input("OEM number (optional)", value="3G1941007A")
        condition = r2[1].selectbox("Condition", ["Any"] + [c.value for c in Condition], index=0)
        preferred = r2[2].multiselect(
            "Countries",
            options=list(country_labels.keys()),
            default=["DE", "PL", "LT", "UA", "MD"],
            format_func=lambda x: country_labels[x],
        )
        destination = r2[3].selectbox(
            "Destination",
            options=list(country_labels.keys()),
            index=list(country_labels.keys()).index("UA"),
            format_func=lambda x: country_labels[x],
        )

        r3 = st.columns(3)
        currency = r3[0].selectbox("Currency", ["EUR", "USD", "UAH", "MDL", "PLN"], index=0)
        vin = r3[1].text_input("VIN (optional — not used as fitment proof)", value="")
        budget = r3[2].number_input("Budget (optional)", min_value=0.0, value=0.0, step=10.0)

        submitted = st.form_submit_button("Search", type="primary", use_container_width=False)

    left, right = st.columns([2.4, 1])

    if submitted:
        gen = generation.split()[0]
        vq = VehicleQuery(
            make=make,
            model=model,
            generation=gen,
            year=int(year),
            part_name=part,
            oem_number=oem or None,
            condition=None if condition == "Any" else Condition(condition),
            preferred_countries=preferred,
            destination_country=destination,
            currency=currency,
            vin=vin or None,
            budget=budget or None,
        )
        with get_session() as session:
            result = run_search(session, vq, source_ids=["fixture"])
            st.session_state["last_search"] = result
            st.session_state["last_vehicle"] = vq.model_dump()

    result = st.session_state.get("last_search")
    with left:
        if not result:
            st.info("Submit a search to load ranked offers. Fixture/demo results are clearly labelled.")
        else:
            if result.get("demo_data_present"):
                st.warning("Results include **DEMO / fixture** listings — not live market availability.")
            st.markdown(f"### Results ({len(result['results'])} offers)")
            st.caption(f"Query: `{result['query']}` · Found hits: {result['found_hits']}")
            for view in result["results"]:
                with st.container(border=True):
                    cA, cB, cC = st.columns([3, 2, 2])
                    with cA:
                        badge = " · DEMO" if view.is_demo_data else ""
                        st.markdown(f"**{view.title}**{badge}")
                        st.caption(
                            f"OEM: {view.oem_as_stated or '—'} · "
                            f"{view.condition} · {view.completeness} · {view.source_id}"
                        )
                        if view.canonical_url:
                            st.markdown(f"[Source]({view.canonical_url})")
                    with cB:
                        st.markdown(f"**{view.seller_name or '—'}**")
                        st.caption(
                            f"{view.seller_country or '—'} · rating {view.seller_rating or '—'} · "
                            f"{view.seller_phone or ''}"
                        )
                        if view.price:
                            item = view.price.item_original
                            landed = view.price.estimated_landed
                            ship = view.price.shipping_original
                            item_s = f"{item.currency} {item.amount}" if item and item.amount is not None else "—"
                            ship_s = (
                                f"{ship.currency} {ship.amount}"
                                if ship and ship.amount is not None
                                else "shipping unknown"
                            )
                            landed_s = (
                                f"{landed.currency} {landed.amount:.2f}"
                                if landed and landed.amount is not None
                                else "landed unknown"
                            )
                            st.write(f"{item_s} + {ship_s} → **{landed_s}**")
                            st.caption(f"Delivery: {view.price.delivery_eligibility.value}")
                            for w in view.price.warnings[:2]:
                                st.caption(f"⚠ {w}")
                    with cC:
                        if view.fitment:
                            st.markdown(f"`{view.fitment.status.value}` ({view.fitment.confidence:.0%})")
                            st.caption(f"Evidence: {view.fitment.evidence_kind.value}")
                            st.caption(view.fitment.explanation[:160])
                        st.caption(f"Freshness: {view.last_checked or '—'} · {view.status}")

            if result.get("errors"):
                with st.expander("Source errors"):
                    st.json(result["errors"])

    with right:
        st.markdown("### Search summary")
        v = st.session_state.get("last_vehicle") or {}
        st.write(
            {
                "vehicle": f"{v.get('make', '—')} {v.get('model', '—')} {v.get('generation', '')} {v.get('year', '')}",
                "part": v.get("part_name"),
                "oem": v.get("oem_number"),
                "destination": v.get("destination_country"),
                "currency": v.get("currency"),
                "data": "Live fixture demo" if result and result.get("demo_data_present") else "—",
            }
        )
        if result:
            st.metric("Offers shown", len(result["results"]))
            st.metric("Discovery hits", result["found_hits"])
        st.markdown("### Quick filters (display)")
        only_verified = st.checkbox("Hide INCOMPATIBLE")
        if only_verified and result:
            filtered = [
                x
                for x in result["results"]
                if not x.fitment or x.fitment.status.value != "INCOMPATIBLE"
            ]
            st.caption(f"{len(filtered)} after filter (re-render list by re-running search for full UX)")

with tabs[1]:
    st.markdown(
        """
- VIN decode is optional and **never** proof of part compatibility.
- Fitment statuses require evidence; title-only stays UNCONFIRMED.
- Unknown shipping/taxes are **not** treated as zero.
- Fixture listings are demo data only.
"""
    )
