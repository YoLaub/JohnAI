import os

TEST_API_KEY = os.environ["API_KEY"]


def test_categorize_command_targets_previous_message_not_itself(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "j'ai appelé maman aujourd'hui", "device_type": "desktop", "mode": "note"})
        ws.receive_json()

        ws.send_json({"content": "mets ça dans Famille", "device_type": "desktop"})
        confirm = ws.receive_json()

    assert confirm["type"] == "done"
    assert "Famille" in confirm["full_text"]

    res = client.get("/api/memory/history", headers={"X-API-Key": TEST_API_KEY})
    history = res.json()["history"]
    thought = next(m for m in history if m["content"] == "j'ai appelé maman aujourd'hui")
    assert thought["category"] == "Famille"
    # the command utterance itself must not show up as a separate note
    assert not any(m["content"] == "mets ça dans Famille" for m in history)


def test_categorize_command_creates_new_category_on_the_fly(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "idée de voyage au Japon", "device_type": "desktop", "mode": "note"})
        ws.receive_json()

        ws.send_json({"content": "range ça dans Voyages Perso", "device_type": "desktop"})
        confirm = ws.receive_json()

    assert "Voyages Perso" in confirm["full_text"]

    res = client.get("/api/categories", headers={"X-API-Key": TEST_API_KEY})
    assert "Voyages Perso" in res.json()["categories"]


def test_note_saved_with_preselected_category(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "réviser le business plan",
            "device_type": "desktop",
            "mode": "note",
            "category": "Projet",
        })
        ws.receive_json()

    res = client.get("/api/memory/history", headers={"X-API-Key": TEST_API_KEY})
    history = res.json()["history"]
    thought = next(m for m in history if m["content"] == "réviser le business plan")
    assert thought["category"] == "Projet"
