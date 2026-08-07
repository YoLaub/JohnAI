import io
import os

TEST_API_KEY = os.environ["API_KEY"]


def test_transcribe_falls_back_gracefully_on_tiny_audio(client, auth_headers):
    """Regression: the fallback text in /api/transcribe used `datetime.now()`
    without importing `datetime`, raising NameError whenever Whisper produced
    no transcription (e.g. a too-small audio blob)."""
    tiny_audio = io.BytesIO(b"\x00" * 10)  # below the 200-byte transcription threshold

    response = client.post(
        "/api/transcribe",
        headers=auth_headers,
        files={"file": ("note.wav", tiny_audio, "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "transcribed"
    assert body["text"]
