"""Alembic migration environment.

Uses the application's settings for the database URL so migrations and the API
always target the same database. On PostgreSQL a transaction-level advisory lock
serialises concurrent `alembic upgrade` runs (e.g. two backend replicas starting
together in Kubernetes).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool, text

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.config import get_settings
from app.db import Base

config = context.config
if config.config_file_name and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata
MIGRATION_LOCK_ID = 73102026  # arbitrary constant, unique to this application


def database_url() -> str:
    return config.attributes.get("database_url") or get_settings().sqlalchemy_url


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(database_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        is_postgres = connection.dialect.name == "postgresql"
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            if is_postgres:
                connection.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": MIGRATION_LOCK_ID})
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
