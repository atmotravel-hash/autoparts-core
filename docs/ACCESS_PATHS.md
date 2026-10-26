# Карта источников и путей сбора

Метод «допускает» = публичный GraphQL витрины **или** Product/ItemList JSON-LD **или** документированный API.  
Обход Cloudflare/CAPTCHA — **нет**.

## Подключено в продукте (zero-key)

| ID | Рынок | Метод | Статус |
|----|-------|--------|--------|
| olx_ua | UA | GraphQL `/apigateway/graphql` | live (иногда 403 с части IP) |
| prom_ua | UA | search HTML Product JSON-LD | live |
| flagma_ua | UA | search HTML Product JSON-LD | live |
| nine99_md | MD | GraphQL `https://999.md/graphql` | live |
| prom_md | MD | search HTML Product JSON-LD | live |
| olx_ro | RO | GraphQL | live |
| olx_pl | PL | GraphQL | live |
| olx_bg | BG | GraphQL | live |
| bazar_bg | BG | ItemList Product JSON-LD | live |
| olx_pt | PT | GraphQL | live |

Свежесть: объявления с age > 30 дней отбрасываются.

## Не допускают публичный сбор — легитимный путь

| Источник | Блокер | Путь сбора |
|----------|--------|------------|
| Rozetka | CF на detail hydrate | Офиц. кабинет продавца / partner feed |
| Allegro | OAuth + CAPTCHA на public GQL | https://developer.allegro.pl — OAuth app |
| eBay | App credentials | eBay Browse / Buy API |
| AUTODOC / DOK.ua / Exist.ua | Cloudflare / 403 | Affiliate / B2B feed у поставщика |
| AUTO.RIA | ключ + 30 req/h | https://developers.ria.com free key (opt-in `ENABLE_AUTORIA`) |
| Otomoto / Autovit / Standvirtual | cars-first Otodom | OLX Group Partner API |
| Mobile.de / AutoScout24 | auth GraphQL | Official dealer APIs |
| Hotline / Bigl | нет Product JSON-LD в SSR | Нет публичного каталога; Bigl = стек Prom без LD на search |
| Publi24 / Jófogás / Lajumate | нет usable Product LD | Нет zero-key path на момент проверки |
| Inter Cars / iParts / Ovoko/RRR | CF / partner | Partner portal |

## Политика расширения
Новый источник попадает в продукт только после live-проверки zero-key метода **или** явного ключа/OAuth с документированным API.
