import os

TEST_API_KEY = os.environ["API_KEY"]


def _save_note(client, content):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": content, "device_type": "desktop", "mode": "note"})
        ws.receive_json()
    history = client.get("/api/memory/history", headers={"X-API-Key": TEST_API_KEY}).json()["history"]
    return next(m["id"] for m in history if m["content"] == content)


def _link(client, auth_headers, from_id, to_id):
    client.post(f"/api/memory/{from_id}/links", headers=auth_headers, json={"to_id": to_id})


def test_related_requires_api_key(client):
    response = client.get("/api/memory/1/related")
    assert response.status_code == 401


def test_related_finds_one_and_two_hop_notes(client, auth_headers):
    id_a = _save_note(client, "note A racine")
    id_b = _save_note(client, "note B à 1 saut de A")
    id_c = _save_note(client, "note C à 2 sauts de A")
    id_d = _save_note(client, "note D non reliée")
    _link(client, auth_headers, id_a, id_b)
    _link(client, auth_headers, id_b, id_c)

    response = client.get(f"/api/memory/{id_a}/related", headers=auth_headers)
    assert response.status_code == 200
    related = response.json()["related"]

    by_id = {r["message_id"]: r for r in related}
    assert by_id[id_b]["hops"] == 1
    assert by_id[id_c]["hops"] == 2
    assert id_d not in by_id
    assert id_a not in by_id


def test_related_takes_the_shortest_path_when_multiple_exist(client, auth_headers):
    id_a = _save_note(client, "note A pour chemin le plus court")
    id_b = _save_note(client, "note B intermédiaire")
    id_c = _save_note(client, "note C atteignable par deux chemins")
    _link(client, auth_headers, id_a, id_b)
    _link(client, auth_headers, id_b, id_c)
    _link(client, auth_headers, id_a, id_c)  # direct shortcut, 1 hop

    response = client.get(f"/api/memory/{id_a}/related", headers=auth_headers)
    related = response.json()["related"]
    by_id = {r["message_id"]: r for r in related}
    assert by_id[id_c]["hops"] == 1


def test_related_returns_empty_for_unlinked_note(client, auth_headers):
    id_a = _save_note(client, "note isolée sans aucun lien")
    response = client.get(f"/api/memory/{id_a}/related", headers=auth_headers)
    assert response.json()["related"] == []
