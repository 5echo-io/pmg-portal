#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Standalone installer (can be run via curl from GitHub)
# Path: install.sh
# Usage: curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/dev/install.sh | sudo bash
set -euo pipefail

APP_NAME="pmg-portal"
APP_DIR="/opt/pmg-portal"
GITHUB_REPO="https://github.com/5echo-io/pmg-portal.git"
GITHUB_BRANCH="dev"
GITHUB_RAW_BASE="https://raw.githubusercontent.com/5echo-io/pmg-portal/dev"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PMG Portal Installer ===${NC}"

# Check if already installed
if [ -d "$APP_DIR" ] && [ -f "$APP_DIR/.env" ]; then
    echo -e "${YELLOW}PMG Portal is already installed at $APP_DIR${NC}"
    
    # Check if we're in an interactive terminal
    if [ -t 0 ] && [ -t 1 ]; then
        # Interactive mode - ask user
        echo ""
        echo "What would you like to do?"
        echo "1) Update (preserves database and .env, updates code)"
        echo "2) Uninstall (removes everything including database)"
        echo "3) Cancel"
        echo ""
        read -rp "Enter choice [1-3]: " choice
    else
        # Non-interactive mode (piped from curl) - default to update
        echo "Non-interactive mode detected. Defaulting to Update mode."
        choice="1"
    fi
    
    case "$choice" in
        1)
            echo -e "${GREEN}Updating PMG Portal...${NC}"
            MODE="update"
            ;;
        2)
            echo -e "${RED}Uninstalling PMG Portal...${NC}"
            MODE="uninstall"
            ;;
        3)
            echo "Cancelled."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Cancelled.${NC}"
            exit 1
            ;;
    esac
else
    echo -e "${GREEN}No existing installation found. Starting fresh install...${NC}"
    MODE="install"
fi

# Uninstall mode
if [ "$MODE" = "uninstall" ]; then
    # Backup .env before removal for database cleanup
    TEMP_ENV_BACKUP=""
    if [ -f "$APP_DIR/.env" ]; then
        TEMP_ENV_BACKUP=$(mktemp)
        sudo cp "$APP_DIR/.env" "$TEMP_ENV_BACKUP"
        set -a
        source "$APP_DIR/.env"
        set +a
        
        echo ""
        if [ -t 0 ] && [ -t 1 ]; then
            read -rp "Remove Postgres database? (y/N): " remove_db
        else
            echo "Non-interactive mode: preserving database."
            remove_db="N"
        fi
        if [[ "$remove_db" =~ ^[Yy]$ ]]; then
            if [ "${POSTGRES_HOST:-127.0.0.1}" = "127.0.0.1" ] || [ "${POSTGRES_HOST:-127.0.0.1}" = "localhost" ]; then
                echo "Removing Postgres database..."
                sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"${POSTGRES_DB}\";" 2>/dev/null || true
                sudo -u postgres psql -c "DROP USER IF EXISTS \"${POSTGRES_USER}\";" 2>/dev/null || true
            fi
            echo -e "${GREEN}Database removed.${NC}"
        else
            echo "Database preserved."
        fi
        rm -f "$TEMP_ENV_BACKUP"
    fi
    
    echo "Stopping service..."
    sudo systemctl stop pmg-portal.service 2>/dev/null || true
    sudo systemctl disable pmg-portal.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/pmg-portal.service
    sudo systemctl daemon-reload
    
    echo "Removing application files..."
    sudo rm -rf "$APP_DIR"
    
    echo -e "${GREEN}Uninstall complete.${NC}"
    exit 0
fi

# Install/Update mode - download repo
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Downloading PMG Portal from GitHub..."
if ! command -v git &> /dev/null; then
    echo "Installing git..."
    sudo apt-get update -y
    sudo apt-get install -y git
fi

git clone -b "$GITHUB_BRANCH" "$GITHUB_REPO" "$TEMP_DIR/pmg-portal"
REPO_DIR="$TEMP_DIR/pmg-portal"

# Preserve .env if updating
if [ "$MODE" = "update" ] && [ -f "$APP_DIR/.env" ]; then
    echo "Preserving existing .env file..."
    sudo cp "$APP_DIR/.env" "$TEMP_DIR/.env.backup"
fi

# Install OS dependencies (postgresql-client provides pg_dump/psql for Admin → Backup & Restore)
echo "Installing OS dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-client rsync curl

# Copy/update application files
if [ "$MODE" = "update" ]; then
    echo "Updating application files (preserving .env)..."
    sudo systemctl stop pmg-portal.service || true
    sudo rsync -a --exclude='.env' --exclude='.venv' --exclude='staticfiles' "$REPO_DIR/" "$APP_DIR/"
    # Restore .env
    if [ -f "$TEMP_DIR/.env.backup" ]; then
        sudo cp "$TEMP_DIR/.env.backup" "$APP_DIR/.env"
    fi
else
    echo "Installing application files..."
    sudo mkdir -p "$APP_DIR"
    sudo rsync -a "$REPO_DIR/" "$APP_DIR/"
fi

SRC_DIR="$APP_DIR/src"

# Run the install wizard (only for fresh installs or if .env is missing)
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Running install wizard..."
    sudo bash "$APP_DIR/scripts/install.sh"
else
    # For updates, just run the update steps
    echo "Running update steps..."
    
    # Update Python dependencies
    echo "Updating Python dependencies..."
    cd "$SRC_DIR"
    if [ ! -d "$SRC_DIR/.venv" ]; then
        sudo python3 -m venv "$SRC_DIR/.venv"
    fi
    sudo "$SRC_DIR/.venv/bin/pip" install --upgrade pip
    sudo "$SRC_DIR/.venv/bin/pip" install -r "$SRC_DIR/requirements.txt"
    
    # Run migrations and collectstatic
    echo "Running migrations + collectstatic..."
    set -a
    source "$APP_DIR/.env"
    set +a
    
    sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput
    sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
    
    # Update systemd service
    echo "Updating systemd service..."
    sudo cp "$APP_DIR/deploy/systemd/pmg-portal.service" /etc/systemd/system/pmg-portal.service
    sudo systemctl daemon-reload
    sudo systemctl enable --now pmg-portal.service
    
    echo -e "${GREEN}Update complete!${NC}"
fi

echo ""
echo -e "${GREEN}=== PMG Portal Installation Complete ===${NC}"
echo ""
if [ -f "$APP_DIR/.env" ]; then
    source "$APP_DIR/.env"
    echo "Service URL: http://$APP_BIND"
fi
echo "View logs: sudo journalctl -u pmg-portal.service -f --no-pager"
echo ""
