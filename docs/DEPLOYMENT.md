# Deployment

## Website → Vercel (primary)

Project root for Vercel: **`web/`**

```bash
cd web
npm install
npm run build
npx vercel --prod
```

Or connect the GitHub repo in Vercel UI and set **Root Directory** = `web`.

### Env

No API keys required for default live catalogs.

### Local preview

```bash
cd web && npm run dev
```

## Python / Streamlit (local only)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c "from autoparts_core.db.session import init_db; init_db()"
streamlit run app/Home.py
```

Streamlit is the research UI for connectors/fitment — not the public site.
