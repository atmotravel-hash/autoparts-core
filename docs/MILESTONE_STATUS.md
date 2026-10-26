# Milestone status — v0.2.0

**Generated:** 26 Oct 2026, Europe/Chisinau (EET)

## What works

- Persistent SQLite database with Spec §13 entities
- **Live GraphQL collection:** OLX UA/PL/RO + 999.md (POST catalog)
- Fixture connector (demo) + manual URL import
- Vehicle / OEM / part-name search UI with source multiselect
- Fitment evidence, pricing, dedupe, import/export

## What was tested

- Unit: **32 passed** (live markers skipped by default)
- Live opt-in: `RUN_LIVE_GRAPHQL=1 pytest -m live` — **2 passed**
- E2E smoke: 51 live listings persisted from OLX/999 search (Passat B8 headlight)

## Incomplete / blocked

- AUTODOC, Ovoko, Allegro HTML GraphQL: Cloudflare/CAPTCHA — not bypassed
- eBay/Allegro official APIs need credentials
- Brave Search, VIN, background revalidation worker

## Live sources

`olx_ua`, `olx_pl`, `olx_ro`, `nine99_md` — see `docs/GRAPHQL_SOURCES.md`.

## Exact next steps

1. Allegro / eBay official API credentials when available.
2. Partner access for Ovoko/AUTODOC (no challenge bypass).
3. Revalidation worker + Alembic for Postgres.
