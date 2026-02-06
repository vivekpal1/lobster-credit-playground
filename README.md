# Lobster Credit Playground 🦞

A minimal, end-to-end demo of a **three-agent AI economy** where AI agents share a credit ledger, charge each other for services, and optionally settle balances on Solana devnet.

**Agents:**

| Agent | Role | What it does |
|-------|------|-------------|
| **Lobster Red** | Data provider | Fetches live BTC/ETH prices |
| **Lobster Yellow** | Analyst | Interprets price data, charges 2 credits per analysis |
| **Lobster Green** | Bank | Manages accounts, issues starter credits, shows stats |

**Stack:** Python/FastAPI (ledger API) + OpenClaw (agent gateway) + OpenRouter (LLM) + Telegram (chat UI) + Solana devnet (settlement demo).

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Telegram Group                     │
│                                                      │
│  User: "Red: btc price"                              │
│  User: "Yellow: analyze btc"                         │
│  User: "Green: balance"                              │
└──────────┬──────────┬──────────┬────────────────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼───┐ ┌───▼──────┐
    │ Red Bot │ │Yellow Bot│ │Green Bot │  (3 Telegram bots)
    └──────┬──┘ └─────┬───┘ └───┬──────┘
           │          │          │
    ┌──────▼──────────▼──────────▼──────┐
    │          OpenClaw Gateway          │
    │  (routes messages → agents,        │
    │   agents use skills to call API)   │
    │                                    │
    │  Model provider: OpenRouter        │
    └──────────────┬────────────────────┘
                   │ HTTP (skills use web_fetch)
    ┌──────────────▼────────────────────┐
    │     Ledger API (FastAPI)          │
    │                                    │
    │  /data/price     → CoinGecko      │
    │  /ledger/*       → SQLite         │
    │  /settle         → Solana devnet  │
    └───────────────────────────────────┘
```

### Credit Flow

1. User tells **Green**: "start" → Green creates account, issues 50 starter credits.
2. User tells **Red**: "btc price" → Red fetches price from `/data/price`, returns it free.
3. User tells **Yellow**: "analyze btc" → Yellow:
   - Fetches price from `/data/price`.
   - Delivers structured analysis.
   - Charges user 2 credits → `POST /ledger/transfer` (user → Yellow).
   - Pays Red 1 credit for data → `POST /ledger/transfer` (Yellow → Red).
4. User tells **Green**: "balance" → Green shows current balance.
5. User tells **Green**: "agents" → Green shows all agent stats.

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
# Edit .env with your actual values:
#   OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN_RED/YELLOW/GREEN, etc.
```

### 3. Start the Ledger API

```bash
python -m app.main
# Or:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API auto-creates the SQLite database and seeds agent accounts on first start.

Verify it's running:
```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl "http://localhost:8000/data/price?symbol=btc"
# {"symbol":"BTC","price_usd":97432.10,"timestamp":"..."}
```

### 4. Install and configure OpenClaw

```bash
npm install -g openclaw
openclaw setup
```

During setup, select **OpenRouter** as the model provider and enter your API key.

Then copy/symlink the config and workspace files:

```bash
# Copy the config (or merge into your existing ~/.openclaw/openclaw.json)
cp openclaw/openclaw.config.json ~/.openclaw/openclaw.json

# Create workspace directories for each agent
mkdir -p ~/.openclaw/workspaces/{red,yellow,green}/skills

# Copy skills into each agent's workspace
cp -r openclaw/skills/lobster-red   ~/.openclaw/workspaces/red/skills/
cp -r openclaw/skills/lobster-yellow ~/.openclaw/workspaces/yellow/skills/
cp -r openclaw/skills/lobster-green  ~/.openclaw/workspaces/green/skills/

# Copy soul files into agent directories
mkdir -p ~/.openclaw/agents/{lobster_red,lobster_yellow,lobster_green}
cp openclaw/souls/lobster_red_soul.md    ~/.openclaw/agents/lobster_red/SOUL.md
cp openclaw/souls/lobster_yellow_soul.md ~/.openclaw/agents/lobster_yellow/SOUL.md
cp openclaw/souls/lobster_green_soul.md  ~/.openclaw/agents/lobster_green/SOUL.md
```

**Important:** Edit `~/.openclaw/openclaw.json` and replace the `${...}` placeholders with your actual bot tokens (or export them as environment variables before starting OpenClaw).

### 5. Start OpenClaw

```bash
# Export tokens if not hardcoded in config:
export TELEGRAM_BOT_TOKEN_RED="your-red-token"
export TELEGRAM_BOT_TOKEN_YELLOW="your-yellow-token"
export TELEGRAM_BOT_TOKEN_GREEN="your-green-token"
export OPENROUTER_API_KEY="your-openrouter-key"
export LEDGER_API_BASE="http://localhost:8000"

openclaw start
```

### 6. Set up Telegram

1. Create a Telegram group (e.g. "Lobster Economy Test").
2. Add all three bots to the group.
3. Make each bot an admin (so they can read messages).
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

### Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/data/price?symbol=btc` | Fetch BTC or ETH price |

### Ledger

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ledger/account` | Create a new account |
| GET | `/ledger/balance?user_id=...` | Get account balance |
| POST | `/ledger/transfer` | Transfer credits between accounts |
| POST | `/ledger/issue_credit` | Issue credits from Green's reserves |
| GET | `/ledger/agent_stats` | Get stats for all three agents |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/settle` | Trigger Solana devnet settlement |

---

## Solana Settlement Demo

The `/settle` endpoint sends a real transaction on Solana devnet to demonstrate that off-chain credit balances can be bridged to an on-chain ledger.

### Setup

1. Install the Solana CLI: https://docs.solanalabs.com/cli/install

2. Generate a devnet keypair:
   ```bash
   solana-keygen new --outfile ~/.config/solana/devnet-treasury.json
   solana config set --url devnet
   ```

3. Fund it with devnet SOL:
   ```bash
   solana airdrop 2 --keypair ~/.config/solana/devnet-treasury.json
   ```

4. Add the private key to `.env`:
   ```bash
   # Copy the JSON array from the keypair file:
   SOLANA_SETTLEMENT_PRIVATE_KEY=[1,2,3,...,64 bytes]
   ```

### Trigger Settlement

```bash
curl -X POST http://localhost:8000/settle
```

Response:
```json
{
  "ok": true,
  "message": "Settlement proof sent. Memo: lobster_red: balance=103 | ...",
  "tx_signature": "5Uj3...",
  "explorer_url": "https://explorer.solana.com/tx/5Uj3...?cluster=devnet"
}
```

Open the `explorer_url` in a browser to see the transaction on Solana Explorer.

---

## Docker

### Build and run

```bash
docker build -t lobster-credit-playground .
docker run -p 8000:8000 --env-file .env lobster-credit-playground
```

### Or use docker-compose

```bash
docker compose up --build
```

This starts only the Ledger API. OpenClaw still needs to run separately (it manages the Telegram bots and LLM connections).

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | — | OpenRouter API key |
| `OPENROUTER_MODEL` | No | `meta-llama/llama-3.1-8b-instruct:free` | LLM model to use |
| `TELEGRAM_BOT_TOKEN_RED` | Yes | — | Telegram token for Lobster Red |
| `TELEGRAM_BOT_TOKEN_YELLOW` | Yes | — | Telegram token for Lobster Yellow |
| `TELEGRAM_BOT_TOKEN_GREEN` | Yes | — | Telegram token for Lobster Green |
| `SOLANA_RPC_URL` | No | `https://api.devnet.solana.com` | Solana RPC endpoint |
| `SOLANA_SETTLEMENT_PRIVATE_KEY` | No | — | Base58 or JSON keypair for settlement |
| `LEDGER_DB_PATH` | No | `./ledger.db` | Path to SQLite database file |
| `LEDGER_API_BASE` | No | `http://localhost:8000` | Base URL skills use to reach the API |

---

## Design Decisions

- **SQLite** instead of Postgres: simplest possible thing for a demo. The schema is compatible with Postgres if you want to swap later.
- **CoinGecko free API**: no key needed, rate-limited but fine for a demo.
- **OpenClaw skills** use `web_fetch` (built-in tool) to call the HTTP service. This avoids needing custom JavaScript tooling.
- **Settlement** sends a self-transfer of 5000 lamports on devnet. It's a proof-of-concept, not real accounting. The transaction exists on-chain and can be verified.
- **Credit flow** is intentionally simple: Green is the bank with 10,000 reserves, Yellow charges 2 and pays Red 1. No interest, no complex accounting.

---

## License

MIT
