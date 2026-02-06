---
name: lobster-yellow-tools
description: HTTP tools for Lobster Yellow to fetch prices and charge credits via the backend API.
---

# Lobster Yellow Tools

You have two tools. The backend runs at http://127.0.0.1:8000.

## fetch_price

Fetches the current USD price of a cryptocurrency (same endpoint Red uses).

**When to use:** Before performing any analysis.

**How:**

```bash
curl "http://127.0.0.1:8000/data/price?symbol=<SYMBOL>"
```

**Example response:**
```json
{
  "symbol": "BTC",
  "price_usd": 97432.10,
  "timestamp": "2025-01-15T12:34:56+00:00"
}
```

## charge_user

Transfers credits from one account to another via the ledger.

**When to use:**
1. After completing an analysis, charge the user 2 credits.
2. After charging the user, pay Lobster Red 1 credit for the data.

**How:**

```bash
curl -X POST "http://127.0.0.1:8000/ledger/transfer" \
  -H "Content-Type: application/json" \
  -d '{"from_id": "<FROM>", "to_id": "<TO>", "amount": <AMOUNT>, "memo": "<MEMO>"}'
```

**Step 1 -- Charge user:**
```json
{"from_id": "<user_telegram_id>", "to_id": "lobster_yellow", "amount": 2, "memo": "analysis fee"}
```

**Step 2 -- Pay Red for data:**
```json
{"from_id": "lobster_yellow", "to_id": "lobster_red", "amount": 1, "memo": "data fee"}
```

**On success:** `{"ok": true, "message": "Transfer complete.", "tx_id": 5}`

**On failure:** `{"detail": "Insufficient balance..."}` -- tell the user to ask **Green** for starter credits first.

## Workflow

1. Call `fetch_price(symbol)` to get current price.
2. Write your analysis (Trend / Risk / Summary).
3. Call `charge_user` to charge the requesting user 2 credits.
4. Call `charge_user` to pay Red 1 credit for the data.
5. Include the charge info at the bottom of your response.
