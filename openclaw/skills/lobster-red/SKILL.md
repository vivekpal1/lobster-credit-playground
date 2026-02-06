---
name: lobster-red-tools
description: Data tools for Lobster Red — fetches crypto prices from the ledger API.
---

# Lobster Red Tools

Tools for fetching cryptocurrency price data from the Lobster Credit Playground API.

## Available Actions

### Get Price

Fetch the current USD price of a cryptocurrency.

**When to use:** When a user asks for the price of BTC or ETH.

**How to use:**

```bash
curl "${LEDGER_API_BASE:-http://localhost:8000}/data/price?symbol=btc"
```

Replace `btc` with the requested symbol (`btc` or `eth`).

**Response format:**
```json
{
  "symbol": "BTC",
  "price_usd": 97432.10,
  "timestamp": "2025-01-15T12:34:56+00:00"
}
```

**Implementation:**

Use `web_fetch` to call the price endpoint:

- URL: `http://localhost:8000/data/price?symbol={symbol}`
- Method: GET
- The symbol must be `btc` or `eth` (lowercase).

If the API returns an error, tell the user the price service is temporarily unavailable.
