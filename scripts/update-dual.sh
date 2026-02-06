#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Update both production and development environments
# Path: scripts/update-dual.sh
# Usage: sudo bash scripts/update-dual.sh
set -euo pipefail

PROD_DIR="/opt/pmg-portal"
DEV_DIR="/opt/pmg-portal-dev"

echo "=== Updating PMG Portal (Production + Development) ==="
echo ""

# Update Production
if [ -d "$PROD_DIR" ] && [ -f "$PROD_DIR/.env" ]; then
    echo "=== Updating Production Environment ==="
    cd "$PROD_DIR"
    sudo git pull origin main
    sudo bash scripts/update.sh
    echo ""
else
    echo "Production installation not found at $PROD_DIR"
    echo "Skipping production update..."
    echo ""
fi

# Update Development
if [ -d "$DEV_DIR" ] && [ -f "$DEV_DIR/.env" ]; then
    echo "=== Updating Development Environment ==="
    cd "$DEV_DIR"
    sudo git pull origin dev
    sudo bash scripts/update.sh
    echo ""
else
    echo "Development installation not found at $DEV_DIR"
    echo "Skipping development update..."
    echo ""
fi

echo "=== Update Complete ==="
echo ""
echo "Production: sudo systemctl status pmg-portal.service"
echo "Development: sudo systemctl status pmg-portal-dev.service"
echo ""
