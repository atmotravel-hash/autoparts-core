# Changelog

## 0.2.0 — 2026-10-26 (Europe/Chisinau)

### GraphQL catalog collection
- Generic GraphQL POST client with SSRF checks, rate limits, CAPTCHA refusal.
- **Live connectors (tested):** `nine99_md`, `olx_ua`, `olx_pl`, `olx_ro`.
- Source catalog `autoparts_core/config/sources.yaml` listing thematic candidates and honest statuses.
- Vehicle Search source multiselect defaults to live GraphQL catalogs.
- Docs: `docs/GRAPHQL_SOURCES.md`.
- Tests: unit + opt-in `RUN_LIVE_GRAPHQL=1 pytest -m live`.

### Not done / blocked (honest)
- AUTODOC, Ovoko, Allegro HTML GraphQL: Cloudflare/CAPTCHA — **not bypassed**.
- eBay / Allegro official APIs still need credentials.

## 0.1.0 — 2026-10-26 (Europe/Chisinau)

### Milestone 0–3 foundations
- Greenfield audit, SQLite schema, Streamlit UI, fixture/manual connectors, fitment/pricing/dedupe, import/export, tests.
