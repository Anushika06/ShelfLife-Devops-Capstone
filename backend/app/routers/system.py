"""Operational endpoints: liveness, readiness and service metadata."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..domain import CATEGORIES, LOCATIONS, UNITS
from ..schemas import MetaOut

router = APIRouter()


@router.get("/", include_in_schema=False)
def root():
    settings = get_settings()
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/api/docs"}


@router.get("/health", tags=["system"])
def health():
    """Liveness: the process is up. Deliberately does not touch the database."""
    return {"status": "ok"}


@router.get("/ready", tags=["system"])
def ready(db: Session = Depends(get_db)):
    """Readiness: the API can reach PostgreSQL and the schema exists."""
    try:
        db.execute(text("SELECT 1 FROM pantry_items LIMIT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "unavailable"})
    return {"status": "ready"}


@router.get("/api/meta", response_model=MetaOut, tags=["system"])
def meta():
    settings = get_settings()
    return MetaOut(
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        categories=list(CATEGORIES),
        locations=list(LOCATIONS),
        units=list(UNITS),
        expiry_warning_days=settings.expiry_warning_days,
    )
