#!/usr/bin/env bash
# Purpose: Update app in-place. Run from repo or /opt/pmg-portal; do git pull first, e.g.:
#   cd /opt/pmg-portal && sudo git pull origin dev && sudo bash scripts/update.sh
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

echo "Ensuring gettext (msgfmt) is installed for compilemessages..."
if ! command -v msgfmt >/dev/null 2>&1; then
  sudo apt-get update -y
  sudo apt-get install -y gettext
fi

echo "Migrating + collectstatic + compilemessages..."
set -a
source "$APP_DIR/.env"
set +a

sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0

sudo systemctl start pmg-portal.service
sudo systemctl status pmg-portal.service --no-pager -l || true

echo "Done."
