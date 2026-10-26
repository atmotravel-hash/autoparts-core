# Implementation plan

| Milestone | Status | Deliverables |
|-----------|--------|--------------|
| M0 Audit | Done | Audit report, architecture, risks, plan |
| M1 Working core | Done in this delivery | Schema, connectors, Streamlit, import/export, fixture search, dedupe L-A/B |
| M2 Data quality | Partial | Taxonomy, OEM normalize, fitment evidence, condition/completeness |
| M3 Market intelligence | Partial | Fixture FX, landed cost, seller entities, price history observations |
| M4 Hardening | Stub | Job queue table, error events; backups/monitoring deferred |

## Exact next steps

1. Obtain authorized API credentials for at least one marketplace or search provider.
2. Implement and **test** that connector; set `operational=True` only after health check passes.
3. Add Alembic revision workflow for non-SQLite deployments.
4. Wire revalidation worker against bounded job queue.
5. Expand trusted OEM catalogue beyond fixtures with documented sources.
