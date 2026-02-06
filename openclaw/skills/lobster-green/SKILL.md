---
name: lobster-green-tools
description: Banking tools for Lobster Green — manages accounts, balances, credits, and agent stats.
---

# Lobster Green Tools

Tools for managing the credit ledger: accounts, balances, issuing credits, and viewing stats.

## Available Actions

### Get User Balance

Look up a user's account balance, credit limit, and reputation.

**When to use:** When a user asks for their balance.

**How to use:**

Use `web_fetch` to call:
- URL: `http://localhost:8000/ledger/balance?user_id={user_telegram_id}`
- Method: GET

**Response:**
```json
{
  "id": "123456789",
  "balance": 48,
  "credit_limit": 10,
  "reputation": 500
}
```

If the account doesn't exist (404), tell the user to run `/start` first.

### Issue Starter Credits

Create an account for a new user and give them 50 starter credits.

**When to use:** When a user says `/start` or `start`.

**How to use:**

Use `web_fetch` to POST:

```bash
curl -X POST http://localhost:8000/ledger/issue_credit \
  -H "Content-Type: application/json" \
  -d '{"user_id": "<user_telegram_id>", "amount": 50}'
```

This automatically creates the account if it doesn't exist and transfers 50 credits from Green's reserves.

**Important:** Only issue starter credits once per user. Check their balance first — if they already have an account, don't issue again.

### Get Agent Stats

Show summary stats for all three lobster agents.

**When to use:** When a user asks for "agents", "stats", or "agent stats".

**How to use:**

Use `web_fetch` to call:
- URL: `http://localhost:8000/ledger/agent_stats`
- Method: GET

**Response:**
```json
[
  {"id": "lobster_red", "balance": 103, "total_earned": 15, "total_spent": 12},
  {"id": "lobster_yellow", "balance": 108, "total_earned": 22, "total_spent": 14},
  {"id": "lobster_green", "balance": 9850, "total_earned": 0, "total_spent": 150}
]
```

### Transfer Credits

Transfer credits between two accounts.

**When to use:** When a user requests a transfer (e.g. "transfer 5 to user123").

**How to use:**

```bash
curl -X POST http://localhost:8000/ledger/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_id": "<sender_id>", "to_id": "<receiver_id>", "amount": <amount>, "memo": "user transfer"}'
```

Check that the amount is positive and reasonable before executing.
