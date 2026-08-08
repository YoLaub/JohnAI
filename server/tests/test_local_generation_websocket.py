import os

TEST_API_KEY = os.environ["API_KEY"]


def test_desktop_client_is_asked_to_generate_locally(client):
    """A Tauri desktop client (supports_local_generation=true) must not get the
    server's own Gemini/Ollama generation — it gets delegated the raw context
    and generates on-device instead (see client/src/local-ollama.js)."""
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "Bonjour JohnAi",
            "device_type": "desktop",
            "supports_local_generation": True,
        })
        msg = ws.receive_json()

    assert msg["type"] == "generate_locally"
    assert isinstance(msg["messages"], list)
    assert any(m["role"] == "user" and m["content"] == "Bonjour JohnAi" for m in msg["messages"])


def test_local_generation_result_is_saved_and_acknowledged(client, auth_headers):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "Quelle heure est-il ?",
            "device_type": "desktop",
            "supports_local_generation": True,
        })
        ws.receive_json()  # generate_locally

        ws.send_json({"type": "local_generation_result", "content": "Il est 10h."})
        done = ws.receive_json()

    assert done["type"] == "done"
    assert done["full_text"] == "Il est 10h."

    history = client.get("/api/memory/history", headers=auth_headers).json()["history"]
    assert any(m["role"] == "assistant" and m["content"] == "Il est 10h." for m in history)


def test_request_cloud_fallback_falls_back_to_server_generation(client):
    """When local Ollama isn't available on the client, it can bail out and ask
    the server to handle it the old way (Gemini/Ollama unreachable in tests ->
    same graceful fallback text as normal chat)."""
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "Un message quelconque",
            "device_type": "desktop",
            "supports_local_generation": True,
        })
        ws.receive_json()  # generate_locally

        ws.send_json({"type": "request_cloud_fallback"})
        messages = [ws.receive_json() for _ in range(2)]

    done = next(m for m in messages if m["type"] == "done")
    assert done.get("full_text")


def test_android_client_is_never_delegated_local_generation(client):
    """supports_local_generation is a client-side capability flag, but mobile
    must never get the local-generation offer regardless of what it sends —
    battery/architecture rule from CLAUDE.md."""
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({
            "content": "Bonjour",
            "device_type": "android",
            "supports_local_generation": True,
        })
        msg = ws.receive_json()

    assert msg["type"] != "generate_locally"
