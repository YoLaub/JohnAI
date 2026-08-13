import io
import os

TEST_API_KEY = os.environ["API_KEY"]


def test_transcribe_returns_no_speech_on_tiny_or_silent_audio(client, auth_headers):
    """Audio below minimum size threshold or containing no voice should return status 'no_speech'
    instead of saving false dummy notes."""
    tiny_audio = io.BytesIO(b"\x00" * 10)

    response = client.post(
        "/api/transcribe",
        headers=auth_headers,
        files={"file": ("note.wav", tiny_audio, "audio/wav")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "no_speech"
    assert body["text"] == ""

