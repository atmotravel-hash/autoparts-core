"""CSV/XLSX/JSON import with preview stats."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from autoparts_core.connectors.base import ParsedListing
from autoparts_core.security.ssrf import validate_public_url
from autoparts_core.services.ingestion import ingest_parsed_listing


REQUIRED_HINTS = ("title", "canonical_url")


def read_tabular(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return pd.DataFrame(data)
        if isinstance(data, dict) and "listings" in data:
            return pd.DataFrame(data["listings"])
        return pd.DataFrame([data])
    return pd.read_csv(path)


def preview_import(df: pd.DataFrame, column_map: dict[str, str] | None = None) -> dict[str, Any]:
    column_map = column_map or {}
    mapped = df.rename(columns=column_map) if column_map else df.copy()
    missing = [c for c in REQUIRED_HINTS if c not in mapped.columns]
    return {
        "rows_read": len(mapped),
        "columns": list(mapped.columns),
        "missing_required_hints": missing,
        "preview": mapped.head(10).fillna("").to_dict(orient="records"),
    }


def import_listings(
    session: Session,
    df: pd.DataFrame,
    *,
    column_map: dict[str, str] | None = None,
    source_id: str = "manual",
) -> dict[str, Any]:
    column_map = column_map or {}
    mapped = df.rename(columns=column_map) if column_map else df
    stats = {
        "rows_read": len(mapped),
        "rows_accepted": 0,
        "rows_inserted": 0,
        "rows_updated": 0,
        "exact_duplicates": 0,
        "rejected_rows": 0,
        "validation_errors": [],
    }
    for idx, row in mapped.iterrows():
        try:
            record = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            url = str(record.get("canonical_url") or record.get("url") or "").strip()
            title = str(record.get("title") or "").strip()
            if not title:
                raise ValueError("title required")
            if url:
                ok, reason = validate_public_url(url)
                if not ok:
                    # Allow fixture-style demo URLs under example.invalid / fixtures
                    if not url.startswith(("https://fixtures.autoparts.local/", "https://example.com/")):
                        raise ValueError(f"URL rejected: {reason}")
            else:
                url = f"https://example.com/import/row-{idx}"
            parsed = ParsedListing(
                source_listing_id=str(record.get("source_listing_id") or url)[:120],
                title=title,
                canonical_url=url,
                original_url=str(record.get("original_url") or url),
                description=record.get("description"),
                oem_as_stated=str(record["oem_as_stated"]) if record.get("oem_as_stated") else None,
                manufacturer_as_stated=str(record["manufacturer_as_stated"])
                if record.get("manufacturer_as_stated")
                else None,
                condition_raw=str(record["condition"]) if record.get("condition") else None,
                condition=str(record.get("condition") or "UNKNOWN"),
                assembly_completeness=str(record.get("assembly_completeness") or "UNKNOWN"),
                price_amount=float(record["price_amount"]) if record.get("price_amount") is not None else None,
                price_currency=str(record["price_currency"]) if record.get("price_currency") else None,
                shipping_amount=float(record["shipping_amount"])
                if record.get("shipping_amount") is not None
                else None,
                shipping_currency=str(record["shipping_currency"]) if record.get("shipping_currency") else None,
                country=str(record["country"]) if record.get("country") else None,
                seller={"display_name": record.get("seller_name"), "country": record.get("country")},
                is_demo_data=bool(record.get("is_demo_data", False)),
                extraction_confidence=0.5,
                availability_status="ACTIVE_UNVERIFIED",
                raw=record,
            )
            listing, created = ingest_parsed_listing(session, source_id, parsed)
            stats["rows_accepted"] += 1
            if created:
                stats["rows_inserted"] += 1
            else:
                stats["rows_updated"] += 1
                stats["exact_duplicates"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["rejected_rows"] += 1
            stats["validation_errors"].append({"row": int(idx) if str(idx).isdigit() else idx, "error": str(exc)})
    return stats
