import os

TEST_API_KEY = os.environ["API_KEY"]


def test_delete_message_requires_api_key(client):
    response = client.delete("/api/memory/1")
    assert response.status_code == 401


def test_delete_message_removes_it(client, auth_headers):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "note à supprimer", "device_type": "desktop", "mode": "note"})
        ws.receive_json()

    history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    message_id = next(m["id"] for m in history if m["content"] == "note à supprimer")

    response = client.delete(f"/api/memory/{message_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    updated_history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    assert all(m["id"] != message_id for m in updated_history)


def test_delete_message_returns_error_for_unknown_id(client, auth_headers):
    response = client.delete("/api/memory/999999999", headers=auth_headers)
    assert response.json()["status"] == "error"
