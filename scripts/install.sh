#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Intelligent installation wizard for PMG Portal
# Path: scripts/install.sh
# Usage: curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/dev/scripts/install.sh | sudo bash
set -euo pipefail

APP_NAME="pmg-portal"
APP_DIR="/opt/pmg-portal"
GITHUB_REPO="https://github.com/5echo-io/pmg-portal.git"
BRANCH="dev"
SRC_DIR="$APP_DIR/src"

# Detect branch from script URL or default to dev
# This allows the script to know which branch it's installing from
INSTALL_BRANCH="${BRANCH}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if already installed (use sudo to check since we'll need sudo anyway)
PROD_EXISTS=false
if sudo test -d "$APP_DIR" && sudo test -f "$APP_DIR/.env"; then
    PROD_EXISTS=true
fi

echo -e "${GREEN}=== PMG Portal Installation Wizard ===${NC}"
echo ""

# Determine mode based on what exists
if [ "$PROD_EXISTS" = "true" ]; then
    # Update/Uninstall mode
    echo -e "${BLUE}Existing installation detected:${NC}"
    echo "  ✓ Production: $APP_DIR"
    echo ""
    
    if [ -t 0 ] && [ -t 1 ]; then
        echo "What would you like to do?"
        echo ""
        echo "  1) Update Production (preserves database and configuration)"
        echo "  2) Reinstall Production (reinstall app, choose to keep/delete database)"
        echo "  3) Uninstall Production (choose to keep/delete database)"
        echo ""
        echo "  0) Cancel"
        echo ""
        read -rp "Enter choice [1-3, 0 to cancel]: " choice
        
        case "$choice" in
            1) 
                MODE="update"
                echo ""
                echo -e "${GREEN}Selected: Update Production${NC}"
                ;;
            2) 
                MODE="reinstall"
                echo ""
                echo -e "${YELLOW}Selected: Reinstall Production${NC}"
                ;;
            3) 
                MODE="uninstall"
                echo ""
                echo -e "${RED}Selected: Uninstall Production${NC}"
                ;;
            0|*) 
                echo "Cancelled."
                exit 0 
                ;;
        esac
    else
        # Non-interactive mode - default to update
        echo "Non-interactive mode detected. Defaulting to Update mode."
        MODE="update"
    fi
else
    # Fresh install mode
    if [ -t 0 ] && [ -t 1 ]; then
        echo -e "${GREEN}No existing installation found.${NC}"
        echo ""
        echo "Starting fresh installation..."
        MODE="install"
    else
        # Non-interactive - default to install
        MODE="install"
    fi
fi

# Helper function for prompts
prompt_default() {
  local var_name="$1"
  local prompt_text="$2"
  local default_value="$3"
  local is_secret="${4:-false}"
  local input=""

  if [ "$is_secret" = "true" ]; then
    read -rsp "$prompt_text [$default_value]: " input
    echo
  else
    read -rp "$prompt_text [$default_value]: " input
  fi

  if [ -z "$input" ]; then
    input="$default_value"
  fi

  printf -v "$var_name" "%s" "$input"
}

# Uninstall mode
if [ "$MODE" = "uninstall" ]; then
    echo -e "${RED}=== Uninstalling PMG Portal ===${NC}"
    
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
            echo "What would you like to do with the database?"
            echo "  1) Keep database and files (only remove application)"
            echo "  2) Delete everything (database, files, and application)"
            echo ""
            read -rp "Enter choice [1-2]: " db_choice
            
            if [ "$db_choice" = "2" ]; then
                if [ "${POSTGRES_HOST:-127.0.0.1}" = "127.0.0.1" ] || [ "${POSTGRES_HOST:-127.0.0.1}" = "localhost" ]; then
                    echo ""
                    echo -e "${RED}Removing Postgres database...${NC}"
                    sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"${POSTGRES_DB}\";" 2>/dev/null || true
                    sudo -u postgres psql -c "DROP USER IF EXISTS \"${POSTGRES_USER}\";" 2>/dev/null || true
                    echo -e "${GREEN}Database removed.${NC}"
                else
                    echo -e "${YELLOW}Database is on remote host ($POSTGRES_HOST). Please remove it manually.${NC}"
                fi
            else
                echo -e "${GREEN}Database preserved.${NC}"
            fi
        else
            echo "Non-interactive mode: preserving database."
        fi
        rm -f "$TEMP_ENV_BACKUP"
    fi
    
    echo ""
    echo "Stopping service..."
    sudo systemctl stop pmg-portal.service 2>/dev/null || true
    sudo systemctl disable pmg-portal.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/pmg-portal.service
    sudo systemctl daemon-reload
    
    echo "Removing application files..."
    sudo rm -rf "$APP_DIR"
    
    echo -e "${GREEN}Uninstall complete!${NC}"
    exit 0
fi

# Reinstall mode
if [ "$MODE" = "reinstall" ]; then
    echo -e "${YELLOW}=== Reinstalling PMG Portal ===${NC}"
    
    # Backup .env and ask about database
    TEMP_ENV_BACKUP=""
    KEEP_DB=true
    if [ -f "$APP_DIR/.env" ]; then
        TEMP_ENV_BACKUP=$(mktemp)
        sudo cp "$APP_DIR/.env" "$TEMP_ENV_BACKUP"
        set -a
        source "$APP_DIR/.env"
        set +a
        
        echo ""
        if [ -t 0 ] && [ -t 1 ]; then
            echo "What would you like to do with the database?"
            echo "  1) Keep existing database (recommended)"
            echo "  2) Delete and recreate database (WARNING: All data will be lost!)"
            echo ""
            read -rp "Enter choice [1-2]: " db_choice
            
            if [ "$db_choice" = "2" ]; then
                KEEP_DB=false
                if [ "${POSTGRES_HOST:-127.0.0.1}" = "127.0.0.1" ] || [ "${POSTGRES_HOST:-127.0.0.1}" = "localhost" ]; then
                    echo ""
                    echo -e "${RED}WARNING: This will delete the database and all data!${NC}"
                    read -rp "Type 'yes' to confirm: " confirm
                    if [ "$confirm" != "yes" ]; then
                        echo "Cancelled."
                        exit 0
                    fi
                    echo "Deleting database..."
                    sudo systemctl stop pmg-portal.service 2>/dev/null || true
                    sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"${POSTGRES_DB}\";" 2>/dev/null || true
                else
                    echo -e "${YELLOW}Database is on remote host ($POSTGRES_HOST). Please delete it manually.${NC}"
                fi
            else
                echo -e "${GREEN}Database will be preserved.${NC}"
            fi
        fi
    fi
    
    # Stop service
    sudo systemctl stop pmg-portal.service 2>/dev/null || true
    
    # Remove application files (but keep .env backup)
    echo "Removing application files..."
    sudo rm -rf "$APP_DIR/src" "$APP_DIR/scripts" "$APP_DIR/deploy" "$APP_DIR/media" 2>/dev/null || true
    sudo rm -f "$APP_DIR"/*.md "$APP_DIR"/*.txt "$APP_DIR/.gitignore" 2>/dev/null || true
    
    # Continue with install (will recreate everything)
    MODE="install"
fi

# Update mode
if [ "$MODE" = "update" ]; then
    echo -e "${GREEN}=== Updating PMG Portal ===${NC}"
    
    # Download latest code from dev branch (always fresh clone)
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    
    echo "Downloading latest code from dev branch..."
    rm -rf "$TEMP_DIR/pmg-portal" 2>/dev/null || true
    git clone -b "$BRANCH" "$GITHUB_REPO" "$TEMP_DIR/pmg-portal"
    REPO_DIR="$TEMP_DIR/pmg-portal"
    
    # Preserve .env and .venv
    if [ -f "$APP_DIR/.env" ]; then
        echo "Preserving existing .env file..."
        sudo cp "$APP_DIR/.env" "$TEMP_DIR/.env.backup"
    fi
    
    # Stop service
    echo "Stopping service..."
    sudo systemctl stop pmg-portal.service || true
    
    # Update files (preserve .env, .venv, media, and database)
    echo "Updating application files (preserving .env, .venv, media, and database)..."
    # Use rsync with --delete to ensure all files are synced, including templates
    sudo rsync -a --delete --exclude='.env' --exclude='.venv' --exclude='staticfiles' --exclude='media' --exclude='*.pyc' --exclude='__pycache__' "$REPO_DIR/" "$APP_DIR/"
    
    # Cleanup branch-specific files after update
    echo ""
    echo "Cleaning up branch-specific files..."
    cleanup_branch_files() {
        local install_branch="$1"
        local app_dir="$2"
        local src_dir="$app_dir/src"
        
        if [ "$install_branch" = "main" ]; then
            echo "  Removing dev-specific files for main branch..."
            
            # Note: Facility templates are now production-ready and kept for both HTMX and regular requests
            # Portal facility templates are kept:
            # - portal/templates/portal/facility_list.html
            # - portal/templates/portal/facility_detail.html
            # - portal/templates/portal/fragments/facility_list_content.html
            # - portal/templates/portal/fragments/facility_detail_content.html
            
            # Remove admin_app Facility templates (admin-only, under facility/ subdir)
            # sudo rm -f "$src_dir/admin_app/templates/admin_app/facility/facility_list.html" 2>/dev/null || true
            # sudo rm -f "$src_dir/admin_app/templates/admin_app/facility/facility_form.html" 2>/dev/null || true
            # sudo rm -f "$src_dir/admin_app/templates/admin_app/facility/facility_card.html" 2>/dev/null || true
            
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
            # Dev branch should have all files - verify Facility templates exist
            if [ ! -f "$src_dir/portal/templates/portal/facility_list.html" ]; then
                echo "  WARNING: Facility templates missing - they should be in the repository"
            fi
            echo "  ✓ Dev branch files verified"
        fi
    }
    
    cleanup_branch_files "$BRANCH" "$APP_DIR"
    
    # Restore .env
    if [ -f "$TEMP_DIR/.env.backup" ]; then
        sudo cp "$TEMP_DIR/.env.backup" "$APP_DIR/.env"
        echo "✓ Configuration preserved"
    fi
    
    # Run update steps (migrations, collectstatic, etc.)
    echo ""
    echo "Running update steps..."
    sudo bash "$APP_DIR/scripts/update.sh"
    
    echo ""
    echo -e "${GREEN}Update complete!${NC}"
    echo "Database and configuration have been preserved."
    exit 0
fi

# Install mode (fresh install or reinstall)
echo -e "${GREEN}=== Installing PMG Portal ===${NC}"

# Download from dev branch (always fresh clone)
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Downloading development code from dev branch..."
rm -rf "$TEMP_DIR/pmg-portal" 2>/dev/null || true
git clone -b "$BRANCH" "$GITHUB_REPO" "$TEMP_DIR/pmg-portal"
REPO_DIR="$TEMP_DIR/pmg-portal"

# Install OS dependencies
echo ""
# Install OS dependencies (postgresql-client for Backup & Restore; pkg-config+libcairo2-dev for xhtml2pdf/svglib/pycairo)
echo "Installing OS dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-client rsync gettext libjpeg-dev libpng-dev zlib1g-dev git pkg-config libcairo2-dev

# Copy files
echo ""
echo "Installing application files..."
sudo mkdir -p "$APP_DIR"
# Use rsync with --delete to ensure all files are synced, including templates
sudo rsync -a --delete --exclude='.git' "$REPO_DIR/" "$APP_DIR/"

# Cleanup branch-specific files
echo ""
echo "Cleaning up branch-specific files..."
cleanup_branch_files() {
    local install_branch="$1"
    local app_dir="$2"
    local src_dir="$app_dir/src"
    
    if [ "$install_branch" = "main" ]; then
        echo "  Removing dev-specific files for main branch..."
        
        # Note: Facility templates are now production-ready and kept for both HTMX and regular requests
        # Portal facility templates are kept:
        # - portal/templates/portal/facility_list.html
        # - portal/templates/portal/facility_detail.html
        # - portal/templates/portal/fragments/facility_list_content.html
        # - portal/templates/portal/fragments/facility_detail_content.html
        
        # Remove admin_app Facility templates (admin-only, under facility/ subdir)
        # sudo rm -f "$src_dir/admin_app/templates/admin_app/facility/facility_list.html" 2>/dev/null || true
        # sudo rm -f "$src_dir/admin_app/templates/admin_app/facility/facility_form.html" 2>/dev/null || true
        # sudo rm -f "$src_dir/admin_app/templates/admin_app/facility/facility_card.html" 2>/dev/null || true
        
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
        # Dev branch should have all files, but we can remove any main-specific cleanup scripts if needed
        # Currently no main-specific files to remove
        echo "  ✓ Dev branch files verified"
    fi
}

cleanup_branch_files "$BRANCH" "$APP_DIR"

# Run install wizard (.env configuration)
echo ""
echo "=== Configuration Wizard ==="

# Load existing .env if reinstalling
if [ -f "$TEMP_ENV_BACKUP" ]; then
    echo "Loading existing configuration..."
    set -a
    source "$TEMP_ENV_BACKUP"
    set +a
    USE_EXISTING=true
else
    USE_EXISTING=false
fi

DJANGO_SECRET_KEY_DEFAULT="${DJANGO_SECRET_KEY:-}"
DJANGO_DEBUG_DEFAULT="${DJANGO_DEBUG:-false}"
DJANGO_ALLOWED_HOSTS_DEFAULT="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1}"
ENABLE_REGISTRATION_DEFAULT="${ENABLE_REGISTRATION:-true}"
DEFAULT_ADMIN_USERNAME_DEFAULT="${DEFAULT_ADMIN_USERNAME:-admin}"
DEFAULT_ADMIN_EMAIL_DEFAULT="${DEFAULT_ADMIN_EMAIL:-admin@example.com}"
DEFAULT_ADMIN_PASSWORD_DEFAULT="${DEFAULT_ADMIN_PASSWORD:-admin}"
POSTGRES_HOST_DEFAULT="${POSTGRES_HOST:-127.0.0.1}"
POSTGRES_PORT_DEFAULT="${POSTGRES_PORT:-5432}"
POSTGRES_DB_DEFAULT="${POSTGRES_DB:-pmg_portal}"
POSTGRES_USER_DEFAULT="${POSTGRES_USER:-pmg_portal}"
POSTGRES_PASSWORD_DEFAULT="${POSTGRES_PASSWORD:-change-me}"
APP_BIND_DEFAULT="${APP_BIND:-0.0.0.0:8097}"

if [ "$USE_EXISTING" = "true" ]; then
    echo "Using existing configuration. Press Enter to keep current values or type new values."
    echo ""
fi

prompt_default DJANGO_SECRET_KEY "DJANGO_SECRET_KEY (leave blank to auto-generate)" "$DJANGO_SECRET_KEY_DEFAULT"
if [ -z "$DJANGO_SECRET_KEY" ]; then
  DJANGO_SECRET_KEY="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
fi
prompt_default DJANGO_DEBUG "DJANGO_DEBUG (true/false)" "$DJANGO_DEBUG_DEFAULT"
prompt_default DJANGO_ALLOWED_HOSTS "DJANGO_ALLOWED_HOSTS (comma-separated, e.g. portal.example.com,localhost,127.0.0.1)" "$DJANGO_ALLOWED_HOSTS_DEFAULT"
prompt_default ENABLE_REGISTRATION "ENABLE_REGISTRATION (true/false)" "$ENABLE_REGISTRATION_DEFAULT"
prompt_default DEFAULT_ADMIN_EMAIL "DEFAULT_ADMIN_EMAIL (login email for first admin)" "$DEFAULT_ADMIN_EMAIL_DEFAULT"
# Username is set from email on create (email-as-primary); kept for .env backward compatibility
DEFAULT_ADMIN_USERNAME="${DEFAULT_ADMIN_USERNAME:-$DEFAULT_ADMIN_EMAIL}"
prompt_default DEFAULT_ADMIN_PASSWORD "DEFAULT_ADMIN_PASSWORD" "$DEFAULT_ADMIN_PASSWORD_DEFAULT" true
prompt_default POSTGRES_HOST "POSTGRES_HOST" "$POSTGRES_HOST_DEFAULT"
prompt_default POSTGRES_PORT "POSTGRES_PORT" "$POSTGRES_PORT_DEFAULT"
prompt_default POSTGRES_DB "POSTGRES_DB" "$POSTGRES_DB_DEFAULT"
prompt_default POSTGRES_USER "POSTGRES_USER" "$POSTGRES_USER_DEFAULT"
prompt_default POSTGRES_PASSWORD "POSTGRES_PASSWORD" "$POSTGRES_PASSWORD_DEFAULT" true
prompt_default APP_BIND "APP_BIND" "$APP_BIND_DEFAULT"

echo ""
echo "Writing $APP_DIR/.env"
sudo tee "$APP_DIR/.env" >/dev/null <<EOF
# --- App ---
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=$DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS=$DJANGO_ALLOWED_HOSTS

# If true, registration page is enabled
ENABLE_REGISTRATION=$ENABLE_REGISTRATION

# Default admin bootstrap (created on install if missing). Login uses email; username is set from email.
DEFAULT_ADMIN_USERNAME=$DEFAULT_ADMIN_USERNAME
DEFAULT_ADMIN_EMAIL=$DEFAULT_ADMIN_EMAIL
DEFAULT_ADMIN_PASSWORD=$DEFAULT_ADMIN_PASSWORD

# --- Postgres ---
POSTGRES_HOST=$POSTGRES_HOST
POSTGRES_PORT=$POSTGRES_PORT
POSTGRES_DB=$POSTGRES_DB
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# --- Runtime ---
APP_BIND=$APP_BIND
EOF

escape_psql_literal() {
  printf "%s" "$1" | sed "s/'/''/g"
}

escape_psql_identifier() {
  printf "%s" "$1" | sed 's/"/""/g'
}

# Database setup (only if not keeping existing database or fresh install)
if [ "${KEEP_DB:-false}" != "true" ]; then
    if [ "$POSTGRES_HOST" = "127.0.0.1" ] || [ "$POSTGRES_HOST" = "localhost" ]; then
        echo ""
        echo "Configuring local Postgres..."
        sudo systemctl enable --now postgresql
        db_user_ident="$(escape_psql_identifier "$POSTGRES_USER")"
        db_name_ident="$(escape_psql_identifier "$POSTGRES_DB")"
        db_user_lit="$(escape_psql_literal "$POSTGRES_USER")"
        db_pass_lit="$(escape_psql_literal "$POSTGRES_PASSWORD")"
        db_name_lit="$(escape_psql_literal "$POSTGRES_DB")"

        role_exists="$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname = '${db_user_lit}'")"
        if [ "$role_exists" != "1" ]; then
            sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE USER \"${db_user_ident}\" WITH PASSWORD '${db_pass_lit}';"
        else
            sudo -u postgres psql -v ON_ERROR_STOP=1 -c "ALTER USER \"${db_user_ident}\" WITH PASSWORD '${db_pass_lit}';"
        fi

        db_exists="$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = '${db_name_lit}'")"
        if [ "$db_exists" != "1" ]; then
            sudo -u postgres psql -v ON_ERROR_STOP=1 -c "CREATE DATABASE \"${db_name_ident}\" OWNER \"${db_user_ident}\";"
            echo "✓ Database created"
        else
            echo "✓ Database already exists (preserved)"
        fi
    else
        echo "Skipping local Postgres setup (host: $POSTGRES_HOST)."
    fi
else
    echo ""
    echo "✓ Database preserved (existing database will be used)"
fi

echo ""
echo "Creating virtual environment..."
cd "$SRC_DIR"
if [ ! -d "$SRC_DIR/.venv" ]; then
    sudo python3 -m venv "$SRC_DIR/.venv"
fi
sudo "$SRC_DIR/.venv/bin/pip" install --upgrade pip
sudo "$SRC_DIR/.venv/bin/pip" install -r "$SRC_DIR/requirements.txt"

echo ""
echo "Creating media directory..."
MEDIA_DIR="$APP_DIR/media"
sudo mkdir -p "$MEDIA_DIR"
SERVICE_USER="root"  # Default from pmg-portal.service
if [ -f "$APP_DIR/deploy/systemd/pmg-portal.service" ]; then
    EXTRACTED_USER=$(grep -E "^User=" "$APP_DIR/deploy/systemd/pmg-portal.service" | cut -d'=' -f2 | tr -d ' ' || echo "")
    if [ -n "$EXTRACTED_USER" ]; then
        SERVICE_USER="$EXTRACTED_USER"
    fi
fi
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$MEDIA_DIR"
sudo chmod -R 755 "$MEDIA_DIR"

echo ""
echo "Running migrations + collectstatic + compilemessages..."
set -a
source "$APP_DIR/.env"
set +a

# Create migrations if needed, then apply them
sudo -E "$SRC_DIR/.venv/bin/python" manage.py makemigrations --noinput || true
sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput
# Record installed app version for backwards-compatibility checks (upgrade/downgrade)
sudo -E "$SRC_DIR/.venv/bin/python" manage.py set_stored_version
sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0

echo ""
echo "Creating default admin (if missing)..."
sudo -E "$SRC_DIR/.venv/bin/python" - <<'PY'
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmg_portal.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()
email = (os.getenv("DEFAULT_ADMIN_EMAIL") or "admin@example.com").strip()
username = email[:150]  # Email-as-primary: username must equal email for login
password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")

if not User.objects.filter(is_superuser=True).exists():
    u = User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser: {email}")
else:
    print("Superuser already exists, skipping.")
PY

echo ""
echo "Installing systemd service..."
sudo cp "$APP_DIR/deploy/systemd/pmg-portal.service" /etc/systemd/system/pmg-portal.service
sudo systemctl daemon-reload
sudo systemctl enable --now pmg-portal.service

echo ""
echo "Updating nginx configuration (if nginx is installed)..."
if command -v nginx >/dev/null 2>&1; then
    if [ -f "$APP_DIR/deploy/nginx/pmg-portal.conf" ]; then
        echo "  Found nginx configuration template."
        echo "  To apply performance optimizations, copy it manually:"
        echo "    sudo cp $APP_DIR/deploy/nginx/pmg-portal.conf /etc/nginx/sites-available/pmg-portal"
        echo "    sudo nginx -t && sudo systemctl reload nginx"
    fi
else
    echo "  Nginx not installed (optional - for production deployments)"
fi

echo ""
echo -e "${GREEN}=== Installation Complete! ===${NC}"
echo ""
echo "Application URL: http://$APP_BIND"
echo "Admin login: $DEFAULT_ADMIN_EMAIL"
echo ""
echo "View logs: sudo journalctl -u pmg-portal.service -f --no-pager"
echo ""
