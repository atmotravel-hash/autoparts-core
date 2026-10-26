# Source candidate evaluation

| Source | Access in this env | Method | Auth | Tested? | Operational? | Notes |
|--------|--------------------|--------|------|---------|--------------|-------|
| Fixture | Yes | Local JSON | None | Yes | Yes | Demo only |
| Manual URL | Yes | User metadata | None | Yes | Yes | No scrape of protected content |
| OLX UA/PL/RO/BG/PT | Yes | Public GraphQL | None | Yes | Yes | ListingSearchQuery |
| 999.md | Yes | Public GraphQL | None | Yes | Yes | searchAds |
| Prom.ua | Yes | HTML Product JSON-LD | None | Yes | Yes | Search + detail |
| Flagma.ua | Yes | HTML Product JSON-LD | None | Yes | Yes | Search listings |
| Rozetka | Partial | Search API IDs only | None | Yes | No | Goods hydrate CF |
| Bigl.ua | Partial | HTML | None | Yes | No | No Product JSON-LD on search |
| Hotline.ua | Partial | Nuxt SSR | None | Yes | No | Prices not in HTML |
| AUTO.RIA | Optional | Official API | Free key | Yes | Opt-in | Cars/donors focus |
| eBay | No | Official API | App credentials | No | No | Deferred |
| Allegro | No | Official API | OAuth | No | No | Deferred |
| AUTODOC / DOK / Exist | No | Blocked | — | Yes | No | Cloudflare / 403 |

Never mark a source operational merely because its public URL is known.
