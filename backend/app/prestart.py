"""Container start-up step: wait for PostgreSQL, then apply Alembic migrations.

Run as `python -m app.prestart` before Uvicorn. Several replicas may start at the
same time; alembic/env.py takes a PostgreSQL advisory lock so only one of them
migrates while the others wait.
"""

import logging
import sys
import time
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .config import get_settings
from .db import engine

log = logging.getLogger("shelflife.prestart")
BACKEND_DIR = Path(__file__).resolve().parent.parent


def wait_for_database(timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    attempt = 0
    while True:
        attempt += 1
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            log.info("database reachable after %d attempt(s)", attempt)
            return
        except OperationalError as exc:
            if time.monotonic() >= deadline:
                raise RuntimeError(f"database not reachable after {timeout_seconds}s") from exc
            log.info("waiting for database (attempt %d)...", attempt)
            time.sleep(2)


def run_migrations() -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(config, "head")
    log.info("migrations applied")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    wait_for_database(get_settings().db_wait_seconds)
    run_migrations()
    return 0


if __name__ == "__main__":
    sys.exit(main())
