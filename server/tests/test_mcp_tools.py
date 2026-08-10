import os

TEST_API_KEY = os.environ["API_KEY"]


def _save_note(client, content, category=None):
    payload = {"content": content, "device_type": "desktop", "mode": "note"}
    if category:
        payload["category"] = category
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json(payload)
        ws.receive_json()


def test_get_messages_by_category_is_case_insensitive_and_user_only(client, auth_headers):
    _save_note(client, "note projet A", category="Projet")
    _save_note(client, "note projet B", category="projet")  # different case, same category
    _save_note(client, "note famille", category="Famille")

    try:
        from server.database import get_messages_by_category
    except ModuleNotFoundError:
        from database import get_messages_by_category

    notes = get_messages_by_category("PROJET")
    contents = {n["content"] for n in notes}
    assert "note projet A" in contents
    assert "note projet B" in contents
    assert "note famille" not in contents
    assert all("created_at" in n and "id" in n for n in notes)


def test_get_messages_by_category_returns_empty_for_unknown_category(client, auth_headers):
    try:
        from server.database import get_messages_by_category
    except ModuleNotFoundError:
        from database import get_messages_by_category

    assert get_messages_by_category("catégorie qui n'existe pas du tout") == []
