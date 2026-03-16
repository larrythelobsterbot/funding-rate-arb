#!/usr/bin/env bash
# ─── Quick update: pull latest and restart ─────────────────────────
set -euo pipefail

APP_DIR="$HOME/funding-rate-arb"
SERVICE_NAME="arb-bot"

echo "→ Pulling latest..."
cd "$APP_DIR"
git pull origin main

echo "→ Reinstalling deps..."
source "$APP_DIR/.venv/bin/activate"
pip install -e . --quiet

echo "→ Restarting bot..."
sudo systemctl restart ${SERVICE_NAME}

echo "→ Done. Checking status..."
sudo systemctl status ${SERVICE_NAME} --no-pager
