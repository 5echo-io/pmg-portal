#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Install both production and development environments side-by-side
# Path: scripts/install-dual.sh
# Usage: sudo bash scripts/install-dual.sh
set -euo pipefail

APP_NAME="pmg-portal"
PROD_DIR="/opt/pmg-portal"
DEV_DIR="/opt/pmg-portal-dev"
GITHUB_REPO="https://github.com/5echo-io/pmg-portal.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PMG Portal Dual Installation (Production + Development) ===${NC}"
echo ""

# Check if already installed
if [ -d "$PROD_DIR" ] && [ -f "$PROD_DIR/.env" ]; then
    echo -e "${YELLOW}Production installation found at $PROD_DIR${NC}"
fi

if [ -d "$DEV_DIR" ] && [ -f "$DEV_DIR/.env" ]; then
    echo -e "${YELLOW}Development installation found at $DEV_DIR${NC}"
fi

echo ""
echo "This script will install:"
echo "  1. Production installation at $PROD_DIR (port 8097, main branch)"
echo "  2. Development installation at $DEV_DIR (port 8098, dev branch)"
echo ""
read -rp "Continue? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Install git if needed
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo apt-get update -y
    sudo apt-get install -y git
fi

# ============================================
# PRODUCTION INSTALLATION
# ============================================
echo ""
echo -e "${GREEN}=== Installing Production Environment ===${NC}"

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Downloading production code from main branch..."
git clone -b main "$GITHUB_REPO" "$TEMP_DIR/pmg-portal-prod"
REPO_DIR="$TEMP_DIR/pmg-portal-prod"

# Preserve .env if updating
if [ -f "$PROD_DIR/.env" ]; then
    echo "Preserving existing production .env file..."
    sudo cp "$PROD_DIR/.env" "$TEMP_DIR/.env.prod.backup"
fi

# Install OS dependencies
echo "Installing OS dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-client rsync curl gettext libjpeg-dev libpng-dev zlib1g-dev

# Copy/update application files
if [ -d "$PROD_DIR" ] && [ -f "$PROD_DIR/.env" ]; then
    echo "Updating production files (preserving .env)..."
    sudo systemctl stop pmg-portal.service 2>/dev/null || true
    sudo rsync -a --exclude='.env' --exclude='.venv' --exclude='staticfiles' "$REPO_DIR/" "$PROD_DIR/"
    # Restore .env
    if [ -f "$TEMP_DIR/.env.prod.backup" ]; then
        sudo cp "$TEMP_DIR/.env.prod.backup" "$PROD_DIR/.env"
    fi
else
    echo "Installing production files..."
    sudo mkdir -p "$PROD_DIR"
    sudo rsync -a "$REPO_DIR/" "$PROD_DIR/"
fi

# Run install wizard if .env doesn't exist
if [ ! -f "$PROD_DIR/.env" ]; then
    echo "Running production install wizard..."
    sudo bash "$PROD_DIR/scripts/install.sh"
else
    echo "Running production update steps..."
    cd "$PROD_DIR/src"
    if [ ! -d "$PROD_DIR/src/.venv" ]; then
        sudo python3 -m venv "$PROD_DIR/src/.venv"
    fi
    sudo "$PROD_DIR/src/.venv/bin/pip" install --upgrade pip
    sudo "$PROD_DIR/src/.venv/bin/pip" install -r "$PROD_DIR/src/requirements.txt"
    
    echo "Running migrations + collectstatic..."
    set -a
    source "$PROD_DIR/.env"
    set +a
    
    sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py migrate --noinput
    sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py collectstatic --noinput
    sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py compilemessages --verbosity 0
    
    # Update systemd service
    echo "Updating production systemd service..."
    sudo cp "$PROD_DIR/deploy/systemd/pmg-portal.service" /etc/systemd/system/pmg-portal.service
    sudo systemctl daemon-reload
    sudo systemctl enable --now pmg-portal.service
    
    echo -e "${GREEN}Production update complete!${NC}"
fi

# ============================================
# DEVELOPMENT INSTALLATION
# ============================================
echo ""
echo -e "${GREEN}=== Installing Development Environment ===${NC}"

echo "Downloading development code from dev branch..."
git clone -b dev "$GITHUB_REPO" "$TEMP_DIR/pmg-portal-dev"
REPO_DIR_DEV="$TEMP_DIR/pmg-portal-dev"

# Preserve .env if updating
if [ -f "$DEV_DIR/.env" ]; then
    echo "Preserving existing development .env file..."
    sudo cp "$DEV_DIR/.env" "$TEMP_DIR/.env.dev.backup"
fi

# Copy/update application files
if [ -d "$DEV_DIR" ] && [ -f "$DEV_DIR/.env" ]; then
    echo "Updating development files (preserving .env)..."
    sudo systemctl stop pmg-portal-dev.service 2>/dev/null || true
    sudo rsync -a --exclude='.env' --exclude='.venv' --exclude='staticfiles' "$REPO_DIR_DEV/" "$DEV_DIR/"
    # Restore .env
    if [ -f "$TEMP_DIR/.env.dev.backup" ]; then
        sudo cp "$TEMP_DIR/.env.dev.backup" "$DEV_DIR/.env"
    fi
else
    echo "Installing development files..."
    sudo mkdir -p "$DEV_DIR"
    sudo rsync -a "$REPO_DIR_DEV/" "$DEV_DIR/"
fi

# Run install wizard if .env doesn't exist
if [ ! -f "$DEV_DIR/.env" ]; then
    echo "Running development install wizard..."
    echo ""
    echo -e "${YELLOW}IMPORTANT: When prompted, set:${NC}"
    echo "  - APP_BIND=0.0.0.0:8098 (different port from production)"
    echo "  - POSTGRES_DB=pmg_portal_dev (different database)"
    echo "  - ENABLE_DEV_FEATURES=true (enable dev features)"
    echo ""
    read -rp "Press Enter to continue with development installation..."
    sudo bash "$DEV_DIR/scripts/install.sh"
else
    echo "Running development update steps..."
    cd "$DEV_DIR/src"
    if [ ! -d "$DEV_DIR/src/.venv" ]; then
        sudo python3 -m venv "$DEV_DIR/src/.venv"
    fi
    sudo "$DEV_DIR/src/.venv/bin/pip" install --upgrade pip
    sudo "$DEV_DIR/src/.venv/bin/pip" install -r "$DEV_DIR/src/requirements.txt"
    
    echo "Running migrations + collectstatic..."
    set -a
    source "$DEV_DIR/.env"
    set +a
    
    sudo -E "$DEV_DIR/src/.venv/bin/python" manage.py migrate --noinput
    sudo -E "$DEV_DIR/src/.venv/bin/python" manage.py collectstatic --noinput
    sudo -E "$DEV_DIR/src/.venv/bin/python" manage.py compilemessages --verbosity 0
    
    # Create/update systemd service for dev
    echo "Creating/updating development systemd service..."
    sudo tee /etc/systemd/system/pmg-portal-dev.service > /dev/null <<EOF
[Unit]
Description=PMG Portal Development (Gunicorn)
After=network.target

[Service]
Type=simple
WorkingDirectory=$DEV_DIR/src
EnvironmentFile=$DEV_DIR/.env
ExecStart=$DEV_DIR/src/.venv/bin/gunicorn pmg_portal.wsgi:application --bind \${APP_BIND} --workers 2 --access-logfile -
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable --now pmg-portal-dev.service
    
    echo -e "${GREEN}Development update complete!${NC}"
fi

# ============================================
# SUMMARY
# ============================================
echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Production Environment:"
if [ -f "$PROD_DIR/.env" ]; then
    source "$PROD_DIR/.env"
    echo "  URL: http://$APP_BIND"
fi
echo "  Path: $PROD_DIR"
echo "  Service: pmg-portal.service"
echo "  Logs: sudo journalctl -u pmg-portal.service -f --no-pager"
echo ""
echo "Development Environment:"
if [ -f "$DEV_DIR/.env" ]; then
    source "$DEV_DIR/.env"
    echo "  URL: http://$APP_BIND"
fi
echo "  Path: $DEV_DIR"
echo "  Service: pmg-portal-dev.service"
echo "  Logs: sudo journalctl -u pmg-portal-dev.service -f --no-pager"
echo ""
echo "To update production: cd $PROD_DIR && sudo git pull origin main && sudo bash scripts/update.sh"
echo "To update development: cd $DEV_DIR && sudo git pull origin dev && sudo bash scripts/update.sh"
echo ""
