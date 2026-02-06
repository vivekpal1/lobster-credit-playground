---
name: lobster-green-tools
description: HTTP tools for Lobster Green to manage accounts, balances, and credits via the backend API.
---

# Lobster Green Tools

You have three tools. The backend runs at http://127.0.0.1:8000.

## get_balance

Looks up a user's account balance, credit limit, and reputation.

**When to use:** When a user asks for their balance.

**How:**

```bash
curl "http://127.0.0.1:8000/ledger/balance?user_id=<USER_ID>"
```

**Example response:**
```json
{
  "id": "123456789",
  "balance": 48,
  "credit_limit": 10,
  "reputation": 500
}
```

**On 404:** The user doesn't have an account yet. Tell them to say `/start`.

## issue_credit

Creates a new user account (if needed) and issues starter credits from Green's reserves.

**When to use:** When a user says `/start` or `start` for the first time.

**How:**

```bash
curl -X POST "http://127.0.0.1:8000/ledger/issue_credit" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<USER_ID>", "amount": 50}'
```

**Important:**
- Always issue exactly **50** starter credits.
- Before issuing, check if the user already has an account via `get_balance`.
  If they do, just show their current balance instead of issuing again.

**Example response:**
```json
{"ok": true, "message": "Transfer complete.", "tx_id": 1}
```

## get_agent_stats

Returns balance and transaction stats for all three lobster agents.

**When to use:** When a user asks for "agents", "stats", or "agent stats".

**How:**

```bash
curl "http://127.0.0.1:8000/ledger/agent_stats"
```

**Example response:**
```json
[
  {"id": "lobster_red", "balance": 103, "total_earned": 15, "total_spent": 12},
  {"id": "lobster_yellow", "balance": 108, "total_earned": 22, "total_spent": 14},
  {"id": "lobster_green", "balance": 9850, "total_earned": 0, "total_spent": 150}
]
```

Format this as a clean list when replying to the user.
