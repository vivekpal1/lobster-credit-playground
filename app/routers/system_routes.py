"""System routes — health check and Solana settlement."""

from fastapi import APIRouter
from app.services.solana_settlement import settle

router = APIRouter(tags=["system"])


@router.get("/")
def root():
    return {"status": "ok", "service": "lobster-credit-playground"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/settle")
async def do_settle():
    return await settle()
