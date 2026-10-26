"""CSV and XLSX export with formula-injection protection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import Workbook
from sqlalchemy.orm import Session

from autoparts_core.db.models import (
    DuplicateCandidate,
    FitmentRecord,
    Listing,
    MergeHistory,
    PriceObservation,
    Seller,
)
from autoparts_core.security.ssrf import sanitize_export_cell


def _safe_df(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame()
    cleaned = [{k: sanitize_export_cell(v) for k, v in row.items()} for row in rows]
    return pd.DataFrame(cleaned)


def collect_export_bundles(session: Session) -> dict[str, pd.DataFrame]:
    listings = session.query(Listing).all()
    listing_rows = []
    for L in listings:
        listing_rows.append(
            {
                "internal_id": L.internal_id,
                "source_id": L.source_id,
                "source_listing_id": L.source_listing_id,
                "title": L.title,
                "oem_as_stated": L.oem_as_stated,
                "manufacturer_as_stated": L.manufacturer_as_stated,
                "condition": L.condition,
                "assembly_completeness": L.assembly_completeness,
                "country": L.country,
                "availability_status": L.availability_status,
                "canonical_url": L.canonical_url,
                "first_discovered": L.first_discovered.isoformat() if L.first_discovered else None,
                "last_checked": L.last_checked.isoformat() if L.last_checked else None,
                "is_demo_data": L.is_demo_data,
                "seller_id": L.seller_id,
            }
        )

    sellers = session.query(Seller).all()
    seller_rows = [
        {
            "internal_id": s.internal_id,
            "display_name": s.display_name,
            "business_name": s.business_name,
            "public_phone": s.public_phone,
            "public_email": s.public_email,
            "public_website": s.public_website,
            "country": s.country,
            "seller_type": s.seller_type,
            "rating": s.rating,
            "review_count": s.review_count,
        }
        for s in sellers
    ]

    prices = session.query(PriceObservation).all()
    price_rows = [
        {
            "listing_id": p.listing_id,
            "amount": p.amount,
            "currency": p.currency,
            "shipping_amount": p.shipping_amount,
            "shipping_currency": p.shipping_currency,
            "converted_amount": p.converted_amount,
            "converted_currency": p.converted_currency,
            "estimated_landed": p.estimated_landed,
            "fx_rate": p.fx_rate,
            "fx_provider": p.fx_provider,
            "fx_timestamp": p.fx_timestamp.isoformat() if p.fx_timestamp else None,
            "warnings": p.warnings,
            "observed_at": p.observed_at.isoformat() if p.observed_at else None,
        }
        for p in prices
    ]

    fitments = session.query(FitmentRecord).all()
    fit_rows = [
        {
            "listing_id": f.listing_id,
            "status": f.status,
            "confidence": f.confidence,
            "evidence_kind": f.evidence_kind,
            "evidence_source": f.evidence_source,
            "evidence_detail": f.evidence_detail,
            "explanation": f.explanation,
            "provenance": f.provenance,
            "verification_timestamp": f.verification_timestamp.isoformat()
            if f.verification_timestamp
            else None,
        }
        for f in fitments
    ]

    dups = session.query(DuplicateCandidate).all()
    dup_rows = [
        {
            "left_listing_id": d.left_listing_id,
            "right_listing_id": d.right_listing_id,
            "outcome": d.outcome,
            "match_score": d.match_score,
            "match_reasons": d.match_reasons,
            "review_status": d.review_status,
        }
        for d in dups
    ]

    merges = session.query(MergeHistory).all()
    merge_rows = [
        {
            "entity_type": m.entity_type,
            "survivor_id": m.survivor_id,
            "merged_id": m.merged_id,
            "reversed": m.reversed,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in merges
    ]

    summary = {
        "listings": len(listing_rows),
        "sellers": len(seller_rows),
        "price_observations": len(price_rows),
        "fitment_records": len(fit_rows),
        "duplicate_candidates": len(dup_rows),
        "demo_listings": sum(1 for r in listing_rows if r["is_demo_data"]),
    }

    return {
        "summary": pd.DataFrame([summary]),
        "listings": _safe_df(listing_rows),
        "sellers": _safe_df(seller_rows),
        "price_history": _safe_df(price_rows),
        "fitment": _safe_df(fit_rows),
        "possible_duplicates": _safe_df(dup_rows),
        "merge_audit": _safe_df(merge_rows),
    }


def export_csvs(session: Session, out_dir: str | Path) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bundles = collect_export_bundles(session)
    written = {}
    mapping = {
        "listings": "listings.csv",
        "sellers": "sellers.csv",
        "price_history": "price_history.csv",
        "fitment": "fitment_results.csv",
        "possible_duplicates": "duplicate_candidates.csv",
    }
    for key, filename in mapping.items():
        path = out_dir / filename
        bundles[key].to_csv(path, index=False)
        written[filename] = len(bundles[key])
    # parts stub from listings OEM
    parts_df = bundles["listings"][["oem_as_stated", "title"]].drop_duplicates() if len(bundles["listings"]) else pd.DataFrame()
    parts_path = out_dir / "parts.csv"
    parts_df.to_csv(parts_path, index=False)
    written["parts.csv"] = len(parts_df)
    summary = bundles["summary"].to_dict(orient="records")[0]
    summary["files"] = written
    summary["reconcile_ok"] = summary["listings"] == written.get("listings.csv", -1)
    return summary


def export_xlsx(session: Session, path: str | Path) -> dict[str, Any]:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    bundles = collect_export_bundles(session)
    wb = Workbook()
    # remove default
    default = wb.active
    wb.remove(default)

    sheet_map = [
        ("Summary", bundles["summary"]),
        ("Listings", bundles["listings"]),
        ("Parts", bundles["listings"][["oem_as_stated", "manufacturer_as_stated", "title"]].drop_duplicates()
         if len(bundles["listings"])
         else pd.DataFrame()),
        ("Sellers", bundles["sellers"]),
        ("Price_Comparison", bundles["price_history"]),
        ("Price_History", bundles["price_history"]),
        ("Fitment", bundles["fitment"]),
        ("Possible_Duplicates", bundles["possible_duplicates"]),
        ("Merge_Audit", bundles["merge_audit"]),
        ("Sources", pd.DataFrame([{"note": "See Source Connectors page / marketplaces table"}])),
        ("Errors", pd.DataFrame(columns=["category", "message"])),
        ("Run_Summary", bundles["summary"]),
    ]
    counts = {}
    for name, df in sheet_map:
        ws = wb.create_sheet(name)
        if df is None or df.empty:
            ws.append(["(empty)"])
            counts[name] = 0
            continue
        ws.append([sanitize_export_cell(c) for c in list(df.columns)])
        for row in df.itertuples(index=False):
            ws.append([sanitize_export_cell(v) for v in row])
        counts[name] = len(df)

    wb.save(path)
    summary = bundles["summary"].to_dict(orient="records")[0]
    summary["xlsx"] = str(path)
    summary["sheet_counts"] = counts
    summary["reconcile_ok"] = summary["listings"] == counts.get("Listings", -1)
    return summary
