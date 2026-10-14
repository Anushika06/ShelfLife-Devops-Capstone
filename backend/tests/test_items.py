"""CRUD behaviour of /api/items."""


def test_create_item_returns_201_and_computed_fields(client, in_days):
    response = client.post(
        "/api/items",
        json={
            "name": "  Paneer  ",
            "category": "Dairy",
            "location": "Fridge",
            "quantity": 1,
            "unit": "pack",
            "min_quantity": 1,
            "expiry_date": in_days(2),
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["name"] == "Paneer"  # whitespace trimmed
    assert body["expiry_status"] == "expiring"
    assert body["days_until_expiry"] == 2
    assert body["low_stock"] is True


def test_create_item_rejects_invalid_payload(client):
    assert client.post("/api/items", json={"name": ""}).status_code == 422
    assert client.post("/api/items", json={"name": "Rice", "quantity": -1}).status_code == 422
    assert client.post("/api/items", json={"name": "Rice", "location": "Garage"}).status_code == 422


def test_list_items_sorted_by_soonest_expiry(client, make_item, in_days):
    make_item(name="No date honey", expiry_date=None)
    make_item(name="Milk", expiry_date=in_days(1))
    make_item(name="Old bread", expiry_date=in_days(-2))
    names = [item["name"] for item in client.get("/api/items").json()]
    assert names == ["Old bread", "Milk", "No date honey"]


def test_list_items_filters(client, make_item, in_days):
    make_item(name="Frozen peas", location="Freezer", category="Frozen", expiry_date=in_days(90))
    make_item(name="Spinach", location="Fridge", category="Produce", expiry_date=in_days(-1))
    make_item(name="Basmati rice", location="Pantry", category="Grains & Pasta", quantity=0.5, min_quantity=1)

    def names(**params):
        return [item["name"] for item in client.get("/api/items", params=params).json()]

    assert names(location="Freezer") == ["Frozen peas"]
    assert names(status="expired") == ["Spinach"]
    assert names(status="fresh") == ["Frozen peas"]
    assert names(status="low-stock") == ["Basmati rice"]
    assert names(q="RICE") == ["Basmati rice"]
    assert client.get("/api/items", params={"status": "rotten"}).status_code == 422


def test_get_item_by_id_and_404(client, make_item):
    created = make_item(name="Oats")
    response = client.get(f"/api/items/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Oats"
    assert client.get("/api/items/99999").status_code == 404


def test_put_replaces_item(client, make_item, in_days):
    created = make_item(name="Butter", quantity=1)
    update = {
        "name": "Salted butter",
        "category": "Dairy",
        "location": "Freezer",
        "quantity": 3,
        "unit": "pack",
        "min_quantity": 1,
        "expiry_date": in_days(30),
        "notes": "Moved to freezer",
    }
    response = client.put(f"/api/items/{created['id']}", json=update)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Salted butter"
    assert body["location"] == "Freezer"
    assert body["quantity"] == 3
    assert body["notes"] == "Moved to freezer"
    # The change is persisted, not just echoed back.
    assert client.get(f"/api/items/{created['id']}").json()["location"] == "Freezer"
    assert client.put("/api/items/99999", json=update).status_code == 404


def test_consume_decrements_and_never_goes_negative(client, make_item):
    created = make_item(name="Eggs", quantity=3)
    first = client.post(f"/api/items/{created['id']}/consume", json={"amount": 2})
    assert first.status_code == 200
    assert first.json()["quantity"] == 1
    second = client.post(f"/api/items/{created['id']}/consume", json={"amount": 5})
    assert second.json()["quantity"] == 0
    assert client.post(f"/api/items/{created['id']}/consume", json={"amount": 0}).status_code == 422


def test_delete_item(client, make_item):
    created = make_item(name="Leftover curry")
    response = client.delete(f"/api/items/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/items/{created['id']}").status_code == 404
    assert client.delete(f"/api/items/{created['id']}").status_code == 404
