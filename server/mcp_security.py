import os
import time
import json
import logging
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("johnai.mcp")

# Separate secret from API_KEY (server/security.py) — the REST/websocket key
# and the MCP endpoint are two different exposure surfaces; a leak on one
# shouldn't hand over the other (this repo has had one API_KEY leak already,
# see CLAUDE.md).
MCP_API_KEY = os.getenv("MCP_API_KEY", "")
if not MCP_API_KEY:
    print("⚠️  MCP_API_KEY n'est pas configurée : le serveur MCP refusera toutes les requêtes.")

RATE_LIMIT_CAPACITY = float(os.getenv("MCP_RATE_LIMIT_CAPACITY", "30"))
RATE_LIMIT_REFILL_PER_SEC = float(os.getenv("MCP_RATE_LIMIT_REFILL_PER_SEC", "0.5"))  # ~30/min sustained


class TokenBucket:
    """Capacity + refill-rate token bucket: tolerates bursts, bounds sustained rate."""

    def __init__(self, capacity: float, refill_per_sec: float):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def allow(self) -> bool:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last_refill) * self.refill_per_sec)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


# Singleton, one bucket per resolved identity, created once at module load —
# a bucket recreated per request would make rate-limiting a no-op. Solo
# project: effectively one identity ("owner"), keyed anyway so this survives
# a future second MCP token without a rewrite.
_buckets: dict[str, TokenBucket] = {}


def _bucket_for(identity: str) -> TokenBucket:
    if identity not in _buckets:
        _buckets[identity] = TokenBucket(RATE_LIMIT_CAPACITY, RATE_LIMIT_REFILL_PER_SEC)
    return _buckets[identity]


def extract_rpc_method(body: bytes) -> str:
    if not body:
        return "?"
    try:
        return json.loads(body).get("method", "?")
    except Exception:
        return "?"


class McpGateMiddleware(BaseHTTPMiddleware):
    """Gates the whole /mcp endpoint in one place: bearer auth (identity +
    nothing revealed to an anonymous caller, including tool discovery), then
    per-identity rate-limit, then logs every call — including rejections, so
    a rate-limit hit shows up in the same log stream as a normal tool call
    instead of vanishing silently."""

    async def dispatch(self, request, call_next):
        auth_header = request.headers.get("authorization", "")
        token = auth_header[7:] if auth_header.lower().startswith("bearer ") else ""
        body = await request.body()
        method = extract_rpc_method(body)

        if not MCP_API_KEY or not secrets.compare_digest(token, MCP_API_KEY):
            logger.warning("mcp rejected method=%s reason=auth", method)
            return JSONResponse({"error": "invalid or missing bearer token"}, status_code=401)

        identity = "owner"
        if not _bucket_for(identity).allow():
            logger.warning("mcp rejected identity=%s method=%s reason=rate_limit", identity, method)
            return JSONResponse({"error": "rate limit exceeded"}, status_code=429)

        response = await call_next(request)
        logger.info("mcp call identity=%s method=%s status=%s", identity, method, response.status_code)
        return response
