#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Fix production urls.py to handle missing facility views
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

# Create fixed version
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
echo "Restarting service..."
sudo systemctl restart pmg-portal.service
sudo systemctl status pmg-portal.service --no-pager -l || true

echo ""
echo "Done!"
