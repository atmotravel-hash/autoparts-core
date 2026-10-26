# Источники — упрощённый MVP

Метод проверки: публичный GraphQL **или** Product/ItemList JSON-LD в HTML поиска.  
Без ключей, без обхода CAPTCHA/Cloudflare.

## В поиске (без ключей, проверено live)

| ID | Рынок | Метод |
|----|--------|--------|
| `olx_ua` | Украина | `POST /apigateway/graphql` |
| `prom_ua` | Украина | HTML search → Product JSON-LD |
| `flagma_ua` | Украина | HTML search → Product JSON-LD |
| `olx_pl` | Польша | GraphQL ListingSearchQuery |
| `olx_ro` | Румыния | то же |
| `olx_bg` | Болгария | то же |
| `bazar_bg` | Болгария | HTML ItemList → Product JSON-LD |
| `olx_pt` | Португалия | GraphQL ListingSearchQuery |
| `nine99_md` | Молдова | `POST /graphql` searchAds |
| `fixture` / `manual` | — | демо / импорт |

## Полный скан (что проверено)

### Работают тем же методом
- OLX: PL/RO/BG/PT (+ UA — GraphQL, иногда 403)
- 999.md GraphQL
- Prom.ua / Flagma.ua JSON-LD
- Bazar.bg ItemList/Product JSON-LD

### Вне фокуса EU/MD/UA
- Satu.kz / Deal.by — метод тот же (Prom-group JSON-LD), но рынки KZ/BY не нужны → `deferred_sources`

### Отложено (гемор / блок / бесполезно для запчастей)
См. `deferred_sources` в `sources.yaml`: Rozetka, Bigl, Hotline, Allo, DOK, Exist, AUTODOC, Allegro, eBay, Otomoto/Autovit/Standvirtual (cars-first), Kleinanzeigen, Wallapop, Vinted, Bazos, Jófogás, SS.LV, Mobile.bg, Subito, Avito, Kaspi, RRR/Ovoko, Ceneo, Makler.md, Bomba.md, Autoplius, Skelbiu, Publi24, Mobile.de, AutoScout24, и др.

## Live-тест
`RUN_LIVE_GRAPHQL=1 pytest -m live`
