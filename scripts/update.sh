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

sudo systemctl start pmg-portal.service
sudo systemctl status pmg-portal.service --no-pager -l || true

# Update development environment if it exists
if [ -d "/opt/pmg-portal-dev" ] && [ -f "/opt/pmg-portal-dev/.env" ]; then
    echo ""
    echo "=== Updating Development Environment ==="
    DEV_DIR="/opt/pmg-portal-dev"
    DEV_SRC_DIR="$DEV_DIR/src"
    
    # Check which branch development is on
    cd "$DEV_DIR"
    CURRENT_BRANCH=$(sudo git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "dev")
    
    if [ "$CURRENT_BRANCH" = "dev" ]; then
        echo "Pulling latest dev branch..."
        sudo git pull origin dev || true
    else
        echo "Switching to dev branch..."
        sudo git fetch origin
        sudo git checkout dev || true
        sudo git pull origin dev || true
    fi
    
    echo "Updating Python dependencies..."
    cd "$DEV_SRC_DIR"
    sudo "$DEV_SRC_DIR/.venv/bin/pip" install -r "$DEV_SRC_DIR/requirements.txt"
    
    echo "Running migrations + collectstatic + compilemessages..."
    set -a
    source "$DEV_DIR/.env"
    set +a
    
    sudo -E "$DEV_SRC_DIR/.venv/bin/python" manage.py migrate --noinput
    sudo -E "$DEV_SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
    sudo -E "$DEV_SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0
    
    sudo systemctl restart pmg-portal-dev.service
    sudo systemctl status pmg-portal-dev.service --no-pager -l || true
    
    echo "Development environment updated!"
fi

echo ""
echo "Done."
