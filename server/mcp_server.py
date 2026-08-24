try:
    from server.database import list_categories, get_messages_by_category
    from server.mcp_security import McpGateMiddleware
except ModuleNotFoundError:
    from database import list_categories, get_messages_by_category
    from mcp_security import McpGateMiddleware

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

mcp = MCPServer(
    "JohnAi",
    instructions=(
        "Accès en lecture aux notes personnelles de JohnAi (assistant IA "
        "personnel de l'utilisateur), classées par catégorie."
    ),
)


@mcp.tool()
def list_note_categories() -> list[str]:
    """Liste les catégories de notes existantes dans JohnAi."""
    return list_categories()


@mcp.tool()
def get_notes_by_category(category: str) -> list[dict]:
    """Récupère les notes JohnAi classées dans la catégorie donnée (insensible à la casse)."""
    return get_messages_by_category(category)


def build_mcp_asgi_app():
    """Self-contained Starlette app (auth+rate-limit+logging included) meant
    to be mounted at /mcp — see server/main.py for lifespan wiring, required
    for the underlying session manager to actually start.

    The MCP SDK's own DNS-rebinding protection (transport_security, on by
    default since mcp 2.0.0) rejects every Host with 421 Invalid Host header
    unless allowed_hosts is listed explicitly — it does not fall back to
    "no restriction" just because the app is mounted behind a public domain.
    """
    app = mcp.streamable_http_app(
        streamable_http_path="/",
        stateless_http=True,
        transport_security=TransportSecuritySettings(
            allowed_hosts=["johnai.john-world.store", "localhost", "127.0.0.1"],
            allowed_origins=[
                "https://johnai.john-world.store",
                "http://localhost",
                "http://127.0.0.1",
            ],
        ),
    )
    app.add_middleware(McpGateMiddleware)
    return app
