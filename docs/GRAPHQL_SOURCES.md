# Источники — GraphQL / JSON-LD

Метод проверки: публичный GraphQL **или** Product/ItemList JSON-LD в HTML поиска.  
Без ключей, без обхода CAPTCHA/Cloudflare. Карта путей для закрытых: `docs/ACCESS_PATHS.md`.

## В поиске (zero-key, live)

| ID | Рынок | Метод |
|----|--------|--------|
| `olx_ua` | UA | `POST /apigateway/graphql` ListingSearchQuery |
| `prom_ua` | UA | HTML search → Product JSON-LD |
| `flagma_ua` | UA | HTML search → Product JSON-LD |
| `nine99_md` | MD | `POST /graphql` searchAds |
| `prom_md` | MD | HTML search → Product JSON-LD |
| `olx_ro` | RO | GraphQL ListingSearchQuery |
| `olx_pl` | PL | GraphQL ListingSearchQuery |
| `olx_bg` | BG | GraphQL ListingSearchQuery |
| `bazar_bg` | BG | ItemList / Product JSON-LD |
| `olx_pt` | PT | GraphQL ListingSearchQuery |
| `fixture` / `manual` | — | демо / импорт |

**Свежесть:** объявления старше 30 дней отбрасываются (если возраст известен).

## Отложено (не обходим)

Rozetka, Allegro, eBay, AUTODOC/DOK/Exist, AUTO.RIA (opt-in key), Otomoto/Autovit, Hotline/Bigl, Publi24/Jófogás, Mobile.de/AS24, Inter Cars/Ovoko — см. `docs/ACCESS_PATHS.md` и `deferred_sources` в `sources.yaml`.

KZ/BY (Satu.kz / Deal.by) — вне scope.

## Live-тест
`RUN_LIVE_GRAPHQL=1 pytest -m live`
