try:
    from server.database import list_categories, get_messages_by_category
    from server.mcp_security import McpGateMiddleware
except ModuleNotFoundError:
    from database import list_categories, get_messages_by_category
    from mcp_security import McpGateMiddleware

from mcp.server.mcpserver import MCPServer

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
    for the underlying session manager to actually start."""
    app = mcp.streamable_http_app(streamable_http_path="/", stateless_http=True)
    app.add_middleware(McpGateMiddleware)
    return app
