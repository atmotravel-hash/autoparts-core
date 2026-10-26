# GraphQL / catalog sources — 26 Oct 2026 (Europe/Chisinau)

## Working (tested this environment)

| Source | Endpoint | Method | Markets |
|--------|----------|--------|---------|
| 999.md | `POST https://999.md/graphql` | `searchAds`, `advert` | Moldova |
| OLX UA | `POST https://www.olx.ua/apigateway/graphql` | `ListingSearchQuery` | Ukraine |
| OLX PL | `POST https://www.olx.pl/apigateway/graphql` | `ListingSearchQuery` | Poland |
| OLX RO | `POST https://www.olx.ro/apigateway/graphql` | `ListingSearchQuery` | Romania |

These use the same public catalog GraphQL the websites call from their UI. Client-side rate limits apply. CAPTCHA/Cloudflare challenges are **not** bypassed.

## Blocked / not operational (honest)

| Source | Result | Action |
|--------|--------|--------|
| AUTODOC `*/graphql` | Cloudflare challenge | Need authorized API / RapidAPI |
| Ovoko / RRR | Cloudflare challenge | Partner API |
| Allegro `/graphql` | Captcha delivery | Official Allegro REST API + OAuth |
| Inter Cars, DOK.ua, Exist.ua | Challenge / deny | Re-evaluate with credentials |
| Euro Car Parts Omnipart GraphQL | HTTP 403 | Auth required |
| eBay | No public GraphQL catalog here | Official Browse API |

## Configuration

- Catalog: `autoparts_core/config/sources.yaml`
- Flags: `ENABLE_LIVE_GRAPHQL`, `INCLUDE_FIXTURE_IN_LIVE_SEARCH`
- Live tests: `RUN_LIVE_GRAPHQL=1 pytest -m live`
