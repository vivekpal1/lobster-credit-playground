# Stage 1: grab Node.js binary from official image
FROM node:22-slim AS node

# Stage 2: Python + Node.js + OpenClaw + FastAPI
FROM python:3.12-slim

WORKDIR /app

# Install git (required by openclaw's npm dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Copy Node.js from the node image (no external repos needed)
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm && \
    ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

# Install OpenClaw globally
RUN npm install -g openclaw@latest

# --- Python deps -----------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- App code + OpenClaw config --------------------------------------------
COPY app/ ./app/
COPY openclaw/ ./openclaw/
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# --- Setup OpenClaw workspace structure ------------------------------------
RUN mkdir -p /root/.openclaw/workspaces/red/skills \
             /root/.openclaw/workspaces/yellow/skills \
             /root/.openclaw/workspaces/green/skills \
             /root/.openclaw/agents/lobster_red \
             /root/.openclaw/agents/lobster_yellow \
             /root/.openclaw/agents/lobster_green \
             /app/data

# Copy souls into agent dirs as SOUL.md
RUN cp openclaw/souls/lobster_red_soul.md    /root/.openclaw/agents/lobster_red/SOUL.md && \
    cp openclaw/souls/lobster_yellow_soul.md /root/.openclaw/agents/lobster_yellow/SOUL.md && \
    cp openclaw/souls/lobster_green_soul.md  /root/.openclaw/agents/lobster_green/SOUL.md

# Copy skills into workspace dirs as SKILL.md
RUN cp openclaw/skills/lobster_red_skills.md    /root/.openclaw/workspaces/red/skills/SKILL.md && \
    cp openclaw/skills/lobster_yellow_skills.md /root/.openclaw/workspaces/yellow/skills/SKILL.md && \
    cp openclaw/skills/lobster_green_skills.md  /root/.openclaw/workspaces/green/skills/SKILL.md

# Copy the OpenClaw config
RUN cp openclaw/openclaw.config.json /root/.openclaw/openclaw.json

ENV LEDGER_DB_PATH=/app/data/ledger.db

EXPOSE 8000

CMD ["./entrypoint.sh"]
