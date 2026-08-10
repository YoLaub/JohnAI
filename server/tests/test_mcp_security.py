import os
import time

# MCP_API_KEY must already be set by conftest.py before server.mcp_security is
# first imported anywhere (module-level constant, read once at import time —
# same constraint as server/security.py's API_KEY).
try:
    from server.mcp_security import TokenBucket, extract_rpc_method, McpGateMiddleware
except ModuleNotFoundError:
    from mcp_security import TokenBucket, extract_rpc_method, McpGateMiddleware

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

MCP_API_KEY = os.environ.get("MCP_API_KEY", "test-mcp-secret-key")


# --- Pure logic: TokenBucket -------------------------------------------------

def test_token_bucket_allows_up_to_capacity_then_blocks():
    bucket = TokenBucket(capacity=3, refill_per_sec=0)
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_token_bucket_refills_over_time():
    bucket = TokenBucket(capacity=1, refill_per_sec=1000)  # fast refill for the test
    assert bucket.allow() is True
    assert bucket.allow() is False
    time.sleep(0.01)  # 1000/sec refill -> ~10 tokens back well within capacity
    assert bucket.allow() is True


# --- Pure logic: JSON-RPC method extraction ----------------------------------

def test_extract_rpc_method_reads_the_method_field():
    assert extract_rpc_method(b'{"method": "tools/call", "params": {}}') == "tools/call"


def test_extract_rpc_method_falls_back_on_empty_or_malformed_body():
    assert extract_rpc_method(b"") == "?"
    assert extract_rpc_method(b"not json") == "?"


# --- End-to-end: the middleware wraps a dummy downstream app ----------------

def _make_app():
    async def ok(request):
        return JSONResponse({"ok": True})

    app = Starlette(routes=[Route("/mcp", ok, methods=["POST"])])
    app.add_middleware(McpGateMiddleware)
    return app


def test_request_without_token_is_rejected():
    client = TestClient(_make_app())
    response = client.post("/mcp", json={"method": "tools/list"})
    assert response.status_code == 401


def test_request_with_wrong_token_is_rejected():
    client = TestClient(_make_app())
    response = client.post(
        "/mcp", json={"method": "tools/list"},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 401


def test_request_with_correct_token_is_accepted():
    client = TestClient(_make_app())
    response = client.post(
        "/mcp", json={"method": "tools/list"},
        headers={"Authorization": f"Bearer {MCP_API_KEY}"},
    )
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_rate_limit_kicks_in_after_capacity_exhausted(monkeypatch):
    try:
        import server.mcp_security as mcp_security
    except ModuleNotFoundError:
        import mcp_security
    monkeypatch.setattr(mcp_security, "RATE_LIMIT_CAPACITY", 2)
    monkeypatch.setattr(mcp_security, "RATE_LIMIT_REFILL_PER_SEC", 0)
    monkeypatch.setattr(mcp_security, "_buckets", {})

    client = TestClient(_make_app())
    headers = {"Authorization": f"Bearer {MCP_API_KEY}"}
    assert client.post("/mcp", json={"method": "x"}, headers=headers).status_code == 200
    assert client.post("/mcp", json={"method": "x"}, headers=headers).status_code == 200
    assert client.post("/mcp", json={"method": "x"}, headers=headers).status_code == 429
