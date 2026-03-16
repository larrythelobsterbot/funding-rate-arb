#!/usr/bin/env bash
# ─── Funding Rate Arb Bot — VPS Deploy Script ─────────────────────
# Run this once on your VPS to set up the bot.
# Assumes: Ubuntu/Debian, Python 3.10+, git installed.
#
# Usage:
#   chmod +x deploy/setup.sh
#   ./deploy/setup.sh
# ───────────────────────────────────────────────────────────────────

set -euo pipefail

APP_DIR="$HOME/funding-rate-arb"
VENV_DIR="$APP_DIR/.venv"
SERVICE_NAME="arb-bot"

echo "╔══════════════════════════════════════════╗"
echo "║  Funding Rate Arb Bot — VPS Setup        ║"
echo "╚══════════════════════════════════════════╝"

# ─── 1. Clone or pull ──────────────────────────────────────────────
if [ -d "$APP_DIR/.git" ]; then
    echo "→ Repo exists, pulling latest..."
    cd "$APP_DIR"
    git pull origin main
else
    echo "→ Cloning repo..."
    git clone https://github.com/larrythelobsterbot/funding-rate-arb.git "$APP_DIR"
    cd "$APP_DIR"
fi

# ─── 2. Python venv ───────────────────────────────────────────────
echo "→ Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# ─── 3. Install dependencies ──────────────────────────────────────
echo "→ Installing dependencies..."
pip install --upgrade pip
pip install -e .

# ─── 4. .env file ─────────────────────────────────────────────────
if [ ! -f "$APP_DIR/.env" ]; then
    echo "→ Creating .env from template..."
    cp "$APP_DIR/example.env" "$APP_DIR/.env"
    echo ""
    echo "⚠  IMPORTANT: Edit $APP_DIR/.env with your API keys before running."
    echo "   nano $APP_DIR/.env"
    echo ""
else
    echo "→ .env already exists, skipping."
fi

# ─── 5. systemd service ───────────────────────────────────────────
echo "→ Installing systemd service..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=Funding Rate Arbitrage Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${APP_DIR}
Environment=PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=${VENV_DIR}/bin/python -m Main.run
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Also install a demo service (one-shot, for testing)
sudo tee /etc/systemd/system/${SERVICE_NAME}-demo.service > /dev/null << EOF
[Unit]
Description=Funding Rate Arb Bot — Demo (single scan)
After=network.target

[Service]
Type=oneshot
User=$(whoami)
WorkingDirectory=${APP_DIR}
Environment=PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=${VENV_DIR}/bin/project-run-demo
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  Setup complete!                         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Edit your .env:           nano $APP_DIR/.env"
echo "  2. Run a demo scan:          sudo systemctl start ${SERVICE_NAME}-demo"
echo "     Check output:             journalctl -u ${SERVICE_NAME}-demo -f"
echo "  3. Start the live bot:       sudo systemctl start ${SERVICE_NAME}"
echo "     Enable on boot:           sudo systemctl enable ${SERVICE_NAME}"
echo "     Check logs:               journalctl -u ${SERVICE_NAME} -f"
echo "  4. Stop the bot:             sudo systemctl stop ${SERVICE_NAME}"
echo ""
