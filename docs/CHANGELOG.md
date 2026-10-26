# Changelog

## 0.2.4 — 2026-10-26 (Europe/Chisinau)

### Scope cleanup
- Removed **Satu.kz** and **Deal.by** from active search (outside EU/MD/UA). Kept in `deferred_sources` only.

## 0.2.3 — 2026-10-26 (Europe/Chisinau)

### Broad catalog scan (GraphQL + JSON-LD method)
- Added **Bazar.bg** via parameterized `jsonld_catalog` connector (EU).
- Full probe of ~60+ thematic sites; deferred list updated honestly in `sources.yaml`.
- Live-verified priced Product/ItemList JSON-LD only — no CAPTCHA bypass.

## 0.2.2 — 2026-10-26 (Europe/Chisinau)

### Ukraine catalog expansion
- **Prom.ua** (`prom_ua`) and **Flagma.ua** (`flagma_ua`): public search HTML → schema.org Product JSON-LD.
- Shared `jsonld_client` with SSRF checks, rate limits, CAPTCHA refusal.
- Deferred: Rozetka (CF hydrate), Bigl/Hotline (no usable SSR products), Allo/DOK/Exist (blocked).

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
