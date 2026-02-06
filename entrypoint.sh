#!/bin/sh
set -e

export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=384}"

# --- Start OpenClaw gateway in the background ------------------------------
# Non-interactive onboard (skip wizard, skip daemon — we run gateway directly)
openclaw onboard --non-interactive \
  --accept-risk \
  --mode local \
  --auth-choice apiKey \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --skip-daemon \
  --skip-skills 2>&1 || echo "Onboard already done or skipped."

# Start the gateway (connects to Telegram, uses OpenRouter, calls FastAPI tools)
openclaw gateway --port 18789 --verbose &
OPENCLAW_PID=$!

echo "OpenClaw gateway started (PID $OPENCLAW_PID)"

# Give OpenClaw a moment to bind
sleep 3

# --- Start FastAPI (tool backend) on $PORT --------------------------------
# Render sets PORT env var; default to 8000.
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
