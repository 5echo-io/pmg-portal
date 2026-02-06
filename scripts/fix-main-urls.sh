#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Fix main branch urls.py to remove facility imports for v2.0.0
# Path: scripts/fix-main-urls.sh
# Usage: sudo bash scripts/fix-main-urls.sh
set -euo pipefail

PROD_DIR="/opt/pmg-portal"

if [ ! -f "$PROD_DIR/src/portal/urls.py" ]; then
    echo "ERROR: Production urls.py not found at $PROD_DIR/src/portal/urls.py"
    exit 1
fi

echo "=== Fixing Production urls.py (v2.0.0) ==="

# Backup
sudo cp "$PROD_DIR/src/portal/urls.py" "$PROD_DIR/src/portal/urls.py.backup.$(date +%Y%m%d_%H%M%S)"

# Create fixed version without facility imports
sudo tee "$PROD_DIR/src/portal/urls.py" > /dev/null <<'EOF'
from django.urls import path
from .views import portal_home, switch_customer, check_updates, set_language_custom

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
    path("about/check-updates/", check_updates, name="check_updates"),
    path("i18n/setlang/", set_language_custom, name="set_language_custom"),
]
EOF

echo "Production urls.py fixed!"
echo "Restarting service..."
sudo systemctl restart pmg-portal.service
sleep 2
sudo systemctl status pmg-portal.service --no-pager -l || true

echo ""
echo "Done! Test with: curl http://localhost:8097"
