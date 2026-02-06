---
name: lobster-yellow-tools
description: Analysis tools for Lobster Yellow — fetches data and charges credits via the ledger API.
---

# Lobster Yellow Tools

Tools for fetching price data and managing credit charges for analysis services.

## Available Actions

### Fetch Price Data

Fetch the current USD price of a cryptocurrency (same as Red's tool, used internally).

**When to use:** Before performing an analysis for a user.

**How to use:**

Use `web_fetch` to call:
- URL: `http://localhost:8000/data/price?symbol={symbol}`
- Method: GET
- Symbol must be `btc` or `eth`.

**Response:**
```json
{
  "symbol": "BTC",
  "price_usd": 97432.10,
  "timestamp": "2025-01-15T12:34:56+00:00"
}
```

### Charge User for Analysis

After completing an analysis, charge the user 2 credits.

**When to use:** After delivering analysis results to a user.

**How to use:**

Use `web_fetch` to POST to the transfer endpoint:

```bash
curl -X POST http://localhost:8000/ledger/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_id": "<user_telegram_id>", "to_id": "lobster_yellow", "amount": 2, "memo": "analysis fee"}'
```

- `from_id`: The Telegram user ID of the person requesting analysis.
- `to_id`: Always `"lobster_yellow"`.
- `amount`: Always `2` credits.
- `memo`: Brief description like `"btc analysis fee"`.

If the transfer fails (insufficient balance), inform the user to ask **Green** for starter credits.

### Pay Red for Data

After charging the user, pay Lobster Red 1 credit for the data used.

**When to use:** After every successful analysis charge.

**How to use:**

```bash
curl -X POST http://localhost:8000/ledger/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_id": "lobster_yellow", "to_id": "lobster_red", "amount": 1, "memo": "data fee from Yellow"}'
```

## Workflow

1. Fetch price data for the requested symbol.
2. Perform analysis and write the response.
3. Charge the user 2 credits → `POST /ledger/transfer`.
4. Pay Red 1 credit → `POST /ledger/transfer`.
5. Include the charge info in the response to the user.
