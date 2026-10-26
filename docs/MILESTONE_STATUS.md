# Milestone status — v0.1.0

**Generated:** 26 Oct 2026, Europe/Chisinau (EET)

## What works

- Persistent SQLite database with Spec §13 entities
- Fixture connector search (demo data clearly labelled)
- Manual URL metadata import with SSRF checks
- Vehicle / OEM / part-name search UI
- Fitment evidence engine (catalogue-backed EXACT; title-only stays UNCONFIRMED)
- Price comparison with FX provenance + unknown cost warnings
- Duplicate scan + manual review actions
- CSV/XLSX import & export with reconcile counts
- 26 automated tests passing without live credentials

## What was tested

See `docs/TEST_REPORT.md` — 26 passed.

## Incomplete

- Live authorized marketplace connectors
- Brave Search discovery execution
- Background revalidation worker loop
- VIN decode provider
- Production Postgres hardening / backups automation
- Image perceptual hashing

## Live sources

None verified.

## Sources requiring credentials

eBay, Allegro, Brave Search, FX API, VIN API — see `docs/SOURCE_CANDIDATES.md`.

## Sample data

All fixture listings under `tests/fixtures/listings.json` and any row with `is_demo_data=true`.

## Known risks

See `docs/RISK_REGISTER.md`.

## Exact next steps

1. Supply authorized API credentials for one marketplace or search provider.
2. Implement + health-test that connector; flip `operational` only after success.
3. Add Alembic migrations for non-SQLite deploys.
4. Implement job worker for revalidation.
