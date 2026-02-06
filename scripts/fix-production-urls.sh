#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Fix production urls.py and views.py to handle missing facility views
# Path: scripts/fix-production-urls.sh
# Usage: sudo bash scripts/fix-production-urls.sh
set -euo pipefail

PROD_DIR="/opt/pmg-portal"

if [ ! -f "$PROD_DIR/src/portal/urls.py" ]; then
    echo "ERROR: Production urls.py not found at $PROD_DIR/src/portal/urls.py"
    exit 1
fi

echo "=== Fixing Production urls.py ==="

# Backup
sudo cp "$PROD_DIR/src/portal/urls.py" "$PROD_DIR/src/portal/urls.py.backup.$(date +%Y%m%d_%H%M%S)"

# Create fixed urls.py
sudo tee "$PROD_DIR/src/portal/urls.py" > /dev/null <<'EOF'
from django.urls import path
from django.conf import settings
from .views import portal_home, switch_customer, check_updates, set_language_custom

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
    path("about/check-updates/", check_updates, name="check_updates"),
    path("i18n/setlang/", set_language_custom, name="set_language_custom"),
]

# Only add facility routes if dev features are enabled and views exist
if settings.ENABLE_DEV_FEATURES:
    try:
        from .views import facility_list, facility_detail
        # Verify views exist and are callable (not stubs)
        if callable(facility_list) and callable(facility_detail):
            urlpatterns += [
                path("facilities/", facility_list, name="facility_list"),
                path("facilities/<int:pk>/", facility_detail, name="facility_detail"),
            ]
    except (ImportError, AttributeError, TypeError):
        # Views don't exist or are stubs (production/main branch), skip facility routes
        pass
EOF

echo "Production urls.py fixed!"

# Check if views.py needs fixing (has direct imports)
if grep -q "from .views import.*facility_list.*facility_detail" "$PROD_DIR/src/portal/urls.py.backup" 2>/dev/null; then
    echo "Found old urls.py with direct facility imports - fix applied"
fi

# Verify views.py has stubs
if [ -f "$PROD_DIR/src/portal/views.py" ]; then
    if grep -q "FACILITY_AVAILABLE" "$PROD_DIR/src/portal/views.py"; then
        echo "✓ views.py already has FACILITY_AVAILABLE handling"
    else
        echo "WARNING: views.py may need FACILITY_AVAILABLE stubs"
    fi
fi

echo "Restarting service..."
sudo systemctl restart pmg-portal.service
sleep 2
sudo systemctl status pmg-portal.service --no-pager -l || true

echo ""
echo "Done! Test with: curl http://localhost:8097"
