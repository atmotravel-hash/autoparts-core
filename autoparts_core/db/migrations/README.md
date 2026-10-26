# Schema migrations

MVP uses `Base.metadata.create_all()` via `init_db()` for SQLite bootstrap.

For PostgreSQL / production, adopt Alembic:

```bash
alembic init alembic
# set sqlalchemy.url from DATABASE_URL
alembic revision --autogenerate -m "baseline"
alembic upgrade head
```

Versioned schema source of truth today: `autoparts_core/db/models.py` (v0.1.0).
