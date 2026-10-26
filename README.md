# AutoParts Core

Поиск автозапчастей по публичным каталогам **UA · MD · RO**.

## Сайт (основной продукт)

Next.js в папке [`web/`](web/) — лендинг, поиск, источники. Деплой на **Vercel**.

```bash
cd web && npm install && npm run dev
```

Live-каталоги: OLX UA/RO, Prom.ua, Flagma.ua, Prom.md, 999.md.  
Метод: публичный GraphQL / Product JSON-LD. CAPTCHA не обходим.  
Закрытые / вне scope → [`docs/ACCESS_PATHS.md`](docs/ACCESS_PATHS.md).

## Python-ядро (локально)

Коннекторы, fitment, SQLite и Streamlit-прототип остаются в `autoparts_core/` и `app/` для разработки логики.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/Home.py
```

## Документация

- `docs/PRODUCT_TZ_V2.md` — ТЗ полного сервиса  
- `docs/ACCESS_PATHS.md` — допускает / путь сбора  
- `docs/GRAPHQL_SOURCES.md` — рабочие и отложенные источники  
- `web/README.md` — сайт и Vercel
