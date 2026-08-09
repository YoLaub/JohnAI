import os

try:
    from server.database import save_message
except ModuleNotFoundError:
    from database import save_message

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


def test_linked_note_content_is_injected_when_both_ends_are_in_the_recent_window(client, auth_headers):
    id_a = _save_note(client, "le bug d'auth sur l'ancienne stack")
    id_b = _save_note(client, "migration React en cours")
    client.post(f"/api/memory/{id_a}/links", headers=auth_headers, json={"to_id": id_b})

    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "où en est la migration ?",
            "device_type": "desktop",
            "supports_local_generation": True,
        })
        msg = ws.receive_json()

    assert msg["type"] == "generate_locally"
    system_message = next(m for m in msg["messages"] if m["role"] == "system")
    assert "migration React en cours" in system_message["content"]


def test_linked_note_resurfaces_after_scrolling_out_of_the_recent_window(client, auth_headers):
    """The whole point of the graph layer: a note that fell out of the last-20
    window still gets pulled back in because it's explicitly linked to
    something that's still visible."""
    id_a = _save_note(client, "note ancienne reliée, hors fenêtre récente")
    id_b = _save_note(client, "note récente qui reste dans la fenêtre")
    client.post(f"/api/memory/{id_a}/links", headers=auth_headers, json={"to_id": id_b})

    # Push id_a out of the last-20 window while keeping id_b just inside it.
    for i in range(18):
        save_message(device_type="desktop", role="user", content=f"note de remplissage {i}")

    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "question sans rapport direct",
            "device_type": "desktop",
            "supports_local_generation": True,
        })
        msg = ws.receive_json()

    system_message = next(m for m in msg["messages"] if m["role"] == "system")
    user_messages = [m["content"] for m in msg["messages"] if m["role"] == "user"]
    assert "note ancienne reliée, hors fenêtre récente" not in user_messages
    assert "note ancienne reliée, hors fenêtre récente" in system_message["content"]


def test_no_graph_section_when_nothing_is_linked(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "une question sans aucun lien",
            "device_type": "desktop",
            "supports_local_generation": True,
        })
        msg = ws.receive_json()

    system_message = next(m for m in msg["messages"] if m["role"] == "system")
    assert "Notes liées" not in system_message["content"]
