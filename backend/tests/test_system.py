"""Health, readiness, metadata and metrics endpoints."""


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_checks_database(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_meta_lists_allowed_values(client):
    body = client.get("/api/meta").json()
    assert body["service"] == "ShelfLife API"
    assert body["locations"] == ["Fridge", "Freezer", "Pantry"]
    assert "Dairy" in body["categories"]
    assert body["expiry_warning_days"] == 3


def test_metrics_endpoint_exposes_prometheus_format(client, make_item):
    make_item()
    client.get("/api/items")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    text = response.text
    assert "# TYPE http_requests_total counter" in text
    assert 'handler="/api/items"' in text
    assert "shelflife_items_created_total" in text
    # Probe endpoints are excluded so they do not drown out real traffic.
    assert 'handler="/health"' not in text
