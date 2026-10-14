"""Prometheus metrics.

HTTP request count/latency metrics come from prometheus-fastapi-instrumentator
(http_requests_total, http_request_duration_seconds). The metrics below add
pantry-specific business signals for the Grafana dashboard.
"""

from prometheus_client import Counter, Gauge

ITEMS_CREATED = Counter(
    "shelflife_items_created_total",
    "Pantry items added through the API.",
    ["location"],
)
ITEMS_CONSUMED = Counter(
    "shelflife_items_consumed_total",
    "Consume actions recorded through the API.",
)
ITEMS_DELETED = Counter(
    "shelflife_items_deleted_total",
    "Pantry items removed through the API.",
)
PANTRY_ITEMS = Gauge(
    "shelflife_pantry_items",
    "Pantry items by status, refreshed whenever the summary endpoint is called.",
    ["status"],
)
