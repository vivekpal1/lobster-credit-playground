FROM python:3.12-slim

WORKDIR /app

# --- System deps for Node.js (OpenClaw) + Python --------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js 22 (required by OpenClaw)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

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
# Create directories that OpenClaw expects for the three agents.
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
