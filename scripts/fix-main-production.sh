#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Fix main branch production installation (remove facility imports, fix staticfiles)
# Path: scripts/fix-main-production.sh
# Usage: sudo bash scripts/fix-main-production.sh
set -euo pipefail

PROD_DIR="/opt/pmg-portal"
SRC_DIR="$PROD_DIR/src"

if [ ! -d "$PROD_DIR" ]; then
    echo "ERROR: Production directory not found at $PROD_DIR"
    exit 1
fi

echo "=== Fixing Production Installation (v2.0.0) ==="

# Backup files
echo "Backing up files..."
sudo cp "$SRC_DIR/portal/views.py" "$SRC_DIR/portal/views.py.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
sudo cp "$SRC_DIR/portal/urls.py" "$SRC_DIR/portal/urls.py.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

# Fix views.py - remove Facility import
echo "Fixing views.py..."
if grep -q "from .models import.*Facility" "$SRC_DIR/portal/views.py" 2>/dev/null; then
    sudo sed -i 's/from \.models import CustomerMembership, Customer, Facility/from .models import CustomerMembership, Customer/' "$SRC_DIR/portal/views.py"
    echo "✓ Removed Facility import from views.py"
else
    echo "✓ views.py already correct (no Facility import)"
fi

# Fix urls.py - ensure no facility imports
echo "Fixing urls.py..."
sudo tee "$SRC_DIR/portal/urls.py" > /dev/null <<'EOF'
from django.urls import path
from .views import portal_home, switch_customer, check_updates, set_language_custom

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
    path("about/check-updates/", check_updates, name="check_updates"),
    path("i18n/setlang/", set_language_custom, name="set_language_custom"),
]
EOF
echo "✓ Fixed urls.py"

# Stop service
echo "Stopping service..."
sudo systemctl stop pmg-portal.service || true

# Fix staticfiles
echo "Fixing staticfiles..."
set -a
source "$PROD_DIR/.env"
set +a

cd "$SRC_DIR"
sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput --clear
echo "✓ Staticfiles collected"

# Restart service
echo "Restarting service..."
sudo systemctl start pmg-portal.service
sleep 2
sudo systemctl status pmg-portal.service --no-pager -l || true

echo ""
echo "=== Fix Complete ==="
echo "Test with: curl http://localhost:8097"
