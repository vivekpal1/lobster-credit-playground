"""SQLite connection helper and schema migration."""

import sqlite3
from app.config import LEDGER_DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id           TEXT PRIMARY KEY,
    balance      INTEGER NOT NULL DEFAULT 0,
    credit_limit INTEGER NOT NULL DEFAULT 10,
    reputation   INTEGER NOT NULL DEFAULT 500
);

CREATE TABLE IF NOT EXISTS transactions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id    TEXT NOT NULL,
    to_id      TEXT NOT NULL,
    amount     INTEGER NOT NULL,
    memo       TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(LEDGER_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist and seed agent accounts."""
    conn = get_conn()
    conn.executescript(SCHEMA)

    # Seed the three agent accounts with starting balances.
    agents = [
        ("lobster_red", 100, 0, 500),
        ("lobster_yellow", 100, 0, 500),
        ("lobster_green", 10000, 0, 500),  # bank starts with reserves
    ]
    for aid, bal, cl, rep in agents:
        conn.execute(
            "INSERT OR IGNORE INTO accounts (id, balance, credit_limit, reputation) VALUES (?, ?, ?, ?)",
            (aid, bal, cl, rep),
        )
    conn.commit()
    conn.close()
