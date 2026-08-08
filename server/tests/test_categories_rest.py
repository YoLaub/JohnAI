import os

TEST_API_KEY = os.environ["API_KEY"]


def test_get_categories_requires_api_key(client):
    response = client.get("/api/categories")
    assert response.status_code == 401


def test_get_categories_lists_defaults(client, auth_headers):
    response = client.get("/api/categories", headers=auth_headers)
    assert response.status_code == 200
    assert "Famille" in response.json()["categories"]


def test_post_category_creates_new_category(client, auth_headers):
    response = client.post("/api/categories", headers=auth_headers, json={"name": "Sport"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    listed = client.get("/api/categories", headers=auth_headers).json()["categories"]
    assert "Sport" in listed


def test_post_category_rejects_missing_name(client, auth_headers):
    response = client.post("/api/categories", headers=auth_headers, json={})
    assert response.json()["status"] == "error"


def test_patch_message_category_updates_and_creates_category(client, auth_headers):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "pensée à reclasser plus tard", "device_type": "desktop", "mode": "note"})
        ws.receive_json()

    history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    message_id = next(m["id"] for m in history if m["content"] == "pensée à reclasser plus tard")

    response = client.patch(
        f"/api/memory/{message_id}/category",
        headers=auth_headers,
        json={"category": "Bricolage"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    updated_history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    updated = next(m for m in updated_history if m["id"] == message_id)
    assert updated["category"] == "Bricolage"
    assert "Bricolage" in client.get("/api/categories", headers=auth_headers).json()["categories"]


def test_patch_message_category_empty_clears_it(client, auth_headers):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "note à déclasser", "device_type": "desktop", "mode": "note", "category": "Philo"})
        ws.receive_json()

    history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    message_id = next(m["id"] for m in history if m["content"] == "note à déclasser")
    assert next(m for m in history if m["id"] == message_id)["category"] == "Philo"

    response = client.patch(
        f"/api/memory/{message_id}/category",
        headers=auth_headers,
        json={"category": ""},
    )
    assert response.status_code == 200
    assert response.json()["category"] is None

    cleared_history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    assert next(m for m in cleared_history if m["id"] == message_id)["category"] is None


def test_patch_message_category_returns_error_for_unknown_id(client, auth_headers):
    response = client.patch(
        "/api/memory/999999999/category",
        headers=auth_headers,
        json={"category": "Famille"},
    )
    assert response.json()["status"] == "error"
