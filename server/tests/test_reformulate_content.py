import os

TEST_API_KEY = os.environ["API_KEY"]


def test_patch_message_content_requires_api_key(client):
    response = client.patch("/api/memory/1/content", json={"content": "x"})
    assert response.status_code == 401


def test_patch_message_content_updates_it(client, auth_headers):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "une idee rapide pas clair", "device_type": "desktop", "mode": "note"})
        ws.receive_json()

    history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    message_id = next(m["id"] for m in history if m["content"] == "une idee rapide pas clair")

    response = client.patch(
        f"/api/memory/{message_id}/content",
        headers=auth_headers,
        json={"content": "Une idée rapide, mais peu claire."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    updated_history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    updated = next(m for m in updated_history if m["id"] == message_id)
    assert updated["content"] == "Une idée rapide, mais peu claire."


def test_patch_message_content_rejects_empty(client, auth_headers):
    response = client.patch("/api/memory/1/content", headers=auth_headers, json={"content": "  "})
    assert response.json()["status"] == "error"


def test_patch_message_content_returns_error_for_unknown_id(client, auth_headers):
    response = client.patch(
        "/api/memory/999999999/content",
        headers=auth_headers,
        json={"content": "x"},
    )
    assert response.json()["status"] == "error"
