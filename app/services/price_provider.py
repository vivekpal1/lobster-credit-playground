"""Thin wrapper around CoinGecko simple-price API (free, no key needed)."""

from datetime import datetime, timezone
import httpx

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

# Map shorthand symbols to CoinGecko ids.
SYMBOL_MAP = {
    "btc": "bitcoin",
    "eth": "ethereum",
}

ALLOWED_SYMBOLS = set(SYMBOL_MAP.keys())


async def get_price(symbol: str) -> dict:
    symbol = symbol.lower()
    if symbol not in SYMBOL_MAP:
        return {"error": f"Unsupported symbol '{symbol}'. Allowed: {', '.join(ALLOWED_SYMBOLS)}"}

    cg_id = SYMBOL_MAP[symbol]
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(COINGECKO_URL, params={"ids": cg_id, "vs_currencies": "usd"})
        resp.raise_for_status()
        data = resp.json()

    price = data.get(cg_id, {}).get("usd")
    if price is None:
        return {"error": "Price data unavailable."}

    return {
        "symbol": symbol.upper(),
        "price_usd": price,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
