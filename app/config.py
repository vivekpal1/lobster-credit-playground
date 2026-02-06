"""Environment configuration — only what FastAPI needs."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- Solana ---------------------------------------------------------------
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
SOLANA_SETTLEMENT_PRIVATE_KEY = os.getenv("SOLANA_SETTLEMENT_PRIVATE_KEY", "")

# --- Ledger DB ------------------------------------------------------------
LEDGER_DB_PATH = os.getenv("LEDGER_DB_PATH", "./ledger.db")

# --- HTTP service ---------------------------------------------------------
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
