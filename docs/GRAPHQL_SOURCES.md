# Источники — упрощённый MVP

## В поиске (без ключей, проверено)

| ID | Рынок | Метод |
|----|--------|--------|
| `olx_ua` | Украина | `POST /apigateway/graphql` |
| `olx_pl` | Польша | то же |
| `olx_ro` | Румыния | то же |
| `olx_bg` | Болгария | то же |
| `olx_pt` | Португалия | то же |
| `nine99_md` | Молдова | `POST /graphql` |
| `fixture` | — | демо |
| `manual` | — | импорт URL/CSV |

## Отсеяно (гемор)

См. `deferred_sources` в `autoparts_core/config/sources.yaml`:

- AUTO.RIA — ключ + 30 req/h + в основном авто/доноры
- eBay / Allegro — OAuth / ключи
- AUTODOC / Ovoko / Inter Cars / DOK / Exist — Cloudflare/CAPTCHA
- Brave, GOODVIN, Euro Car Parts — ключи / закрытая схема

Включать обратно только по явной необходимости (`ENABLE_AUTORIA=true` + ключ для RIA).
