# Source candidate evaluation

Method: public GraphQL gateway **or** schema.org Product/ItemList JSON-LD in search HTML.  
Never mark operational just because a URL is known. No CAPTCHA/CF bypass.

| Source | Access | Method | Auth | Tested | Operational | Notes |
|--------|--------|--------|------|--------|-------------|-------|
| Fixture / Manual | Yes | Local / user | None | Yes | Yes | Demo / SSRF-safe |
| OLX UA/PL/RO/BG/PT | Yes | Public GraphQL | None | Yes | Yes | ListingSearchQuery |
| 999.md | Yes | Public GraphQL | None | Yes | Yes | searchAds |
| Prom.ua | Yes | Product JSON-LD | None | Yes | Yes | Search + detail |
| Flagma.ua | Yes | Product JSON-LD | None | Yes | Yes | B2B/marketplace |
| Bazar.bg | Yes | ItemList JSON-LD | None | Yes | Yes | Classifieds EUR |
| Satu.kz / Deal.by | Yes | Product JSON-LD | None | Yes | No | Outside EU/MD/UA focus |
| Bigl / Hotline | Partial | HTML | None | Yes | No | No priced Product SSR |
| Rozetka | Partial | Search API IDs | None | Yes | No | Hydrate CF |
| Allegro / eBay / AUTODOC | No | Blocked/credentials | — | Yes | No | Deferred |
| Otomoto / Autovit / Standvirtual | Partial | Otodom stack | None | Yes | No | Cars-first |
| Kleinanzeigen / Wallapop / Vinted / Bazos / Jófogás / SS.LV | Partial | HTML | None | Yes | No | No usable Product JSON-LD |
| AUTO.RIA | Optional | Official API | Free key | Yes | Opt-in | Cars/donors |
