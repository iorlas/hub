"""MCP server apps -- one per service, each with OAuth at root.

Usage:
    uvicorn mcps.server:jackett --host 0.0.0.0 --port 8000
    uvicorn mcps.server:transmission --host 0.0.0.0 --port 8000
    uvicorn mcps.server:tmdb --host 0.0.0.0 --port 8000
    uvicorn mcps.server:storage --host 0.0.0.0 --port 8000
"""

from mcps.auth.provider import McpsOAuthProvider
from mcps.config import settings
from mcps.servers.jackett import mcp as jackett_mcp
from mcps.servers.storage import mcp as storage_mcp
from mcps.servers.tmdb import mcp as tmdb_mcp
from mcps.servers.transmission import mcp as transmission_mcp


def _setup_auth(mcp_instance) -> None:
    """Configure OAuth on an MCP instance if auth is enabled."""
    if not settings.auth_users:
        return
    # AUTH_ISSUER is set per-service in compose to match the service's public domain
    issuer = settings.auth_issuer.rstrip("/")
    mcp_instance.auth = McpsOAuthProvider(
        base_url=issuer,
        users=settings.get_users(),
    )


_setup_auth(jackett_mcp)
_setup_auth(tmdb_mcp)
_setup_auth(transmission_mcp)
_setup_auth(storage_mcp)

# ASGI apps -- uvicorn targets these directly
jackett = jackett_mcp.http_app(path="/")
transmission = transmission_mcp.http_app(path="/")
tmdb = tmdb_mcp.http_app(path="/")
storage = storage_mcp.http_app(path="/")
