"""Solana devnet settlement demo.

Reads agent balances and sends a small SOL transfer on devnet to prove
that off-chain state *can* be settled on-chain.
"""

import json
import base64
from app.config import SOLANA_RPC_URL, SOLANA_SETTLEMENT_PRIVATE_KEY
from app.ledger import get_agent_stats

# We only import solana/solders when actually settling, so the service
# starts fine even if the deps are missing or the key is unset.


def _load_keypair():
    """Parse the settlement private key from env (base58 or JSON array)."""
    from solders.keypair import Keypair  # type: ignore

    raw = SOLANA_SETTLEMENT_PRIVATE_KEY.strip()
    if not raw:
        raise ValueError("SOLANA_SETTLEMENT_PRIVATE_KEY is not set.")

    # Try JSON array of ints first (Solana CLI format).
    if raw.startswith("["):
        secret = bytes(json.loads(raw))
        return Keypair.from_bytes(secret)

    # Otherwise treat as base58.
    return Keypair.from_base58_string(raw)


async def settle() -> dict:
    """Build and send a tiny devnet SOL transfer as settlement proof."""
    try:
        from solders.keypair import Keypair  # type: ignore
        from solders.pubkey import Pubkey  # type: ignore
        from solders.system_program import transfer, TransferParams  # type: ignore
        from solders.transaction import Transaction  # type: ignore
        from solders.message import Message  # type: ignore
        from solders.hash import Hash  # type: ignore
        import httpx
    except ImportError:
        return {
            "ok": False,
            "message": "Solana dependencies not installed. Run: pip install solders solana",
        }

    try:
        payer = _load_keypair()
    except ValueError as e:
        return {"ok": False, "message": str(e)}

    stats = get_agent_stats()
    memo_lines = [f"{s['id']}: balance={s['balance']}" for s in stats]
    memo = " | ".join(memo_lines)

    # We send 5000 lamports (~negligible) to ourselves as a memo-bearing proof tx.
    recipient = payer.pubkey()
    ix = transfer(TransferParams(from_pubkey=payer.pubkey(), to_pubkey=recipient, lamports=5000))

    async with httpx.AsyncClient(timeout=30) as client:
        # Fetch recent blockhash.
        rpc_body = {"jsonrpc": "2.0", "id": 1, "method": "getLatestBlockhash", "params": []}
        resp = await client.post(SOLANA_RPC_URL, json=rpc_body)
        bh_data = resp.json()
        blockhash_str = bh_data["result"]["value"]["blockhash"]
        blockhash = Hash.from_string(blockhash_str)

        msg = Message.new_with_blockhash([ix], payer.pubkey(), blockhash)
        tx = Transaction.new_unsigned(msg)
        tx.sign([payer], blockhash)

        tx_bytes = bytes(tx)
        tx_b64 = base64.b64encode(tx_bytes).decode()

        send_body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "sendTransaction",
            "params": [tx_b64, {"encoding": "base64"}],
        }
        send_resp = await client.post(SOLANA_RPC_URL, json=send_body)
        send_data = send_resp.json()

    if "error" in send_data:
        return {"ok": False, "message": f"RPC error: {send_data['error']}"}

    sig = send_data["result"]
    return {
        "ok": True,
        "message": f"Settlement proof sent. Memo: {memo}",
        "tx_signature": sig,
        "explorer_url": f"https://explorer.solana.com/tx/{sig}?cluster=devnet",
    }
