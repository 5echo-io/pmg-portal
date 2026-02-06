#!/usr/bin/env bash
# Purpose: Update app in-place. Automatically detects if running from production.
# Usage: sudo bash scripts/update.sh
#   OR: cd /opt/pmg-portal && sudo bash scripts/update.sh
set -euo pipefail

# Detect installation directory and branch
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -d "/opt/pmg-portal" ] && [ "$SCRIPT_DIR" = "/opt/pmg-portal" ]; then
    APP_DIR="/opt/pmg-portal"
    BRANCH="main"
    SERVICE_NAME="pmg-portal.service"
    ENV_TYPE="production"
else
    # Default to production if script is run from repo
    APP_DIR="/opt/pmg-portal"
    BRANCH="main"
    SERVICE_NAME="pmg-portal.service"
    ENV_TYPE="production"
fi

SRC_DIR="$APP_DIR/src"

echo "=== Updating $ENV_TYPE environment (branch: $BRANCH) ==="

if [ ! -d "$APP_DIR" ]; then
  echo "ERROR: $APP_DIR not found. Run install.sh first."
  exit 1
fi

# Note: Code is already updated by install.sh, so we skip git pull here
# This script only handles: dependencies, migrations, collectstatic, restart
echo "Note: Code update is handled by install.sh. This script updates dependencies and applies migrations."

sudo systemctl stop "$SERVICE_NAME" || true

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

# Cleanup branch-specific files before migrations
echo ""
echo "Cleaning up branch-specific files..."
cleanup_branch_files() {
    local install_branch="$1"
    local app_dir="$2"
    local src_dir="$app_dir/src"
    
    if [ "$install_branch" = "main" ]; then
        echo "  Removing dev-specific files for main branch..."
        
        # Remove Facility templates (dev feature)
        sudo rm -f "$src_dir/portal/templates/portal/facility_list.html" 2>/dev/null || true
        sudo rm -f "$src_dir/portal/templates/portal/facility_detail.html" 2>/dev/null || true
        sudo rm -f "$src_dir/portal/templates/portal/fragments/facility_list_content.html" 2>/dev/null || true
        sudo rm -f "$src_dir/portal/templates/portal/fragments/facility_detail_content.html" 2>/dev/null || true
        sudo rm -f "$src_dir/admin_app/templates/admin_app/facility_list.html" 2>/dev/null || true
        sudo rm -f "$src_dir/admin_app/templates/admin_app/facility_form.html" 2>/dev/null || true
        sudo rm -f "$src_dir/admin_app/templates/admin_app/facility_card.html" 2>/dev/null || true
        
        # Remove dev feature decorators
        sudo rm -f "$src_dir/portal/decorators.py" 2>/dev/null || true
        
        # Remove dev feature flags from settings.py
        if [ -f "$src_dir/pmg_portal/settings.py" ]; then
            sudo sed -i '/^# Development Feature Flags/,/^DEV_ACCESS_USERS =/d' "$src_dir/pmg_portal/settings.py" 2>/dev/null || true
            sudo sed -i '/^ENABLE_DEV_FEATURES =/d' "$src_dir/pmg_portal/settings.py" 2>/dev/null || true
            sudo sed -i '/^DEV_ACCESS_USERS =/d' "$src_dir/pmg_portal/settings.py" 2>/dev/null || true
        fi
        
        echo "  ✓ Removed dev-specific files"
    elif [ "$install_branch" = "dev" ]; then
        echo "  Ensuring dev-specific files are present..."
        # Dev branch should have all files
        echo "  ✓ Dev branch files verified"
    fi
}

cleanup_branch_files "$BRANCH" "$APP_DIR"

# Create migrations if needed
sudo -E "$SRC_DIR/.venv/bin/python" manage.py makemigrations --noinput || true

# Handle migration errors for existing tables
# If migration fails with "already exists", mark it as fake
echo "Applying migrations..."
MIGRATE_OUTPUT=$(sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput 2>&1) || {
    MIGRATE_EXIT_CODE=$?
    echo "$MIGRATE_OUTPUT"
    if echo "$MIGRATE_OUTPUT" | grep -q "already exists\|DuplicateTable\|relation.*already exists"; then
        echo ""
        echo "Warning: Some tables already exist. Attempting to fake the migration..."
        
        # Try multiple patterns to extract the migration name
        # Pattern 1: Look for "Applying portal.XXXX_..." in the output
        FAILED_MIGRATION=$(echo "$MIGRATE_OUTPUT" | grep -oE "Applying portal\.[0-9]{4}_[a-zA-Z0-9_]+" | sed 's/Applying //' | head -1)
        
        # Pattern 2: Look for "portal.XXXX_..." anywhere in the output
        if [ -z "$FAILED_MIGRATION" ]; then
            FAILED_MIGRATION=$(echo "$MIGRATE_OUTPUT" | grep -oE "portal\.[0-9]{4}_[a-zA-Z0-9_]+" | head -1)
        fi
        
        # Pattern 3: Check Django migration state for unapplied migrations
        if [ -z "$FAILED_MIGRATION" ]; then
            echo "Checking Django migration state for unapplied migrations..."
            SHOWMIGRATIONS=$(sudo -E "$SRC_DIR/.venv/bin/python" manage.py showmigrations portal 2>&1 || echo "")
            # Find the first unapplied migration (marked with [ ])
            FAILED_MIGRATION=$(echo "$SHOWMIGRATIONS" | grep -E "^\[ \]" | head -1 | sed 's/^\[ \] *//' | sed 's/^/portal./')
        fi
        
        if [ -n "$FAILED_MIGRATION" ]; then
            echo "Detected failed migration: $FAILED_MIGRATION"
            # Extract app label and migration name (format: app.0004_name)
            # Django's migrate --fake expects: migrate --fake <app_label> <migration_name>
            if echo "$FAILED_MIGRATION" | grep -qE "^[a-zA-Z_]+\.[0-9]"; then
                APP_LABEL=$(echo "$FAILED_MIGRATION" | cut -d'.' -f1)
                MIGRATION_NAME=$(echo "$FAILED_MIGRATION" | cut -d'.' -f2-)
                echo "Marking migration $APP_LABEL.$MIGRATION_NAME as fake..."
                sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --fake "$APP_LABEL" "$MIGRATION_NAME" || {
                    echo "Warning: Failed to fake migration $FAILED_MIGRATION, trying to continue..."
                }
            else
                # If format doesn't match expected pattern, try as-is
                echo "Marking migration $FAILED_MIGRATION as fake..."
                sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --fake "$FAILED_MIGRATION" || {
                    echo "Warning: Failed to fake migration $FAILED_MIGRATION, trying to continue..."
                }
            fi
            # Try migrate again after faking
            echo "Retrying migrations..."
            sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput || {
                echo "Warning: Some migrations may still need attention. Continuing with other steps..."
            }
        else
            echo "Could not determine failed migration name automatically."
            echo "Please run migrations manually:"
            echo "  cd $SRC_DIR"
            echo "  sudo -E $SRC_DIR/.venv/bin/python manage.py showmigrations"
            echo "  sudo -E $SRC_DIR/.venv/bin/python manage.py migrate --fake <migration_name>"
            echo ""
            echo "Attempting to continue with other steps..."
        fi
    else
        echo "Migration failed with an unexpected error."
        exit $MIGRATE_EXIT_CODE
    fi
}
sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0

sudo systemctl start "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager -l || true

echo ""
echo "Checking nginx configuration (if nginx is installed)..."
if command -v nginx >/dev/null 2>&1; then
    if [ -f "$APP_DIR/deploy/nginx/pmg-portal.conf" ]; then
        echo "  Updated nginx configuration template available at:"
        echo "    $APP_DIR/deploy/nginx/pmg-portal.conf"
        echo "  To apply performance optimizations, update your nginx config:"
        echo "    sudo cp $APP_DIR/deploy/nginx/pmg-portal.conf /etc/nginx/sites-available/pmg-portal"
        echo "    sudo nginx -t && sudo systemctl reload nginx"
    fi
fi

echo "Done."
