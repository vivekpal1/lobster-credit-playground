"""Telegram bot handlers for the three lobster agents.

Each bot runs as an async polling loop inside the FastAPI process.
Messages are routed to the right agent based on which bot receives them.
The agent calls ledger/data functions directly (no HTTP round-trip needed).
"""

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

from app.config import (
    TELEGRAM_BOT_TOKEN_RED,
    TELEGRAM_BOT_TOKEN_YELLOW,
    TELEGRAM_BOT_TOKEN_GREEN,
)
from app.services.llm import chat
from app.services.price_provider import get_price
from app import ledger

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Soul prompts (loaded inline — same content as the SOUL.md files)
# ---------------------------------------------------------------------------

RED_SYSTEM = """You are Lobster Red, the data lobster. You fetch live cryptocurrency prices.
- Keep answers SHORT. One price, one line. Maybe one joke.
- Never give financial advice.
- Only support BTC and ETH.
- You will receive the current price data as context when available.
- If someone asks for analysis, redirect them to Yellow. For balances, redirect to Green."""

YELLOW_SYSTEM = """You are Lobster Yellow, the analyst lobster. You interpret crypto data and charge credits.
- Structure responses as: Trend / Risk / Summary.
- Never overstate certainty.
- You will receive the current price data as context.
- You charge 2 credits per analysis. The system handles the transfer automatically.
- If the charge fails (insufficient balance), tell the user to ask Green for starter credits.
- For raw prices, redirect to Red. For balances, redirect to Green."""

GREEN_SYSTEM = """You are Lobster Green, the bank lobster. You manage the credit ledger.
- Be blunt and numeric. Always show exact balances.
- Handle: /start (create account + 50 credits), balance, agents/stats, transfers.
- You will receive account/stats data as context when available.
- For prices, redirect to Red. For analysis, redirect to Yellow."""


# ---------------------------------------------------------------------------
# Red handler
# ---------------------------------------------------------------------------
async def handle_red(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    user_msg = text

    # Try to fetch price data for context
    context_data = ""
    lower = text.lower()
    for sym in ("btc", "eth", "bitcoin", "ethereum"):
        if sym in lower:
            symbol = "btc" if sym in ("btc", "bitcoin") else "eth"
            try:
                price_data = await get_price(symbol)
                if "error" not in price_data:
                    context_data = f"\n\nCurrent data: {price_data['symbol']} = ${price_data['price_usd']:,.2f} (at {price_data['timestamp']})"
            except Exception:
                context_data = "\n\nPrice API is temporarily unavailable."
            break

    prompt = RED_SYSTEM + context_data
    reply = await chat(prompt, user_msg)
    await update.message.reply_text(reply)


# ---------------------------------------------------------------------------
# Yellow handler
# ---------------------------------------------------------------------------
async def handle_yellow(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    user_id = str(update.effective_user.id)

    # Fetch price for analysis context
    context_data = ""
    symbol = None
    lower = text.lower()
    for sym in ("btc", "eth", "bitcoin", "ethereum"):
        if sym in lower:
            symbol = "btc" if sym in ("btc", "bitcoin") else "eth"
            break

    charge_note = ""
    if symbol:
        try:
            price_data = await get_price(symbol)
            if "error" not in price_data:
                context_data = f"\n\nCurrent data: {price_data['symbol']} = ${price_data['price_usd']:,.2f} (at {price_data['timestamp']})"
        except Exception:
            context_data = "\n\nPrice API is temporarily unavailable."

        # Charge user 2 credits
        charge = ledger.transfer(user_id, "lobster_yellow", 2, memo=f"{symbol} analysis fee")
        if charge["ok"]:
            # Pay Red 1 credit for data
            ledger.transfer("lobster_yellow", "lobster_red", 1, memo="data fee")
            acct = ledger.get_account(user_id)
            bal = acct["balance"] if acct else "?"
            charge_note = f"\n\n💳 Charged: 2 credits | Your balance: {bal}"
        else:
            charge_note = f"\n\n⚠️ Could not charge: {charge['message']}\nAsk Green for starter credits first! Say: Green: start"

    prompt = YELLOW_SYSTEM + context_data
    reply = await chat(prompt, text)
    await update.message.reply_text(reply + charge_note)


# ---------------------------------------------------------------------------
# Green handler
# ---------------------------------------------------------------------------
async def handle_green_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    name = update.effective_user.first_name or user_id

    acct = ledger.get_account(user_id)
    if acct:
        await update.message.reply_text(
            f"You already have an account, {name}.\n"
            f"💰 Balance: {acct['balance']} credits\n"
            f"📊 Credit limit: {acct['credit_limit']} | Reputation: {acct['reputation']}"
        )
        return

    ledger.create_account(user_id, initial_balance=0, credit_limit=10)
    result = ledger.issue_credit(user_id, 50)
    acct = ledger.get_account(user_id)
    bal = acct["balance"] if acct else 50
    await update.message.reply_text(
        f"Welcome, {name}! 🦞\n"
        f"💰 Balance: {bal} credits\n"
        f"📊 Credit limit: 10 | Reputation: 500\n\n"
        f"Ask Red for prices, Yellow for analysis!"
    )


async def handle_green(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").lower()
    user_id = str(update.effective_user.id)

    # Direct handling for known commands
    if "balance" in text:
        acct = ledger.get_account(user_id)
        if not acct:
            await update.message.reply_text("No account found. Say /start to create one.")
            return
        await update.message.reply_text(
            f"💰 Balance: {acct['balance']} credits\n"
            f"📊 Credit limit: {acct['credit_limit']} | Reputation: {acct['reputation']}"
        )
        return

    if "agent" in text or "stats" in text:
        stats = ledger.get_agent_stats()
        lines = ["🦞 Agent Stats:"]
        for s in stats:
            lines.append(f"  {s['id']}: balance {s['balance']}, earned {s['total_earned']}, spent {s['total_spent']}")
        await update.message.reply_text("\n".join(lines))
        return

    if "start" in text:
        await handle_green_start(update, ctx)
        return

    # Fallback to LLM for other messages
    acct = ledger.get_account(user_id)
    context_data = f"\n\nUser {user_id} account: {acct}" if acct else "\n\nUser has no account yet."
    prompt = GREEN_SYSTEM + context_data
    reply = await chat(prompt, text)
    await update.message.reply_text(reply)


# ---------------------------------------------------------------------------
# Bot lifecycle
# ---------------------------------------------------------------------------
_apps: list = []


async def start_bots():
    """Start all three Telegram bots as async polling loops."""
    bots = [
        ("Red", TELEGRAM_BOT_TOKEN_RED, handle_red, handle_red),
        ("Yellow", TELEGRAM_BOT_TOKEN_YELLOW, handle_yellow, handle_yellow),
        ("Green", TELEGRAM_BOT_TOKEN_GREEN, handle_green, handle_green_start),
    ]

    for name, token, msg_handler, start_handler in bots:
        if not token:
            log.warning("No token for Lobster %s — skipping.", name)
            continue

        try:
            app = ApplicationBuilder().token(token).connect_timeout(20).read_timeout(20).build()
            app.add_handler(CommandHandler("start", start_handler))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))

            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            log.info("Lobster %s bot started.", name)
            _apps.append(app)
        except Exception as e:
            log.error("Failed to start Lobster %s bot: %s", name, e)


async def stop_bots():
    """Gracefully stop all running bots."""
    for app in _apps:
        try:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except Exception as e:
            log.warning("Error stopping bot: %s", e)
    _apps.clear()
