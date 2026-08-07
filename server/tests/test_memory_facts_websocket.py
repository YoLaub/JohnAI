import os

TEST_API_KEY = os.environ["API_KEY"]


def test_remember_command_stores_a_fact_and_confirms(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "retiens que mon plat préféré est le tajine", "device_type": "desktop"})
        msg = ws.receive_json()

    assert msg["type"] == "done"
    assert "mon plat préféré est le tajine" in msg["full_text"]


def test_forget_command_removes_a_previously_remembered_fact(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "retiens que je déteste les lundis", "device_type": "desktop"})
        ws.receive_json()

        ws.send_json({"content": "oublie que je déteste les lundis", "device_type": "desktop"})
        forget_msg = ws.receive_json()

    assert forget_msg["type"] == "done"
    assert "oublié" in forget_msg["full_text"]
    assert "je déteste les lundis" in forget_msg["full_text"]


def test_forget_command_reports_when_nothing_matches(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "oublie que ceci n'a jamais été mémorisé xyz123", "device_type": "desktop"})
        msg = ws.receive_json()

    assert msg["type"] == "done"
    assert "Aucun fait" in msg["full_text"]
