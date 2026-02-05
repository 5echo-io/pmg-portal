#!/usr/bin/env bash
# Purpose: Update app in-place (git pull expected to be done before running, or rsync from repo clone)
set -euo pipefail

APP_DIR="/opt/pmg-portal"
SRC_DIR="$APP_DIR/src"

echo "=== Updating pmg-portal ==="

if [ ! -d "$APP_DIR" ]; then
  echo "ERROR: $APP_DIR not found. Run install.sh first."
  exit 1
fi

sudo systemctl stop pmg-portal.service || true

echo "Re-installing python deps..."
cd "$SRC_DIR"
sudo "$SRC_DIR/.venv/bin/pip" install -r "$SRC_DIR/requirements.txt"

echo "Migrating + collectstatic..."
set -a
source "$APP_DIR/.env"
set +a

sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput

sudo systemctl start pmg-portal.service
sudo systemctl status pmg-portal.service --no-pager -l || true

echo "Done."
