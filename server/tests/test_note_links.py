import os

TEST_API_KEY = os.environ["API_KEY"]


def _save_note(client, content, category=None):
    payload = {"content": content, "device_type": "desktop", "mode": "note"}
    if category:
        payload["category"] = category
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json(payload)
        ws.receive_json()
    history = client.get("/api/memory/history", headers={"X-API-Key": TEST_API_KEY}).json()["history"]
    return next(m["id"] for m in history if m["content"] == content)


def test_create_link_requires_api_key(client):
    response = client.post("/api/memory/1/links", json={"to_id": 2})
    assert response.status_code == 401


def test_create_and_list_link(client, auth_headers):
    id_a = _save_note(client, "idée A à relier")
    id_b = _save_note(client, "idée B liée à A")

    response = client.post(f"/api/memory/{id_a}/links", headers=auth_headers, json={"to_id": id_b})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    links_a = client.get(f"/api/memory/{id_a}/links", headers=auth_headers).json()["links"]
    assert len(links_a) == 1
    assert links_a[0]["message_id"] == id_b
    assert links_a[0]["content"] == "idée B liée à A"
    assert "created_at" in links_a[0]

    # Undirected: the link shows up from the other side too.
    links_b = client.get(f"/api/memory/{id_b}/links", headers=auth_headers).json()["links"]
    assert len(links_b) == 1
    assert links_b[0]["message_id"] == id_a


def test_create_link_is_idempotent_regardless_of_direction(client, auth_headers):
    id_a = _save_note(client, "note X pour idempotence")
    id_b = _save_note(client, "note Y pour idempotence")

    client.post(f"/api/memory/{id_a}/links", headers=auth_headers, json={"to_id": id_b})
    client.post(f"/api/memory/{id_b}/links", headers=auth_headers, json={"to_id": id_a})

    links_a = client.get(f"/api/memory/{id_a}/links", headers=auth_headers).json()["links"]
    assert len(links_a) == 1


def test_create_link_rejects_missing_to_id(client, auth_headers):
    response = client.post("/api/memory/1/links", headers=auth_headers, json={})
    assert response.json()["status"] == "error"


def test_create_link_rejects_self_link(client, auth_headers):
    id_a = _save_note(client, "note qui ne peut pas se lier à elle-même")
    response = client.post(f"/api/memory/{id_a}/links", headers=auth_headers, json={"to_id": id_a})
    assert response.json()["status"] == "error"


def test_delete_link(client, auth_headers):
    id_a = _save_note(client, "note à délier A")
    id_b = _save_note(client, "note à délier B")
    create_response = client.post(f"/api/memory/{id_a}/links", headers=auth_headers, json={"to_id": id_b})
    link_id = create_response.json()["link_id"]

    delete_response = client.delete(f"/api/memory/links/{link_id}", headers=auth_headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] == "ok"

    links_a = client.get(f"/api/memory/{id_a}/links", headers=auth_headers).json()["links"]
    assert links_a == []


def test_delete_link_returns_error_for_unknown_id(client, auth_headers):
    response = client.delete("/api/memory/links/999999999", headers=auth_headers)
    assert response.json()["status"] == "error"


def test_deleting_a_note_removes_its_links(client, auth_headers):
    id_a = _save_note(client, "note supprimée avec ses liens A")
    id_b = _save_note(client, "note supprimée avec ses liens B")
    client.post(f"/api/memory/{id_a}/links", headers=auth_headers, json={"to_id": id_b})

    client.delete(f"/api/memory/{id_a}", headers=auth_headers)

    links_b = client.get(f"/api/memory/{id_b}/links", headers=auth_headers).json()["links"]
    assert links_b == []
