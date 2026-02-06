#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Fix ALLOWED_HOSTS in .env files
# Path: scripts/fix-allowed-hosts.sh
# Usage: sudo bash scripts/fix-allowed-hosts.sh
set -euo pipefail

PROD_DIR="/opt/pmg-portal"
DEV_DIR="/opt/pmg-portal-dev"

echo "=== Fixing ALLOWED_HOSTS Configuration ==="
echo ""

# Fix production .env
if [ -f "$PROD_DIR/.env" ]; then
    echo "Fixing production .env..."
    
    # Backup
    sudo cp "$PROD_DIR/.env" "$PROD_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Remove dev subdomain from production ALLOWED_HOSTS
    sudo sed -i 's/dev\.portal\.parkmediagroup\.no,//g' "$PROD_DIR/.env"
    sudo sed -i 's/,dev\.portal\.parkmediagroup\.no//g' "$PROD_DIR/.env"
    sudo sed -i 's/dev\.portal\.parkmediagroup\.no//g' "$PROD_DIR/.env"
    
    # Ensure production has correct hosts
    CURRENT_HOSTS=$(grep "^DJANGO_ALLOWED_HOSTS=" "$PROD_DIR/.env" | cut -d'=' -f2-)
    if [[ "$CURRENT_HOSTS" != *"portal.parkmediagroup.no"* ]] && [[ "$CURRENT_HOSTS" != *"localhost"* ]]; then
        echo "Warning: Production ALLOWED_HOSTS may be incorrect: $CURRENT_HOSTS"
    fi
    
    echo "Production .env fixed."
    echo "Current ALLOWED_HOSTS: $(grep "^DJANGO_ALLOWED_HOSTS=" "$PROD_DIR/.env" | cut -d'=' -f2-)"
    echo ""
fi

# Fix development .env
if [ -f "$DEV_DIR/.env" ]; then
    echo "Fixing development .env..."
    
    # Backup
    sudo cp "$DEV_DIR/.env" "$DEV_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Ensure dev subdomain is in development ALLOWED_HOSTS
    CURRENT_HOSTS=$(grep "^DJANGO_ALLOWED_HOSTS=" "$DEV_DIR/.env" | cut -d'=' -f2-)
    if [[ "$CURRENT_HOSTS" != *"dev.portal.parkmediagroup.no"* ]]; then
        # Add dev subdomain if not present
        NEW_HOSTS="dev.portal.parkmediagroup.no,$CURRENT_HOSTS"
        sudo sed -i "s|^DJANGO_ALLOWED_HOSTS=.*|DJANGO_ALLOWED_HOSTS=$NEW_HOSTS|" "$DEV_DIR/.env"
        echo "Added dev subdomain to development ALLOWED_HOSTS"
    fi
    
    echo "Development .env fixed."
    echo "Current ALLOWED_HOSTS: $(grep "^DJANGO_ALLOWED_HOSTS=" "$DEV_DIR/.env" | cut -d'=' -f2-)"
    echo ""
fi

echo "Restarting services..."
sudo systemctl restart pmg-portal.service 2>/dev/null || true
sudo systemctl restart pmg-portal-dev.service 2>/dev/null || true

echo ""
echo "Done! Services restarted."
echo "Check status:"
echo "  sudo systemctl status pmg-portal.service"
echo "  sudo systemctl status pmg-portal-dev.service"
