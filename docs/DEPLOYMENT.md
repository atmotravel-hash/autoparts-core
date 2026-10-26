# Deployment guide

## Local MVP

```bash
cd /path/to/autoparts-core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -c "from autoparts_core.db.session import init_db; init_db()"
streamlit run app/Home.py
```

Open the printed local URL. Demo mode seeds fixture listings on first launch.

## Data

- SQLite file: `data/autoparts.db` (configurable via `DATABASE_URL`)
- Exports: `exports/`
- Backup: copy `data/autoparts.db` while the app is stopped, or use `sqlite3 .backup`

## Production notes (future)

- Switch `DATABASE_URL` to PostgreSQL when concurrent workers are required.
- Put Streamlit behind auth at the reverse proxy.
- Provide real FX and marketplace credentials via a secrets manager.
- Do not enable unauthorized scraping as a fallback when quotas exhaust.
