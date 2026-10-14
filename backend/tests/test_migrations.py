"""Alembic migrations apply and roll back cleanly (on a separate SQLite file).

CI additionally runs the same upgrade/downgrade cycle against a real PostgreSQL
service container.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

BACKEND_DIR = Path(__file__).resolve().parent.parent


def _alembic_config(url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    config.attributes["database_url"] = url
    config.attributes["configure_logger"] = False
    return config


def test_upgrade_and_downgrade(test_dir):
    url = f"sqlite:///{(test_dir / 'migrations.db').as_posix()}"
    config = _alembic_config(url)
    engine = create_engine(url)

    command.upgrade(config, "head")
    columns = {col["name"] for col in inspect(engine).get_columns("pantry_items")}
    assert {"name", "location", "expiry_date", "min_quantity"} <= columns

    command.downgrade(config, "0001_create_pantry_items")
    columns = {col["name"] for col in inspect(engine).get_columns("pantry_items")}
    assert "min_quantity" not in columns

    command.downgrade(config, "base")
    assert "pantry_items" not in inspect(engine).get_table_names()
    engine.dispose()
