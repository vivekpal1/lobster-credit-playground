"""Routes for market-data lookups (crypto prices)."""

from fastapi import APIRouter, HTTPException
from app.services.price_provider import get_price, ALLOWED_SYMBOLS

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/price")
async def price(symbol: str):
    symbol = symbol.lower()
    if symbol not in ALLOWED_SYMBOLS:
        raise HTTPException(400, f"Unsupported symbol. Allowed: {', '.join(ALLOWED_SYMBOLS)}")
    result = await get_price(symbol)
    if "error" in result:
        raise HTTPException(502, result["error"])
    return result
