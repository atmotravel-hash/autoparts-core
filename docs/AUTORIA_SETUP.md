# AUTO.RIA — бесплатный API-ключ

Официальный API: [developers.ria.com](https://developers.ria.com/)  
Документация: [docs-developers.ria.com](https://docs-developers.ria.com/)

## Зачем

Коннектор `auto_ria` ищет объявления AUTO.RIA (в т.ч. **авто на запчасти** / доноры через `spareParts=1`) и тянет карточку через `/auto/info`.

Это **не** OEM-каталог фар/крыльев — это рынок авто/доноров в Украине. Детали по-прежнему лучше искать через OLX/999.md.

## Как получить ключ (бесплатно)

1. Открой https://developers.ria.com/ и зарегистрируйся / войди.
2. Раздел **«Мій профіль»** → скопируй **API key**.
3. Лимит free-тарифа: около **30 запросов/час** (выше — платные пакеты).
4. Обязательное условие ToS: на сайте/в приложении должна быть **индексируемая гиперссылка** на https://auto.ria.com (в UI AutoParts уже есть attribution).

## Подключение в AutoParts Core

```bash
cp .env.example .env
# вставь ключ:
echo 'AUTORIA_API_KEY=твой_ключ' >> .env
```

Или одной строкой в окружении:

```bash
export AUTORIA_API_KEY='...'
```

Проверка:

```bash
source .venv/bin/activate
python -c "from autoparts_core.connectors.registry import get_registry; print(get_registry()['auto_ria'].health_check())"
```

Ожидается `"ok": true`. После этого источник появится как **operational** в Source Connectors и в Vehicle Search.

## Используемые методы

| Метод | URL |
|-------|-----|
| Поиск | `GET /auto/search?api_key=…&category_id=1&marka_id[0]=…&spareParts=1&status_id=0` |
| Карточка | `GET /auto/info?api_key=…&auto_id=…` |
| Справочник марок | `GET /auto/categories/1/marks?api_key=…` |

Клиент держит паузу `AUTORIA_MIN_INTERVAL_SECONDS` (по умолчанию 2.5 с) между запросами.
