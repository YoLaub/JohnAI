def test_reformulate_requires_api_key(client):
    res = client.post("/api/reformulate", json={"text": "une idee rapide pas clair"})
    assert res.status_code == 401


def test_reformulate_rejects_empty_text(client, auth_headers):
    res = client.post("/api/reformulate", json={"text": "   "}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "error"


def test_reformulate_falls_back_gracefully_when_llm_unreachable(client, auth_headers):
    """OLLAMA_URL is unreachable-by-design in tests (see conftest.py) — the
    route must not crash, and must hand back something usable rather than a
    500, mirroring the /ws chat handler's fallback behavior."""
    res = client.post(
        "/api/reformulate",
        json={"text": "une idee rapide pas super clair", "device_type": "desktop"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "error"
    assert body["reformulated"] == "une idee rapide pas super clair"
