# AutoParts Core

Поиск автозапчастей по публичным каталогам **EU · Moldova · Ukraine**.

## Сайт (основной продукт)

Next.js в папке [`web/`](web/) — лендинг, поиск, источники. Деплой на **Vercel**.

```bash
cd web && npm install && npm run dev
```

Live-каталоги: OLX UA/PL/RO/BG/PT, Prom.ua, Flagma.ua, Bazar.bg, 999.md.  
Метод: публичный GraphQL / Product JSON-LD. CAPTCHA не обходим.

## Python-ядро (локально)

Коннекторы, fitment, SQLite и Streamlit-прототип остаются в `autoparts_core/` и `app/` для разработки логики.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/Home.py
```

## Документация

- `docs/GRAPHQL_SOURCES.md` — рабочие и отложенные источники  
- `web/README.md` — сайт и Vercel
