"""Core credit-ledger logic — accounts, transfers, stats."""

from app.db import get_conn


def create_account(
    account_id: str,
    initial_balance: int = 0,
    credit_limit: int = 10,
    reputation: int = 500,
) -> dict:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO accounts (id, balance, credit_limit, reputation) VALUES (?, ?, ?, ?)",
            (account_id, initial_balance, credit_limit, reputation),
        )
        conn.commit()
        return {"ok": True, "message": f"Account {account_id} created."}
    except Exception as e:
        return {"ok": False, "message": str(e)}
    finally:
        conn.close()


def get_account(account_id: str) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return dict(row)


def transfer(from_id: str, to_id: str, amount: int, memo: str | None = None) -> dict:
    if amount <= 0:
        return {"ok": False, "message": "Amount must be positive."}

    conn = get_conn()
    try:
        sender = conn.execute("SELECT * FROM accounts WHERE id = ?", (from_id,)).fetchone()
        if sender is None:
            return {"ok": False, "message": f"Sender {from_id} not found."}

        effective_floor = -(sender["credit_limit"])
        if sender["balance"] - amount < effective_floor:
            return {
                "ok": False,
                "message": f"Insufficient balance. {from_id} has {sender['balance']} credits (limit {sender['credit_limit']}).",
            }

        # Ensure receiver exists.
        receiver = conn.execute("SELECT * FROM accounts WHERE id = ?", (to_id,)).fetchone()
        if receiver is None:
            return {"ok": False, "message": f"Receiver {to_id} not found."}

        conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_id))
        conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_id))
        cur = conn.execute(
            "INSERT INTO transactions (from_id, to_id, amount, memo) VALUES (?, ?, ?, ?)",
            (from_id, to_id, amount, memo),
        )
        conn.commit()
        return {"ok": True, "message": "Transfer complete.", "tx_id": cur.lastrowid}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "message": str(e)}
    finally:
        conn.close()


def issue_credit(user_id: str, amount: int) -> dict:
    """Green bank issues credits to a user from its own reserves."""
    return transfer("lobster_green", user_id, amount, memo="starter credit issued by Green")


def get_agent_stats() -> list[dict]:
    conn = get_conn()
    agents = ["lobster_red", "lobster_yellow", "lobster_green"]
    results = []
    for aid in agents:
        row = conn.execute("SELECT * FROM accounts WHERE id = ?", (aid,)).fetchone()
        balance = row["balance"] if row else 0

        earned = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE to_id = ?",
            (aid,),
        ).fetchone()["total"]

        spent = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE from_id = ?",
            (aid,),
        ).fetchone()["total"]

        results.append({
            "id": aid,
            "balance": balance,
            "total_earned": earned,
            "total_spent": spent,
        })
    conn.close()
    return results
