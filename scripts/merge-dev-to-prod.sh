#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Merge development features to production (final release)
# Path: scripts/merge-dev-to-prod.sh
# Usage: sudo bash scripts/merge-dev-to-prod.sh
set -euo pipefail

PROD_DIR="/opt/pmg-portal"
DEV_DIR="/opt/pmg-portal-dev"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Merging Development to Production (Final Release) ===${NC}"
echo ""

# Check installations
if [ ! -d "$PROD_DIR" ] || [ ! -f "$PROD_DIR/.env" ]; then
    echo -e "${RED}Production installation not found at $PROD_DIR${NC}"
    exit 1
fi

if [ ! -d "$DEV_DIR" ] || [ ! -f "$DEV_DIR/.env" ]; then
    echo -e "${RED}Development installation not found at $DEV_DIR${NC}"
    exit 1
fi

echo -e "${RED}WARNING: This will merge development features into production.${NC}"
echo "This operation will:"
echo "  1. Backup production database"
echo "  2. Pull latest main branch (should have dev features merged)"
echo "  3. Run migrations (will add dev features to production)"
echo "  4. Keep all existing production data"
echo ""

if [ -t 0 ] && [ -t 1 ]; then
    read -rp "Are you sure you want to proceed? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Backup production database
echo "Backing up production database..."
set -a
source "$PROD_DIR/.env"
set +a

BACKUP_FILE="/tmp/pmg_portal_backup_$(date +%Y%m%d_%H%M%S).sql"
if [ "$POSTGRES_HOST" = "127.0.0.1" ] || [ "$POSTGRES_HOST" = "localhost" ]; then
    sudo -u postgres pg_dump "$POSTGRES_DB" > "$BACKUP_FILE"
    echo -e "${GREEN}Database backup saved to: $BACKUP_FILE${NC}"
else
    echo -e "${YELLOW}Remote database detected. Please backup manually.${NC}"
fi

# Backup .env
sudo cp "$PROD_DIR/.env" "$PROD_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"

# Update production from main (should have dev features merged)
echo "Updating production from main branch..."
cd "$PROD_DIR"
sudo git fetch origin
sudo git checkout main
sudo git pull origin main

# Enable dev features in production (they're now stable)
echo "Enabling features in production..."
if grep -q "^ENABLE_DEV_FEATURES=false" "$PROD_DIR/.env"; then
    sudo sed -i 's/^ENABLE_DEV_FEATURES=false/ENABLE_DEV_FEATURES=true/' "$PROD_DIR/.env"
    echo "Changed ENABLE_DEV_FEATURES to true"
fi

# Update Python dependencies
echo "Updating Python dependencies..."
cd "$PROD_DIR/src"
sudo "$PROD_DIR/src/.venv/bin/pip" install -r "$PROD_DIR/src/requirements.txt"

# Run migrations (will add dev features)
echo "Running migrations..."
set -a
source "$PROD_DIR/.env"
set +a

sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py migrate --noinput
sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py collectstatic --noinput
sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py compilemessages --verbosity 0

# Restart service
echo "Restarting production service..."
sudo systemctl restart pmg-portal.service
sudo systemctl status pmg-portal.service --no-pager -l || true

echo ""
echo -e "${GREEN}=== Merge Complete! ===${NC}"
echo "Production now has all development features."
if [ -f "$BACKUP_FILE" ]; then
    echo "Database backup: $BACKUP_FILE"
fi
echo ""
echo "You can continue developing new features in development environment."
echo ""
