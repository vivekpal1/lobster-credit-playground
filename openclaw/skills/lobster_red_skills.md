---
name: lobster-red-tools
description: HTTP tools for Lobster Red to fetch cryptocurrency prices from the backend API.
---

# Lobster Red Tools

You have one tool: fetching live crypto prices from the backend at http://127.0.0.1:8000.

## get_price

Fetches the current USD price of a cryptocurrency.

**When to use:** Whenever someone asks for the price of BTC or ETH.

**How:**

```bash
curl "http://127.0.0.1:8000/data/price?symbol=<SYMBOL>"
```

- Replace `<SYMBOL>` with `btc` or `eth` (lowercase).
- Only `btc` and `eth` are supported.

**Example request:**
```
GET http://127.0.0.1:8000/data/price?symbol=btc
```

**Example response:**
```json
{
  "symbol": "BTC",
  "price_usd": 97432.10,
  "timestamp": "2025-01-15T12:34:56+00:00"
}
```

**On error:** If the API returns an error or is unavailable, tell the user the price service is temporarily down and to try again shortly.

## Examples

- User says "btc price" -> call `get_price` with symbol=btc -> reply with formatted price.
- User says "eth price" -> call `get_price` with symbol=eth -> reply with formatted price.
- User says "sol price" -> reply that you only support BTC and ETH.
