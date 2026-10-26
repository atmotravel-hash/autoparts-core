# Architecture

```
┌──────────────────┐
│  Streamlit UI    │  app/Home.py + pages (14 nav modules)
└────────┬─────────┘
         │
┌────────▼─────────┐     ┌─────────────────────┐
│ Application core │────▶│ SQLite (MVP)        │
│ services/        │     │ SQLAlchemy models   │
│ identity/        │     │ idempotent ingest   │
│ fitment/         │     └─────────────────────┘
│ pricing/         │
│ dedupe/          │
│ discovery/       │
│ io/              │
│ security/        │
│ jobs/            │
└────────┬─────────┘
         │
┌────────▼─────────┐
│ Connector API    │  fixture (operational demo)
│ SourceConnector  │  manual (URL metadata import)
│ registry         │  ebay/allegro/brave (stubs — not operational)
└──────────────────┘
```

## Design invariants

1. Discovery ≠ extraction ≠ availability confirmation.
2. Fitment requires evidence; title-only never `VERIFIED_EXACT`.
3. Price unknowns are never silently zero.
4. Demo/fixture data is always labelled `is_demo_data`.
5. Connectors are `operational=False` until a successful test.
6. SSRF protections on all URL imports.
