import os

import pytest
from starlette.websockets import WebSocketDisconnect

TEST_API_KEY = os.environ["API_KEY"]


def test_memory_history_rejects_missing_api_key(client):
    response = client.get("/api/memory/history")
    assert response.status_code == 401


def test_memory_history_accepts_correct_api_key(client, auth_headers):
    response = client.get("/api/memory/history", headers=auth_headers)
    assert response.status_code == 200


def test_memory_history_rejects_wrong_api_key(client):
    response = client.get("/api/memory/history", headers={"X-API-Key": "wrong"})
    assert response.status_code == 401


def test_upload_rejects_missing_api_key(client):
    response = client.post("/api/upload", files={"file": ("note.txt", b"hello", "text/plain")})
    assert response.status_code == 401


def test_upload_accepts_correct_api_key(client, auth_headers):
    response = client.post(
        "/api/upload",
        headers=auth_headers,
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 200


def test_transcribe_rejects_missing_api_key(client):
    response = client.post(
        "/api/transcribe",
        files={"file": ("note.wav", b"\x00" * 10, "audio/wav")},
    )
    assert response.status_code == 401


def test_health_check_does_not_require_api_key(client):
    """Health check stays public so uptime monitors don't need the secret."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_websocket_rejects_missing_api_key(client):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws"):
            pass


def test_websocket_accepts_correct_api_key(client):
    with client.websocket_connect(f"/ws?api_key={TEST_API_KEY}") as ws:
        ws.send_json({"content": "Bonjour", "device_type": "desktop"})
        msg = ws.receive_json()
        assert msg is not None


def test_upload_sanitizes_path_traversal_filename(client, auth_headers, tmp_path, monkeypatch):
    import server.main as main

    monkeypatch.setattr(main, "UPLOAD_DIR", str(tmp_path))

    response = client.post(
        "/api/upload",
        headers=auth_headers,
        files={"file": ("../../evil.txt", b"payload", "text/plain")},
    )

    assert response.status_code == 200
    saved_name = response.json()["filename"]
    assert ".." not in saved_name and "/" not in saved_name
    # the file must have landed inside UPLOAD_DIR, not escaped it
    assert (tmp_path / saved_name).is_file()
    assert not (tmp_path.parent / "evil.txt").exists()
