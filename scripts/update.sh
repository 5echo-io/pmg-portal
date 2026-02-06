#!/usr/bin/env bash
# Purpose: Update app in-place. Run from repo or /opt/pmg-portal; detects if production or development
# Usage: cd /opt/pmg-portal && sudo bash scripts/update.sh
#        cd /opt/pmg-portal-dev && sudo bash scripts/update.sh
set -euo pipefail

# Detect if this is production or development based on path
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$APP_DIR/src"

# Determine branch based on installation type
if [ "$APP_DIR" = "/opt/pmg-portal-dev" ]; then
    BRANCH="dev"
    SERVICE_NAME="pmg-portal-dev.service"
    ENV_TYPE="development"
else
    BRANCH="main"
    SERVICE_NAME="pmg-portal.service"
    ENV_TYPE="production"
fi

echo "=== Updating PMG Portal ($ENV_TYPE) ==="

if [ ! -d "$APP_DIR" ]; then
    echo "ERROR: $APP_DIR not found. Run install.sh first."
    exit 1
fi

if [ ! -f "$APP_DIR/.env" ]; then
    echo "ERROR: $APP_DIR/.env not found. Run install.sh first."
    exit 1
fi

echo "Detected: $ENV_TYPE installation"
echo "Using branch: $BRANCH"
echo ""

# Pull latest code from correct branch
echo "Pulling latest code from $BRANCH branch..."
cd "$APP_DIR"
sudo git fetch origin
CURRENT_BRANCH=$(sudo git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "$BRANCH")
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "Switching to $BRANCH branch..."
    sudo git checkout "$BRANCH" || true
fi
sudo git pull origin "$BRANCH"

sudo systemctl stop "$SERVICE_NAME" || true

echo "Re-installing python deps..."
cd "$SRC_DIR"
sudo "$SRC_DIR/.venv/bin/pip" install -r "$SRC_DIR/requirements.txt"

echo "Ensuring system dependencies are installed..."
NEED_UPDATE=false
if ! command -v msgfmt >/dev/null 2>&1; then
  NEED_UPDATE=true
fi
# Check if Pillow build dependencies are installed
if [ ! -f /usr/include/jpeglib.h ] || [ ! -f /usr/include/png.h ]; then
  NEED_UPDATE=true
fi
if [ "$NEED_UPDATE" = "true" ]; then
  sudo apt-get update -y
  sudo apt-get install -y gettext libjpeg-dev libpng-dev zlib1g-dev
fi

echo "Ensuring media directory exists..."
MEDIA_DIR="$APP_DIR/media"
sudo mkdir -p "$MEDIA_DIR"
# Set ownership: check systemd service file for User, fallback to root (default in pmg-portal.service)
# Media directory should be writable by the service user
SERVICE_USER="root"  # Default from pmg-portal.service
if [ -f "/etc/systemd/system/pmg-portal.service" ]; then
  # Try to extract User from installed service file if specified
  EXTRACTED_USER=$(grep -E "^User=" /etc/systemd/system/pmg-portal.service | cut -d'=' -f2 | tr -d ' ' || echo "")
  if [ -n "$EXTRACTED_USER" ]; then
    SERVICE_USER="$EXTRACTED_USER"
  fi
fi
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$MEDIA_DIR"
sudo chmod -R 755 "$MEDIA_DIR"

echo "Migrating + collectstatic + compilemessages..."
set -a
source "$APP_DIR/.env"
set +a

sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0

sudo systemctl start "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager -l || true

echo ""
echo "Done."
echo "Service: $SERVICE_NAME"
echo "Logs: sudo journalctl -u $SERVICE_NAME -f --no-pager"
