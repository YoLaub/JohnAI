import os

TEST_API_KEY = os.environ["API_KEY"]


def test_chat_message_gets_a_response(client):
    """A plain chat message (not Mode Note) must not crash the websocket handler.

    Regression: `recent_context` was referenced in main.py's websocket handler
    without ever being defined, raising NameError on every non-note message.
    """
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "Bonjour JohnAi", "device_type": "desktop"})
        messages = []
        for _ in range(10):
            msg = ws.receive_json()
            messages.append(msg)
            if msg.get("type") == "done":
                break

    assert any(m.get("type") == "done" for m in messages)
    done = next(m for m in messages if m.get("type") == "done")
    assert done.get("full_text")
