#!/bin/sh
set -e

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

# Start the gateway with auto-restart on crash
(
  while true; do
    echo "[entrypoint] Starting OpenClaw gateway..."
    openclaw gateway --port 18789 --verbose 2>&1 || true
    echo "[entrypoint] OpenClaw gateway exited, restarting in 5s..."
    sleep 5
  done
) &
OPENCLAW_PID=$!

echo "OpenClaw gateway wrapper started (PID $OPENCLAW_PID)"

# Give OpenClaw a moment to bind
sleep 5

# --- Start FastAPI (tool backend) on $PORT --------------------------------
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
