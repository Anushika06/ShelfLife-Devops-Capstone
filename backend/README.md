# backend/ — ShelfLife API

FastAPI service that stores pantry items in PostgreSQL and exposes health, readiness and
Prometheus metrics endpoints. The React frontend and the Kubernetes Ingress call it under `/api`.

## Layout

| Path | Purpose |
| --- | --- |
| `app/main.py` | FastAPI app, CORS, router registration, metrics instrumentation |
| `app/config.py` | Settings from environment variables (`DATABASE_URL` or `DB_*` parts) |
| `app/db.py`, `app/models.py` | SQLAlchemy engine/session and the `pantry_items` model |
| `app/schemas.py`, `app/domain.py` | Pydantic request/response models; expiry and low-stock rules |
| `app/routers/items.py` | `/api/items` CRUD, `/api/items/{id}/consume`, `/api/summary` |
| `app/routers/system.py` | `/health`, `/ready`, `/api/meta` |
| `app/metrics.py` | Custom Prometheus metrics (`shelflife_*`) |
| `app/prestart.py` | Waits for PostgreSQL, then runs `alembic upgrade head` |
| `alembic/versions/` | `0001_create_pantry_items`, `0002_add_min_quantity` |
| `tests/` | 17 pytest tests; `conftest.py` points the app at a temporary SQLite file |
| `Dockerfile` | Multi-stage build; runtime runs as UID 10001 with `pip` removed |
| `docker-entrypoint.sh` | `python -m app.prestart`, then `exec uvicorn` |

Migrations own the schema — the app never calls `create_all()`. When several replicas start at
once, `alembic/env.py` takes a PostgreSQL advisory lock so only one migrates.

## Prerequisites

Python 3.13 (CI version), and a PostgreSQL 17 instance for running the API outside Docker
(`docker compose up -d postgres` from the repository root publishes one on `127.0.0.1:55432`).

## Commands

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

ruff check . && ruff format --check .   # lint + formatting (CI gate)
pytest -v                               # 17 tests on an isolated SQLite DB

cp .env.example .env                    # local DB settings (git-ignored)
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000/api/docs (Swagger UI), http://localhost:8000/health and
http://localhost:8000/metrics.

Build the image on its own:

```bash
docker build -t shelflife-backend:local backend/
```

Environment variables are listed in the root [README](../README.md#12-configuration-reference).
