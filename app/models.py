"""Pydantic models for request / response payloads."""

from pydantic import BaseModel
from typing import Optional


# --- Ledger ---------------------------------------------------------------

class CreateAccountRequest(BaseModel):
    id: str
    initial_balance: int = 0
    credit_limit: int = 10
    reputation: int = 500


class TransferRequest(BaseModel):
    from_id: str
    to_id: str
    amount: int
    memo: Optional[str] = None


class IssueCreditRequest(BaseModel):
    user_id: str
    amount: int


class AccountResponse(BaseModel):
    id: str
    balance: int
    credit_limit: int
    reputation: int


class TransferResponse(BaseModel):
    ok: bool
    message: str
    tx_id: Optional[int] = None


class AgentStatsEntry(BaseModel):
    id: str
    balance: int
    total_earned: int
    total_spent: int


# --- Data -----------------------------------------------------------------

class PriceResponse(BaseModel):
    symbol: str
    price_usd: float
    timestamp: str


# --- Settlement -----------------------------------------------------------

class SettleResponse(BaseModel):
    ok: bool
    message: str
    tx_signature: Optional[str] = None
    explorer_url: Optional[str] = None
