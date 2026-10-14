"""Dashboard summary and expiry rules."""

from datetime import date

from app.domain import expiry_status, is_low_stock


def test_summary_counts(client, make_item, in_days):
    make_item(name="Yogurt", location="Fridge", expiry_date=in_days(-1))
    make_item(name="Tofu", location="Fridge", expiry_date=in_days(0))
    make_item(name="Ice cream", location="Freezer", expiry_date=in_days(60))
    make_item(name="Lentils", location="Pantry", quantity=0, min_quantity=1)

    body = client.get("/api/summary").json()
    assert body["total"] == 4
    assert body["expired"] == 1
    assert body["expiring_soon"] == 1  # expires today counts as "expiring"
    assert body["low_stock"] == 1
    assert body["by_location"] == {"Fridge": 2, "Freezer": 1, "Pantry": 1}
    assert body["expiry_warning_days"] == 3


def test_summary_empty_pantry(client):
    body = client.get("/api/summary").json()
    assert body["total"] == 0
    assert body["by_location"] == {"Fridge": 0, "Freezer": 0, "Pantry": 0}


def test_expiry_status_boundaries():
    ref = date(2026, 10, 14)
    assert expiry_status(None, ref) == "no-date"
    assert expiry_status(date(2026, 10, 13), ref) == "expired"
    assert expiry_status(date(2026, 10, 14), ref) == "expiring"
    assert expiry_status(date(2026, 10, 17), ref) == "expiring"  # 3-day window, inclusive
    assert expiry_status(date(2026, 10, 18), ref) == "fresh"


def test_low_stock_rule():
    assert is_low_stock(1, 1) is True
    assert is_low_stock(2, 1) is False
    assert is_low_stock(0, 0) is False  # no threshold set
