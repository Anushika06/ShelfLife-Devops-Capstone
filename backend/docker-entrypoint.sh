#!/bin/sh
# Wait for PostgreSQL, apply Alembic migrations, then hand PID 1 to Uvicorn.
set -eu
python -m app.prestart
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --http h11 --proxy-headers --forwarded-allow-ips='*' "$@"
