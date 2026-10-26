# GraphQL / catalog sources — 26 Oct 2026 (Europe/Chisinau)

## Working (tested this environment)

| Source | Endpoint | Method | Markets |
|--------|----------|--------|---------|
| 999.md | `POST https://999.md/graphql` | `searchAds`, `advert` | Moldova |
| OLX UA | `POST …/apigateway/graphql` | `ListingSearchQuery` | Ukraine |
| OLX PL | same | `ListingSearchQuery` | Poland |
| OLX RO | same | `ListingSearchQuery` | Romania |
| OLX BG | same | `ListingSearchQuery` | Bulgaria |
| OLX PT | same | `ListingSearchQuery` | Portugal |

These use the same public catalog GraphQL the websites call from their UI. Client-side rate limits apply. CAPTCHA/Cloudflare challenges are **not** bypassed.

## Broad scan (~70 hosts)

Many classifieds/parts shops were probed for `/graphql`, `/apigateway/graphql`, `/api/graphql`.

| Candidate | Finding |
|-----------|---------|
| AUTO.RIA | Public JSON search for vehicles; parts → `developers.ria.com` API key |
| Euro Car Parts `/api/graphql` | Endpoint alive; schema locked without known operations |
| Otomoto / Standvirtual | Challenge or incompatible schema |
| Kleinanzeigen | 403 JSON |
| Lalafo / Kufar / Autoplius | No usable public search in this probe |
| AUTODOC / Ovoko / Allegro / Inter Cars / DOK / Exist | Cloudflare/CAPTCHA or deny — not bypassed |

## Configuration

- Catalog: `autoparts_core/config/sources.yaml`
- Flags: `ENABLE_LIVE_GRAPHQL`, `INCLUDE_FIXTURE_IN_LIVE_SEARCH`
- Live tests: `RUN_LIVE_GRAPHQL=1 pytest -m live`
