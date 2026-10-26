# Источники — упрощённый MVP

## В поиске (без ключей, проверено)

| ID | Рынок | Метод |
|----|--------|--------|
| `olx_ua` | Украина | `POST /apigateway/graphql` |
| `prom_ua` | Украина | HTML search → Product JSON-LD |
| `flagma_ua` | Украина | HTML search → Product JSON-LD |
| `olx_pl` | Польша | `POST /apigateway/graphql` |
| `olx_ro` | Румыния | то же |
| `olx_bg` | Болгария | то же |
| `olx_pt` | Португалия | то же |
| `nine99_md` | Молдова | `POST /graphql` |
| `fixture` | — | демо |
| `manual` | — | импорт URL/CSV |

## Украина — что проверено

**Работают без ключей**

- **OLX.ua** — публичный GraphQL `ListingSearchQuery`
- **Prom.ua** — публичная выдача `/ua/search?search_term=…` с `schema.org/Product` (цена UAH, бренд, SKU, фото, URL)
- **Flagma.ua** — публичный поиск `/uk/search/?q=…` с Product JSON-LD

**Отложено (гемор / блок)**

- Rozetka — search API только ID, hydrate через Cloudflare
- Bigl — стек как у Prom, но в search HTML нет Product JSON-LD
- Hotline — Nuxt SSR без цен в HTML
- Allo / DOK / Exist / avto.pro — Cloudflare или 403

## Отсеяно (гемор)

См. `deferred_sources` в `autoparts_core/config/sources.yaml`:

- AUTO.RIA — ключ + 30 req/h + в основном авто/доноры
- eBay / Allegro — OAuth / ключи
- AUTODOC / Ovoko / Inter Cars / DOK / Exist — Cloudflare/CAPTCHA
- Brave, GOODVIN, Euro Car Parts — ключи / закрытая схема

Включать обратно только по явной необходимости (`ENABLE_AUTORIA=true` + ключ для RIA).
