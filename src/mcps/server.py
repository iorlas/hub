from contextlib import asynccontextmanager

from fastapi import FastAPI

from mcps.servers.jackett import mcp as jackett_mcp
from mcps.servers.tmdb import mcp as tmdb_mcp
from mcps.servers.transmission import mcp as transmission_mcp

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

    from mcps.config import settings

    uvicorn.run(app, host=settings.host, port=settings.port)
