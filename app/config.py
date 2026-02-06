"""Environment configuration — all tunables come from env vars."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM -----------------------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

# --- Telegram bot tokens (used only in OpenClaw config, listed here for docs)
TELEGRAM_BOT_TOKEN_RED = os.getenv("TELEGRAM_BOT_TOKEN_RED", "")
TELEGRAM_BOT_TOKEN_YELLOW = os.getenv("TELEGRAM_BOT_TOKEN_YELLOW", "")
TELEGRAM_BOT_TOKEN_GREEN = os.getenv("TELEGRAM_BOT_TOKEN_GREEN", "")

# --- Solana ---------------------------------------------------------------
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
SOLANA_SETTLEMENT_PRIVATE_KEY = os.getenv("SOLANA_SETTLEMENT_PRIVATE_KEY", "")

# --- Ledger DB ------------------------------------------------------------
LEDGER_DB_PATH = os.getenv("LEDGER_DB_PATH", "./ledger.db")

# --- HTTP service ---------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Base URL the OpenClaw skills will use to reach this service.
LEDGER_API_BASE = os.getenv("LEDGER_API_BASE", "http://localhost:8000")
