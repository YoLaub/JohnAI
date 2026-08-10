import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

os.environ.setdefault("DB_PATH", os.path.join(tempfile.mkdtemp(), "test_johnai_memory.db"))
os.environ.setdefault("OLLAMA_URL", "http://127.0.0.1:1")  # unreachable on purpose, keeps tests offline
os.environ.setdefault("GEMINI_API_KEY", "")

TEST_API_KEY = "test-secret-key"
os.environ.setdefault("API_KEY", TEST_API_KEY)
os.environ.setdefault("MCP_API_KEY", "test-mcp-secret-key")

import pytest
from fastapi.testclient import TestClient
from server.main import app


@pytest.fixture(scope="session")
def client():
    # Session-scoped: app's lifespan wires up the MCP session manager
    # (server/mcp_server.py), whose StreamableHTTPSessionManager.run() can only
    # be entered once per process — re-entering per test (function-scoped
    # TestClient) would call it again and raise. Matches how DB_PATH is
    # already a single shared temp file for the whole test session, not reset
    # per test (see the setdefault above) — tests already coexist in shared
    # state and rely on unique content strings for isolation.
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers():
    return {"X-API-Key": TEST_API_KEY}
