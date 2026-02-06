# Lobster Credit Playground

A minimal demo of a **three-agent AI credit economy**.

Three AI agents ("lobsters") live in a Telegram group, share a credit ledger, charge each other for services, and can settle balances on Solana devnet.

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
          +--------------+--------------+
                         |
                  OpenClaw Gateway          <-- runs separately
                  (agents + LLM via OpenRouter)
                         |
                    HTTP calls              <-- skills use web_fetch / curl
                         |
                  FastAPI Backend           <-- this repo, deployed on Render/etc.
                  |       |       |
              /data/*  /ledger/*  /settle
              (CoinGecko) (SQLite)  (Solana devnet)
```

**Key separation:**
- **FastAPI** = pure HTTP tool backend. No Telegram, no LLM calls.
- **OpenClaw** = owns all agent logic, Telegram integration, and LLM (via OpenRouter). Runs as a separate process.

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

## Setup

### Prerequisites

- Python 3.11+
- Node.js 22+ (for OpenClaw)
- Three Telegram bot tokens (from [@BotFather](https://t.me/BotFather))
- An [OpenRouter](https://openrouter.ai/) API key

### 1. Clone and install

```bash
git clone https://github.com/vivekpal1/lobster-credit-playground.git
cd lobster-credit-playground

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Start the FastAPI backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API auto-creates the SQLite database and seeds agent accounts on first start.

### 4. Verify the backend works

```bash
# Health check
curl http://localhost:8000/health
# -> {"status":"ok"}

# Price endpoint
curl "http://localhost:8000/data/price?symbol=btc"
# -> {"symbol":"BTC","price_usd":65634.0,"timestamp":"2026-02-06T..."}

# Issue starter credits
curl -X POST http://localhost:8000/ledger/issue_credit \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "amount": 50}'
# -> {"ok":true,"message":"Transfer complete.","tx_id":1}

# Check balance
curl "http://localhost:8000/ledger/balance?user_id=test123"
# -> {"id":"test123","balance":50,"credit_limit":10,"reputation":500}

# Transfer credits
curl -X POST http://localhost:8000/ledger/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_id":"test123","to_id":"lobster_yellow","amount":2,"memo":"test"}'
# -> {"ok":true,"message":"Transfer complete.","tx_id":2}

# Agent stats
curl http://localhost:8000/ledger/agent_stats
# -> [{"id":"lobster_red","balance":100,...}, ...]
```

### 5. Install and configure OpenClaw

```bash
npm install -g openclaw
openclaw setup
```

During setup, select **OpenRouter** as the model provider and enter your API key.

Then copy the config and skill/soul files:

```bash
# Copy the config
cp openclaw/openclaw.config.json ~/.openclaw/openclaw.json

# Create workspace directories for each agent
mkdir -p ~/.openclaw/workspaces/{red,yellow,green}/skills

# Copy skills into each agent's workspace
cp openclaw/skills/lobster_red_skills.md    ~/.openclaw/workspaces/red/skills/SKILL.md
cp openclaw/skills/lobster_yellow_skills.md ~/.openclaw/workspaces/yellow/skills/SKILL.md
cp openclaw/skills/lobster_green_skills.md  ~/.openclaw/workspaces/green/skills/SKILL.md

# Copy soul files into agent directories
mkdir -p ~/.openclaw/agents/{lobster_red,lobster_yellow,lobster_green}
cp openclaw/souls/lobster_red_soul.md    ~/.openclaw/agents/lobster_red/SOUL.md
cp openclaw/souls/lobster_yellow_soul.md ~/.openclaw/agents/lobster_yellow/SOUL.md
cp openclaw/souls/lobster_green_soul.md  ~/.openclaw/agents/lobster_green/SOUL.md
```

Edit `~/.openclaw/openclaw.json` and replace `${...}` placeholders with your actual values, or export them as environment variables.

### 6. Start OpenClaw

```bash
export TELEGRAM_BOT_TOKEN_RED="7986130620:AAE..."
export TELEGRAM_BOT_TOKEN_YELLOW="7691960881:AAH..."
export TELEGRAM_BOT_TOKEN_GREEN="8280137496:AAE..."
export OPENROUTER_API_KEY="sk-or-v1-..."
export BACKEND_URL="http://localhost:8000"  # or your Render URL

openclaw start --config ./openclaw/openclaw.config.json
```

### 7. Set up Telegram

1. Create a Telegram group (e.g. "Lobster Economy").
2. Add all three bots to the group.
3. Make each bot an admin (so they can read group messages).
4. Start chatting!

---

## Telegram Commands

In the group, address each agent by name:

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

## API Reference

All endpoints are on the FastAPI backend. OpenClaw agents call these via HTTP.

### Data

| Method | Path | Description | Example |
|--------|------|-------------|---------|
| GET | `/data/price?symbol=btc` | BTC or ETH price | `{"symbol":"BTC","price_usd":97432.10,"timestamp":"..."}` |

### Ledger

| Method | Path | Body | Description |
|--------|------|------|-------------|
| POST | `/ledger/account` | `{"id":"...","initial_balance":0,"credit_limit":10,"reputation":500}` | Create account |
| GET | `/ledger/balance?user_id=...` | - | Get balance |
| POST | `/ledger/transfer` | `{"from_id":"...","to_id":"...","amount":2,"memo":"..."}` | Transfer credits |
| POST | `/ledger/issue_credit` | `{"user_id":"...","amount":50}` | Issue credits from Green |
| GET | `/ledger/agent_stats` | - | Stats for all 3 agents |

### System

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/settle` | Solana devnet settlement demo |

---

## Environment Variables

### FastAPI backend (set in `.env` or cloud dashboard)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LEDGER_DB_PATH` | No | `./ledger.db` | Path to SQLite database |
| `SOLANA_RPC_URL` | No | `https://api.devnet.solana.com` | Solana RPC endpoint |
| `SOLANA_SETTLEMENT_PRIVATE_KEY` | No | - | Keypair for /settle |
| `PORT` | No | `8000` | Server port |

### OpenClaw (export before running `openclaw start`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | OpenRouter API key |
| `OPENROUTER_MODEL` | No | LLM model (default: `meta-llama/llama-3.1-8b-instruct:free`) |
| `TELEGRAM_BOT_TOKEN_RED` | Yes | Telegram token for Red bot |
| `TELEGRAM_BOT_TOKEN_YELLOW` | Yes | Telegram token for Yellow bot |
| `TELEGRAM_BOT_TOKEN_GREEN` | Yes | Telegram token for Green bot |
| `BACKEND_URL` | Yes | URL of FastAPI backend (e.g. `http://localhost:8000`) |

---

## Solana Settlement Demo

The `/settle` endpoint sends a real transaction on Solana devnet as proof that off-chain balances can be bridged on-chain.

### Setup

1. Install Solana CLI: https://docs.solanalabs.com/cli/install
2. Generate a devnet keypair:
   ```bash
   solana-keygen new --outfile ~/.config/solana/devnet-treasury.json
   solana config set --url devnet
   ```
3. Fund it:
   ```bash
   solana airdrop 2 --keypair ~/.config/solana/devnet-treasury.json
   ```
4. Set in `.env`:
   ```
   SOLANA_SETTLEMENT_PRIVATE_KEY=[1,2,3,...,64 bytes from keypair file]
   ```

### Trigger

```bash
curl -X POST http://localhost:8000/settle
```

Returns a transaction signature and Solana Explorer link.

---

## Docker

```bash
docker build -t lobster-credit-playground .
docker run -p 8000:8000 --env-file .env lobster-credit-playground
```

This runs only the FastAPI backend. OpenClaw runs separately.

---

## Project Structure

```
lobster-credit-playground/
  README.md
  Dockerfile
  requirements.txt
  .env.example

  app/
    main.py              # FastAPI entrypoint
    config.py            # env vars (only what FastAPI needs)
    db.py                # SQLite schema + seeding
    ledger.py            # credit ledger logic
    models.py            # Pydantic models
    routers/
      ledger_routes.py   # /ledger/* endpoints
      data_routes.py     # /data/* endpoints
      system_routes.py   # /health, /settle
    services/
      price_provider.py  # CoinGecko wrapper
      solana_settlement.py

  openclaw/
    openclaw.config.json # 3-agent config for OpenClaw
    souls/
      lobster_red_soul.md
      lobster_yellow_soul.md
      lobster_green_soul.md
    skills/
      lobster_red_skills.md
      lobster_yellow_skills.md
      lobster_green_skills.md
```

No Telegram bot code in FastAPI. No LLM calls in FastAPI. OpenClaw handles all of that.

---

## License

MIT
