# AutoParts Intelligence Platform — AUTOPARTS CORE v0.2.0

Modular automotive parts intelligence for **Europe, Moldova, and Ukraine**.

This is **not** a generic scraper. It is a traceable multi-source search, identification, fitment, pricing, and seller-intelligence MVP.

## Live GraphQL catalogs (tested)

| Source | Endpoint | Market |
|--------|----------|--------|
| OLX UA | `POST /apigateway/graphql` | Ukraine |
| OLX PL | `POST /apigateway/graphql` | Poland |
| OLX RO | `POST /apigateway/graphql` | Romania |
| 999.md | `POST /graphql` | Moldova |

See `docs/GRAPHQL_SOURCES.md`. Cloudflare/CAPTCHA on AUTODOC/Ovoko/Allegro is **not** bypassed.

## Important honesty labels

- Offline **fixture / demo** listings are flagged `is_demo_data`.
- eBay / Allegro official APIs still need credentials.
- Live collection uses public catalog GraphQL the sites already expose to their UI.

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
