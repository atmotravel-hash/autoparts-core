# Источники — GraphQL / JSON-LD

Метод: публичный GraphQL **или** Product/ItemList JSON-LD. Без ключей, без обхода CAPTCHA.  
Карта путей: `docs/ACCESS_PATHS.md`.

**Продуктовый scope: только UA · MD · RO.**

## В поиске (zero-key)

| ID | Рынок | Метод |
|----|--------|--------|
| `olx_ua` | UA | GraphQL ListingSearchQuery |
| `prom_ua` | UA | Product JSON-LD |
| `flagma_ua` | UA | Product JSON-LD |
| `nine99_md` | MD | GraphQL searchAds |
| `prom_md` | MD | Product JSON-LD |
| `olx_ro` | RO | GraphQL ListingSearchQuery |

Свежесть: >30 дней отбрасываются.

## Вне scope / отложено
OLX PL/BG/PT, Bazar.bg — метод работает, рынки не в продукте.  
Rozetka, Allegro, eBay, AUTODOC/DOK/Exist, AUTO.RIA (opt-in), Hotline/Bigl — см. ACCESS_PATHS.

## Live-тест
`RUN_LIVE_GRAPHQL=1 pytest -m live`
