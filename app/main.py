"""FastAPI entrypoint for the Lobster Credit Playground."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import init_db
from app.routers import ledger_routes, data_routes, system_routes
from app.services.telegram_bots import start_bots, stop_bots

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await start_bots()
    yield
    await stop_bots()


app = FastAPI(
    title="Lobster Credit Playground",
    description="Minimal credit ledger + data API for three AI lobster agents.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(system_routes.router)
app.include_router(ledger_routes.router)
app.include_router(data_routes.router)


if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT

    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
