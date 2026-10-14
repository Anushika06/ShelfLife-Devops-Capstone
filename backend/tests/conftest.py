"""Shared pytest fixtures.

Tests never touch the real PostgreSQL database: DATABASE_URL is forced to a
throw-away SQLite file in a temporary directory *before* the application is
imported, and every test starts from freshly created, empty tables.
"""

import os
import tempfile
from datetime import timedelta
from pathlib import Path

_TEST_DIR = Path(tempfile.mkdtemp(prefix="shelflife-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TEST_DIR / 'test.db').as_posix()}"
os.environ["EXPIRY_WARNING_DAYS"] = "3"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app.domain import today  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def test_dir() -> Path:
    return _TEST_DIR


@pytest.fixture(autouse=True)
def fresh_database():
    assert engine.url.get_backend_name() == "sqlite", "tests must not run against PostgreSQL"
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def make_item(client):
    """Create an item through the API and return the JSON response."""

    def _make(**overrides):
        payload = {
            "name": "Greek yogurt",
            "category": "Dairy",
            "location": "Fridge",
            "quantity": 2,
            "unit": "pcs",
        }
        payload.update(overrides)
        response = client.post("/api/items", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def in_days():
    """Return an ISO date N days from 'today' in the app's timezone."""

    def _in_days(days: int) -> str:
        return (today() + timedelta(days=days)).isoformat()

    return _in_days
