"""FastAPI entrypoint — pure HTTP tool backend for OpenClaw agents."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import init_db
from app.routers import ledger_routes, data_routes, system_routes

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Lobster Credit Playground",
    description="HTTP tool backend for three OpenClaw AI agents (Red/Yellow/Green).",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(system_routes.router)
app.include_router(ledger_routes.router)
app.include_router(data_routes.router)


if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
