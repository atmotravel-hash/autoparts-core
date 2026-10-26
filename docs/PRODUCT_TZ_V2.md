# ТЗ v2 — Полноценный сервис поиска автозапчастей

## Цель
С нуля собрать **рабочий веб-сервис** поиска запчастей: агрегирует **все источники, которые отдают публичный каталог без обхода защит**.  
Для закрытых — зафиксировать **легитимный путь** (офики API / партнёрка / ключ), не CAPTCHA/CF bypass.

## Правила доступа (жёстко)
1. **Допускается:** публичный GraphQL витрины, Product/ItemList JSON-LD в HTML поиска, официальный API с бесплатным/документированным ключом (opt-in).
2. **Запрещено:** обход Cloudflare/CAPTCHA, скрытый scrape за логином, подделка сессий.
3. Старые объявления с известной датой **> 30 дней** — отбрасывать.

## Продукт (сайт)
- Один продукт: поиск (Vehicle / OEM / Part name).
- Sidebar + форма + лента результатов + фильтры.
- Live multi-source, цена, фото, ссылка, страна, возраст.
- Честные бейджи совместимости (title heuristic ≠ verified OEM).

## Источники
### Подключаем сейчас (zero-key, проверено ранее)
UA: OLX, Prom, Flagma  
MD: 999.md  
RO: OLX  
PL: OLX  
BG: OLX, Bazar.bg  
PT: OLX  

### Пути для «не допускают» (документируем, не обходим)
| Источник | Почему блок | Путь сбора |
|----------|-------------|------------|
| Rozetka | CF на hydrate | Partner / official merchant API при наличии |
| Allegro | OAuth + CAPTCHA | [developer.allegro.pl](https://developer.allegro.pl) OAuth app |
| eBay | credentials | eBay Browse API |
| AUTODOC / DOK / Exist | CF | Партнёрский фид / affiliate API |
| AUTO.RIA | ключ + лимиты | Free key developers.ria.com (opt-in) |
| Otomoto/Autovit | cars-first | OLX Group Partner API |
| Mobile.de / AS24 | auth GraphQL | Official dealer APIs |

## Критерий готовности
- Сайт на Vercel: поиск по всем zero-key источникам
- `docs/ACCESS_PATHS.md` — карта «допускает / путь»
- Прогнан live smoke по ≥1 источнику на рынок
