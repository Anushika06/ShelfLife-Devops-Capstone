"""ShelfLife API entry point.

The schema is owned by Alembic: containers run `python -m app.prestart` (which
applies migrations) before Uvicorn starts, so the app never calls create_all().
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from .config import get_settings
from .routers import items, system

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Track what is in your fridge, freezer and pantry, and what expires soon.",
    # Docs live under /api so the Ingress rule "/api -> backend" covers them too.
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
    )

app.include_router(system.router)
app.include_router(items.router)

# Probe and scrape traffic is excluded so dashboards show real user/API traffic.
Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)
