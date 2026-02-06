"""Routes for the credit ledger — accounts, transfers, stats."""

from fastapi import APIRouter, HTTPException
from app import ledger, models

router = APIRouter(prefix="/ledger", tags=["ledger"])


@router.post("/account", response_model=models.TransferResponse)
def create_account(req: models.CreateAccountRequest):
    result = ledger.create_account(req.id, req.initial_balance, req.credit_limit, req.reputation)
    return result


@router.get("/balance")
def get_balance(user_id: str):
    acct = ledger.get_account(user_id)
    if acct is None:
        raise HTTPException(404, f"Account {user_id} not found.")
    return acct


@router.post("/transfer", response_model=models.TransferResponse)
def do_transfer(req: models.TransferRequest):
    result = ledger.transfer(req.from_id, req.to_id, req.amount, req.memo)
    if not result["ok"]:
        raise HTTPException(400, result["message"])
    return result


@router.post("/issue_credit", response_model=models.TransferResponse)
def issue_credit(req: models.IssueCreditRequest):
    # Auto-create the user account if it doesn't exist.
    if ledger.get_account(req.user_id) is None:
        ledger.create_account(req.user_id, initial_balance=0, credit_limit=10)
    result = ledger.issue_credit(req.user_id, req.amount)
    if not result["ok"]:
        raise HTTPException(400, result["message"])
    return result


@router.get("/agent_stats")
def agent_stats():
    return ledger.get_agent_stats()
