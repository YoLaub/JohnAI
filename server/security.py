import os
import re
import secrets

from fastapi import Header, HTTPException

# Shared secret protecting every non-public route: every JohnAi device (Mac,
# Windows, Android app) sends it as `X-API-Key` header, or `?api_key=` for the
# websocket which can't set custom headers from a browser.
API_KEY = os.getenv("API_KEY", "")
if not API_KEY:
    print("⚠️  API_KEY n'est pas configurée : toutes les routes protégées renverront 401/refuseront la connexion.")


def require_api_key(x_api_key: str = Header(default="")):
    if not API_KEY or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Clé API manquante ou invalide")


def check_websocket_api_key(supplied_key: str) -> bool:
    return bool(API_KEY) and secrets.compare_digest(supplied_key, API_KEY)


def sanitize_filename(filename: str) -> str:
    """Strip any directory components / traversal so uploads stay inside UPLOAD_DIR."""
    name = os.path.basename(filename or "").replace("\\", "_")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name).lstrip(".")
    return name or "upload"
