import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

os.environ.setdefault("DB_PATH", os.path.join(tempfile.mkdtemp(), "test_johnai_memory.db"))
os.environ.setdefault("OLLAMA_URL", "http://127.0.0.1:1")  # unreachable on purpose, keeps tests offline
os.environ.setdefault("GEMINI_API_KEY", "")

TEST_API_KEY = "test-secret-key"
os.environ.setdefault("API_KEY", TEST_API_KEY)

import pytest
from fastapi.testclient import TestClient
from server.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers():
    return {"X-API-Key": TEST_API_KEY}
