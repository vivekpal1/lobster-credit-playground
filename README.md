# Lobster Credit Playground

A minimal demo of a **three-agent AI credit economy**, deployed as a single container on Render.

Inside the container, **OpenClaw** and **FastAPI** both run:

- **OpenClaw** handles Telegram bots, LLM calls (via OpenRouter), and agent logic.
- **FastAPI** is a pure HTTP tool backend (ledger, price data, settlement).

OpenClaw agents call FastAPI tools at `http://127.0.0.1:8000` (localhost inside the container).

| Agent | Role | What it does |
|-------|------|-------------|
| **Lobster Red** | Data provider | Fetches live BTC/ETH prices |
| **Lobster Yellow** | Analyst | Interprets price data, charges 2 credits per analysis |
| **Lobster Green** | Bank | Manages accounts, issues starter credits, shows stats |

---

## Architecture

```
                    Telegram Group
                   (users chat here)
                         |
          +--------------+--------------+
          |              |              |
      Red Bot      Yellow Bot      Green Bot
          |              |              |
  ========|==============|==============|========  single Render container
  |       +--------------+--------------+       |
  |                      |                      |
  |               OpenClaw Gateway              |
  |         (agents + LLM via OpenRouter)       |
  |                      |                      |
  |              http://127.0.0.1:8000          |
  |                      |                      |
  |               FastAPI Backend               |
  |            |       |       |                |
  |        /data/*  /ledger/*  /settle          |
  |       (CoinGecko) (SQLite) (Solana devnet)  |
  ==============================================
```

### Credit Flow

1. User tells **Green**: "start" -> Green calls `/ledger/issue_credit` -> user gets 50 credits.
2. User tells **Red**: "btc price" -> Red calls `/data/price?symbol=btc` -> returns price.
3. User tells **Yellow**: "analyze btc" -> Yellow:
   - Calls `/data/price?symbol=btc` to get data.
   - Delivers structured analysis.
   - Calls `/ledger/transfer` to charge user 2 credits.
   - Calls `/ledger/transfer` to pay Red 1 credit for data.
4. User tells **Green**: "balance" -> Green calls `/ledger/balance` -> shows balance.
5. User tells **Green**: "agents" -> Green calls `/ledger/agent_stats` -> shows all stats.

---

## Deploy on Render

### 1. Create a Web Service

- Connect your GitHub repo.
- **Environment**: Docker.
- **Branch**: `main` (or your deploy branch).
- **Health check path**: `/health`

### 2. Set environment variables in Render dashboard

| Variable | Value |
|----------|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `OPENROUTER_MODEL` | `meta-llama/llama-3.1-8b-instruct:free` (or any model) |
| `TELEGRAM_BOT_TOKEN_RED` | Token from @BotFather for Red bot |
| `TELEGRAM_BOT_TOKEN_YELLOW` | Token from @BotFather for Yellow bot |
| `TELEGRAM_BOT_TOKEN_GREEN` | Token from @BotFather for Green bot |

Optional:

| Variable | Default | Description |
|----------|---------|-------------|
| `SOLANA_RPC_URL` | `https://api.devnet.solana.com` | For /settle |
| `SOLANA_SETTLEMENT_PRIVATE_KEY` | - | Keypair for settlement |
| `LEDGER_DB_PATH` | `/app/data/ledger.db` | SQLite path |

### 3. Deploy

Render builds the Docker image and starts both OpenClaw + FastAPI via `entrypoint.sh`.

### 4. Set up Telegram

1. Create a Telegram group (e.g. "Lobster Economy").
2. Add all three bots to the group.
3. Make each bot an admin (so they can read group messages).
4. Start chatting!

---

## Telegram Commands

Address each agent by name in the group:

| Command | Agent | What happens |
|---------|-------|-------------|
| `Green: start` | Green | Creates your account + 50 starter credits |
| `Green: balance` | Green | Shows your credit balance |
| `Green: agents` | Green | Shows all agent stats |
| `Red: btc price` | Red | Returns current BTC price in USD |
| `Red: eth price` | Red | Returns current ETH price in USD |
| `Yellow: analyze btc` | Yellow | Analyzes BTC, charges 2 credits |
| `Yellow: analyze eth` | Yellow | Analyzes ETH, charges 2 credits |

---

## What Runs Where

| Component | Process | Responsibility |
|-----------|---------|---------------|
| **OpenClaw Gateway** | Background process | Telegram bots, LLM (OpenRouter), agent personas, tool routing |
| **FastAPI** | Foreground process | HTTP endpoints: ledger, prices, health, settlement |

OpenClaw calls FastAPI at `http://127.0.0.1:8000` (localhost, same container).

FastAPI has **no** Telegram code and **no** LLM code. It's a pure tool backend.

---

## API Reference

### Data

| Method | Path | Description |
|--------|------|-------------|
| GET | `/data/price?symbol=btc` | BTC or ETH price from CoinGecko |

### Ledger

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ledger/account` | Create account |
| GET | `/ledger/balance?user_id=...` | Get balance |
| POST | `/ledger/transfer` | Transfer credits |
| POST | `/ledger/issue_credit` | Issue credits from Green |
| GET | `/ledger/agent_stats` | Stats for all 3 agents |

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (use for Render) |
| POST | `/settle` | Solana devnet settlement demo |

---

## Environment Variables

All set via the Render dashboard (or `.env` for local dev).

| Variable | Required | Default | Used By |
|----------|----------|---------|---------|
| `OPENROUTER_API_KEY` | Yes | - | OpenClaw |
| `OPENROUTER_MODEL` | No | `meta-llama/llama-3.1-8b-instruct:free` | OpenClaw |
| `TELEGRAM_BOT_TOKEN_RED` | Yes | - | OpenClaw |
| `TELEGRAM_BOT_TOKEN_YELLOW` | Yes | - | OpenClaw |
| `TELEGRAM_BOT_TOKEN_GREEN` | Yes | - | OpenClaw |
| `LEDGER_DB_PATH` | No | `/app/data/ledger.db` | FastAPI |
| `SOLANA_RPC_URL` | No | `https://api.devnet.solana.com` | FastAPI |
| `SOLANA_SETTLEMENT_PRIVATE_KEY` | No | - | FastAPI |
| `PORT` | No | `8000` | FastAPI (Render sets this) |

---

## Local Development

```bash
# Install Python deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, install and start OpenClaw
npm install -g openclaw
export TELEGRAM_BOT_TOKEN_RED="..."
export TELEGRAM_BOT_TOKEN_YELLOW="..."
export TELEGRAM_BOT_TOKEN_GREEN="..."
export OPENROUTER_API_KEY="..."
openclaw gateway --port 18789 --verbose
```

---

## Project Structure

```
lobster-credit-playground/
  README.md
  Dockerfile              # Installs Node.js + OpenClaw + Python + FastAPI
  entrypoint.sh           # Starts OpenClaw (background) + FastAPI (foreground)
  requirements.txt
  .env.example

  app/                    # FastAPI — pure HTTP tool backend
    main.py
    config.py
    db.py
    ledger.py
    models.py
    routers/
      ledger_routes.py
      data_routes.py
      system_routes.py
    services/
      price_provider.py
      solana_settlement.py

  openclaw/               # OpenClaw config + agent definitions
    openclaw.config.json  # 3 agents, 3 Telegram bots, OpenRouter model
    souls/
      lobster_red_soul.md
      lobster_yellow_soul.md
      lobster_green_soul.md
    skills/
      lobster_red_skills.md
      lobster_yellow_skills.md
      lobster_green_skills.md
```

---

## Solana Settlement Demo

```bash
curl -X POST https://your-app.onrender.com/settle
```

Returns a transaction signature and Solana Explorer link. See the previous README section for devnet wallet setup.

---

## License

MIT
