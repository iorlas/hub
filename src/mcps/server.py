from contextlib import asynccontextmanager

from fastapi import FastAPI

from mcps.auth.provider import McpsOAuthProvider
from mcps.config import settings
from mcps.servers.jackett import mcp as jackett_mcp
from mcps.servers.tmdb import mcp as tmdb_mcp
from mcps.servers.transmission import mcp as transmission_mcp

# Create per-server OAuth providers with correct base_url per mount path.
# Each provider needs its own base_url so OAuth metadata advertises endpoints
# at the correct subpath (e.g., /jackett/authorize, not /authorize).
if settings.auth_users:
    users = settings.get_users()
    issuer = settings.auth_issuer.rstrip("/")
    for mcp_instance, mount in [(jackett_mcp, "jackett"), (tmdb_mcp, "tmdb"), (transmission_mcp, "transmission")]:
        mcp_instance.auth = McpsOAuthProvider(
            base_url=f"{issuer}/{mount}",
            users=users,
        )

# Create HTTP apps (auth is read from mcp.auth internally)
jackett_app = jackett_mcp.http_app(path="/")
tmdb_app = tmdb_mcp.http_app(path="/")
transmission_app = transmission_mcp.http_app(path="/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with jackett_app.lifespan(jackett_app):
        async with tmdb_app.lifespan(tmdb_app):
            async with transmission_app.lifespan(transmission_app):
                yield


app = FastAPI(title="mcps", lifespan=lifespan)
app.mount("/jackett", jackett_app)
app.mount("/tmdb", tmdb_app)
app.mount("/transmission", transmission_app)


@app.get("/")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
