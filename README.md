# AutoParts Intelligence Platform — AUTOPARTS CORE v0.1.0

Modular automotive parts intelligence for **Europe, Moldova, and Ukraine**.

This is **not** a generic scraper. It is a traceable multi-source search, identification, fitment, pricing, and seller-intelligence MVP.

## Important honesty labels

- **No live marketplace connector has been verified** in this environment.
- Offline **fixture / demo** listings are seeded when `DEMO_MODE=true` and are always flagged `is_demo_data`.
- eBay / Allegro / Brave Search appear in the registry as **non-operational stubs** until authorized access is tested.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/Home.py
```

## Tests

```bash
pytest -q
```

## Milestone status

| Milestone | Status |
|-----------|--------|
| M0 Audit | Complete — see `docs/AUDIT_REPORT.md` |
| M1 Working core | Complete (fixture + manual + import/export + UI) |
| M2 Data quality | Core engines in place |
| M3 Market intelligence | Fixture FX + landed cost + sellers + price history |
| M4 Hardening | Job/error tables only — scheduler deferred |

## Navigation

Dashboard · Vehicle Search · OEM Search · Part Name Search · Discovery · Listings · Price Comparison · Sellers · Duplicate Review · Import · Export · Source Connectors · Jobs and Logs · Settings

## Documentation

- `docs/AUDIT_REPORT.md`
- `docs/ARCHITECTURE.md`
- `docs/IMPLEMENTATION_PLAN.md`
- `docs/RISK_REGISTER.md`
- `docs/KNOWN_LIMITATIONS.md`
- `docs/SECURITY_NOTES.md`
- `docs/DEPLOYMENT.md`
- `docs/TEST_REPORT.md`
- `docs/CHANGELOG.md`

## Non-negotiable rules (enforced in code paths)

1. No fabricated listings/prices/contacts.
2. No exact fitment from title similarity alone.
3. No treating similar OEM strings as interchangeable without evidence.
4. Unknown shipping/taxes are not silently zero.
5. Connectors are not “operational” until tested.
