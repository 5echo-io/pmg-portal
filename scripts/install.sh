#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Install on Ubuntu (wizard, deps, migrations, admin, systemd)
# Path: scripts/install.sh
set -euo pipefail

APP_NAME="pmg-portal"
PROD_DIR="/opt/pmg-portal"
DEV_DIR="/opt/pmg-portal-dev"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GITHUB_REPO="https://github.com/5echo-io/pmg-portal.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check what's already installed
PROD_EXISTS=false
DEV_EXISTS=false

if [ -d "$PROD_DIR" ] && [ -f "$PROD_DIR/.env" ]; then
    PROD_EXISTS=true
fi

if [ -d "$DEV_DIR" ] && [ -f "$DEV_DIR/.env" ]; then
    DEV_EXISTS=true
fi

echo -e "${GREEN}=== PMG Portal Installation Wizard ===${NC}"
echo ""

# Determine mode based on what exists
if [ "$PROD_EXISTS" = "true" ] || [ "$DEV_EXISTS" = "true" ]; then
    # Update/Uninstall mode
    echo "Existing installation(s) detected:"
    if [ "$PROD_EXISTS" = "true" ]; then
        echo "  ✓ Production: $PROD_DIR"
    fi
    if [ "$DEV_EXISTS" = "true" ]; then
        echo "  ✓ Development: $DEV_DIR"
    fi
    echo ""
    
    if [ -t 0 ] && [ -t 1 ]; then
        echo "What would you like to do?"
        echo ""
        
        if [ "$PROD_EXISTS" = "true" ]; then
            echo "Production:"
            echo "  1) Update Production (from main branch)"
            echo "  2) Uninstall Production"
        fi
        
        if [ "$DEV_EXISTS" = "true" ]; then
            echo "Development:"
            echo "  3) Update Development (from dev branch)"
            echo "  4) Uninstall Development"
        fi
        
        if [ "$PROD_EXISTS" = "false" ] || [ "$DEV_EXISTS" = "false" ]; then
            echo "Install:"
            if [ "$PROD_EXISTS" = "false" ]; then
                echo "  5) Install Production only"
            fi
            if [ "$DEV_EXISTS" = "false" ]; then
                echo "  6) Install Development only"
            fi
            if [ "$PROD_EXISTS" = "false" ] && [ "$DEV_EXISTS" = "false" ]; then
                echo "  7) Install Production & Development"
            fi
        fi
        
        echo ""
        echo "  0) Cancel"
        echo ""
        read -rp "Enter choice: " choice
    else
        # Non-interactive mode - default to update
        if [ "$PROD_EXISTS" = "true" ]; then
            choice="1"
        elif [ "$DEV_EXISTS" = "true" ]; then
            choice="3"
        else
            choice="0"
        fi
    fi
    
    case "$choice" in
        1)
            if [ "$PROD_EXISTS" = "true" ]; then
                MODE="update_prod"
            else
                echo -e "${RED}Production not installed.${NC}"
                exit 1
            fi
            ;;
        2)
            if [ "$PROD_EXISTS" = "true" ]; then
                MODE="uninstall_prod"
            else
                echo -e "${RED}Production not installed.${NC}"
                exit 1
            fi
            ;;
        3)
            if [ "$DEV_EXISTS" = "true" ]; then
                MODE="update_dev"
            else
                echo -e "${RED}Development not installed.${NC}"
                exit 1
            fi
            ;;
        4)
            if [ "$DEV_EXISTS" = "true" ]; then
                MODE="uninstall_dev"
            else
                echo -e "${RED}Development not installed.${NC}"
                exit 1
            fi
            ;;
        5)
            if [ "$PROD_EXISTS" = "false" ]; then
                MODE="install_prod"
            else
                echo -e "${RED}Production already installed.${NC}"
                exit 1
            fi
            ;;
        6)
            if [ "$DEV_EXISTS" = "false" ]; then
                MODE="install_dev"
            else
                echo -e "${RED}Development already installed.${NC}"
                exit 1
            fi
            ;;
        7)
            if [ "$PROD_EXISTS" = "false" ] && [ "$DEV_EXISTS" = "false" ]; then
                MODE="install_both"
            else
                echo -e "${RED}One or both installations already exist.${NC}"
                exit 1
            fi
            ;;
        0|*)
            echo "Cancelled."
            exit 0
            ;;
    esac
else
    # Fresh install mode
    if [ -t 0 ] && [ -t 1 ]; then
        echo "No existing installation found."
        echo ""
        echo "What would you like to install?"
        echo "  1) Production only (main branch)"
        echo "  2) Development only (dev branch)"
        echo "  3) Production & Development (both)"
        echo "  0) Cancel"
        echo ""
        read -rp "Enter choice: " choice
        
        case "$choice" in
            1) MODE="install_prod" ;;
            2) MODE="install_dev" ;;
            3) MODE="install_both" ;;
            0|*) echo "Cancelled."; exit 0 ;;
        esac
    else
        # Non-interactive - default to production only
        MODE="install_prod"
    fi
fi

# Helper functions
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

escape_psql_literal() {
    printf "%s" "$1" | sed "s/'/''/g"
}

escape_psql_identifier() {
    printf "%s" "$1" | sed 's/"/""/g'
}

# Function to install production
install_production() {
    local APP_DIR="$PROD_DIR"
    local SRC_DIR="$APP_DIR/src"
    local BRANCH="main"
    
    echo ""
    echo -e "${GREEN}=== Installing Production Environment ===${NC}"
    
    # Download from main branch
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    
    echo "Downloading production code from main branch..."
    git clone -b "$BRANCH" "$GITHUB_REPO" "$TEMP_DIR/pmg-portal"
    REPO_DIR="$TEMP_DIR/pmg-portal"
    
    # Install OS dependencies
    echo "Installing OS dependencies..."
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-client rsync gettext libjpeg-dev libpng-dev zlib1g-dev
    
    # Copy files
    echo "Installing application files..."
    sudo mkdir -p "$APP_DIR"
    sudo rsync -a --exclude='.git' "$REPO_DIR/" "$APP_DIR/"
    
    # Run install wizard
    run_install_wizard "$APP_DIR" "$SRC_DIR" "production" false
    
    # Setup systemd service
    echo "Installing systemd service..."
    sudo cp "$APP_DIR/deploy/systemd/pmg-portal.service" /etc/systemd/system/pmg-portal.service
    sudo systemctl daemon-reload
    sudo systemctl enable --now pmg-portal.service
    
    echo -e "${GREEN}Production installation complete!${NC}"
}

# Function to install development
install_development() {
    local APP_DIR="$DEV_DIR"
    local SRC_DIR="$APP_DIR/src"
    local BRANCH="dev"
    
    echo ""
    echo -e "${GREEN}=== Installing Development Environment ===${NC}"
    
    # Download from dev branch
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT
    
    echo "Downloading development code from dev branch..."
    git clone -b "$BRANCH" "$GITHUB_REPO" "$TEMP_DIR/pmg-portal-dev"
    REPO_DIR="$TEMP_DIR/pmg-portal-dev"
    
    # Install OS dependencies
    echo "Installing OS dependencies..."
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-client rsync gettext libjpeg-dev libpng-dev zlib1g-dev
    
    # Copy files
    echo "Installing application files..."
    sudo mkdir -p "$APP_DIR"
    sudo rsync -a --exclude='.git' "$REPO_DIR/" "$APP_DIR/"
    
    # Run install wizard
    run_install_wizard "$APP_DIR" "$SRC_DIR" "development" true
    
    # Setup systemd service
    echo "Installing systemd service..."
    sudo tee /etc/systemd/system/pmg-portal-dev.service > /dev/null <<EOF
[Unit]
Description=PMG Portal Development (Gunicorn)
After=network.target

[Service]
Type=simple
WorkingDirectory=$SRC_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$SRC_DIR/.venv/bin/gunicorn pmg_portal.wsgi:application --bind \${APP_BIND} --workers 2 --access-logfile -
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable --now pmg-portal-dev.service
    
    echo -e "${GREEN}Development installation complete!${NC}"
}

# Function to run install wizard
run_install_wizard() {
    local APP_DIR="$1"
    local SRC_DIR="$2"
    local ENV_TYPE="$3"
    local IS_DEV="$4"
    
    echo ""
    echo "=== Install wizard (.env) for $ENV_TYPE ==="
    
    # Load existing .env if it exists
    if [ -f "$APP_DIR/.env" ]; then
        echo "Existing .env found. Using it as defaults."
        set -a
        source "$APP_DIR/.env"
        set +a
    fi
    
    # Set defaults
    DJANGO_SECRET_KEY_DEFAULT="${DJANGO_SECRET_KEY:-}"
    DJANGO_DEBUG_DEFAULT="${DJANGO_DEBUG:-false}"
    DJANGO_ALLOWED_HOSTS_DEFAULT="${DJANGO_ALLOWED_HOSTS:-localhost,127.0.0.1}"
    ENABLE_REGISTRATION_DEFAULT="${ENABLE_REGISTRATION:-true}"
    DEFAULT_ADMIN_USERNAME_DEFAULT="${DEFAULT_ADMIN_USERNAME:-admin}"
    DEFAULT_ADMIN_EMAIL_DEFAULT="${DEFAULT_ADMIN_EMAIL:-admin@example.com}"
    DEFAULT_ADMIN_PASSWORD_DEFAULT="${DEFAULT_ADMIN_PASSWORD:-admin}"
    POSTGRES_HOST_DEFAULT="${POSTGRES_HOST:-127.0.0.1}"
    POSTGRES_PORT_DEFAULT="${POSTGRES_PORT:-5432}"
    
    if [ "$IS_DEV" = "true" ]; then
        POSTGRES_DB_DEFAULT="${POSTGRES_DB:-pmg_portal_dev}"
        POSTGRES_USER_DEFAULT="${POSTGRES_USER:-pmg_portal_dev}"
        APP_BIND_DEFAULT="${APP_BIND:-0.0.0.0:8098}"
        ENABLE_DEV_FEATURES_DEFAULT="true"
    else
        POSTGRES_DB_DEFAULT="${POSTGRES_DB:-pmg_portal}"
        POSTGRES_USER_DEFAULT="${POSTGRES_USER:-pmg_portal}"
        APP_BIND_DEFAULT="${APP_BIND:-0.0.0.0:8097}"
        ENABLE_DEV_FEATURES_DEFAULT="${ENABLE_DEV_FEATURES:-false}"
    fi
    
    POSTGRES_PASSWORD_DEFAULT="${POSTGRES_PASSWORD:-change-me}"
    DEV_ACCESS_USERS_DEFAULT="${DEV_ACCESS_USERS:-}"
    
    # Prompt for values
    prompt_default DJANGO_SECRET_KEY "DJANGO_SECRET_KEY (leave blank to auto-generate)" "$DJANGO_SECRET_KEY_DEFAULT"
    if [ -z "$DJANGO_SECRET_KEY" ]; then
        DJANGO_SECRET_KEY="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
    fi
    
    prompt_default DJANGO_DEBUG "DJANGO_DEBUG (true/false)" "$DJANGO_DEBUG_DEFAULT"
    prompt_default DJANGO_ALLOWED_HOSTS "DJANGO_ALLOWED_HOSTS (comma-separated, e.g. portal.parkmediagroup.no,localhost,127.0.0.1)" "$DJANGO_ALLOWED_HOSTS_DEFAULT"
    
    # Auto-generate dev subdomain if domain is provided
    DEV_ALLOWED_HOSTS="$DJANGO_ALLOWED_HOSTS"
    if [ "$IS_DEV" = "true" ]; then
        FIRST_DOMAIN=$(echo "$DJANGO_ALLOWED_HOSTS" | cut -d',' -f1 | tr -d ' ')
        if [ "$FIRST_DOMAIN" != "localhost" ] && [ "$FIRST_DOMAIN" != "127.0.0.1" ] && [[ ! "$FIRST_DOMAIN" =~ ^dev\. ]]; then
            DEV_ALLOWED_HOSTS="dev.$FIRST_DOMAIN,$DJANGO_ALLOWED_HOSTS"
            echo "Auto-generated dev subdomain: dev.$FIRST_DOMAIN"
        fi
    fi
    
    prompt_default ENABLE_REGISTRATION "ENABLE_REGISTRATION (true/false)" "$ENABLE_REGISTRATION_DEFAULT"
    prompt_default DEFAULT_ADMIN_EMAIL "DEFAULT_ADMIN_EMAIL (login email for first admin)" "$DEFAULT_ADMIN_EMAIL_DEFAULT"
    DEFAULT_ADMIN_USERNAME="${DEFAULT_ADMIN_USERNAME:-$DEFAULT_ADMIN_EMAIL}"
    prompt_default DEFAULT_ADMIN_PASSWORD "DEFAULT_ADMIN_PASSWORD" "$DEFAULT_ADMIN_PASSWORD_DEFAULT" true
    prompt_default POSTGRES_HOST "POSTGRES_HOST" "$POSTGRES_HOST_DEFAULT"
    prompt_default POSTGRES_PORT "POSTGRES_PORT" "$POSTGRES_PORT_DEFAULT"
    prompt_default POSTGRES_DB "POSTGRES_DB" "$POSTGRES_DB_DEFAULT"
    prompt_default POSTGRES_USER "POSTGRES_USER" "$POSTGRES_USER_DEFAULT"
    prompt_default POSTGRES_PASSWORD "POSTGRES_PASSWORD" "$POSTGRES_PASSWORD_DEFAULT" true
    prompt_default APP_BIND "APP_BIND" "$APP_BIND_DEFAULT"
    
    if [ "$IS_DEV" = "true" ]; then
        ENABLE_DEV_FEATURES="true"
        echo "ENABLE_DEV_FEATURES set to true (required for development environment)"
    else
        prompt_default ENABLE_DEV_FEATURES "ENABLE_DEV_FEATURES (true/false - enable development features like Facility management, admin only)" "$ENABLE_DEV_FEATURES_DEFAULT"
    fi
    
    prompt_default DEV_ACCESS_USERS "DEV_ACCESS_USERS (comma-separated emails/usernames, leave empty for all superusers)" "$DEV_ACCESS_USERS_DEFAULT"
    
    # Write .env file
    echo "Writing $APP_DIR/.env"
    sudo tee "$APP_DIR/.env" >/dev/null <<EOF
# --- App ---
DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY
DJANGO_DEBUG=$DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS=$DEV_ALLOWED_HOSTS

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

# --- Development Features ---
# Enable development features (Facility management, etc.) - admin/superuser only
ENABLE_DEV_FEATURES=$ENABLE_DEV_FEATURES
# Restrict dev access to specific superusers (leave empty for all superusers)
DEV_ACCESS_USERS=$DEV_ACCESS_USERS
EOF
    
    # Setup database
    if [ "$POSTGRES_HOST" = "127.0.0.1" ] || [ "$POSTGRES_HOST" = "localhost" ]; then
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
        fi
    else
        echo "Skipping local Postgres setup (host: $POSTGRES_HOST)."
    fi
    
    # Create venv
    echo "Creating venv..."
    cd "$SRC_DIR"
    sudo python3 -m venv "$SRC_DIR/.venv"
    sudo "$SRC_DIR/.venv/bin/pip" install --upgrade pip
    sudo "$SRC_DIR/.venv/bin/pip" install -r "$SRC_DIR/requirements.txt"
    
    # Create media directory
    echo "Creating media directory..."
    MEDIA_DIR="$APP_DIR/media"
    sudo mkdir -p "$MEDIA_DIR"
    SERVICE_USER="root"
    if [ -f "$APP_DIR/deploy/systemd/pmg-portal.service" ]; then
        EXTRACTED_USER=$(grep -E "^User=" "$APP_DIR/deploy/systemd/pmg-portal.service" | cut -d'=' -f2 | tr -d ' ' || echo "")
        if [ -n "$EXTRACTED_USER" ]; then
            SERVICE_USER="$EXTRACTED_USER"
        fi
    fi
    sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$MEDIA_DIR"
    sudo chmod -R 755 "$MEDIA_DIR"
    
    # Run migrations
    echo "Running migrations + collectstatic + compilemessages..."
    set -a
    source "$APP_DIR/.env"
    set +a
    
    sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput
    sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
    sudo -E "$SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0
    
    # Create admin
    echo "Creating default admin (if missing)..."
    sudo -E "$SRC_DIR/.venv/bin/python" - <<'PY'
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmg_portal.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
email = (os.getenv("DEFAULT_ADMIN_EMAIL") or "admin@example.com").strip()
username = email[:150]
password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")

if not User.objects.filter(is_superuser=True).exists():
    u = User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser: {email}")
else:
    print("Superuser already exists, skipping.")
PY
}

# Function to update production
update_production() {
    echo ""
    echo -e "${GREEN}=== Updating Production Environment ===${NC}"
    
    cd "$PROD_DIR"
    
    # Backup .env
    sudo cp "$PROD_DIR/.env" "$PROD_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)" || true
    
    echo "Pulling latest code from main branch..."
    sudo git fetch origin
    sudo git checkout main
    sudo git pull origin main
    
    echo "Running update script..."
    sudo bash "$PROD_DIR/scripts/update.sh"
    
    echo -e "${GREEN}Production update complete!${NC}"
}

# Function to update development
update_development() {
    echo ""
    echo -e "${GREEN}=== Updating Development Environment ===${NC}"
    
    cd "$DEV_DIR"
    
    # Backup .env
    sudo cp "$DEV_DIR/.env" "$DEV_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)" || true
    
    echo "Pulling latest code from dev branch..."
    sudo git fetch origin
    sudo git checkout dev
    sudo git pull origin dev
    
    echo "Running update script..."
    sudo bash "$DEV_DIR/scripts/update.sh"
    
    echo -e "${GREEN}Development update complete!${NC}"
}

# Function to merge dev to production (final release)
merge_dev_to_production() {
    echo ""
    echo -e "${YELLOW}=== Merging Development to Production (Final Release) ===${NC}"
    echo ""
    echo -e "${RED}WARNING: This will merge development features into production.${NC}"
    echo "This operation will:"
    echo "  1. Backup production database"
    echo "  2. Pull latest main branch"
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
    
    if [ "$PROD_EXISTS" != "true" ]; then
        echo -e "${RED}Production installation not found!${NC}"
        exit 1
    fi
    
    if [ "$DEV_EXISTS" != "true" ]; then
        echo -e "${RED}Development installation not found!${NC}"
        exit 1
    fi
    
    # Backup production database
    echo "Backing up production database..."
    set -a
    source "$PROD_DIR/.env"
    set +a
    
    BACKUP_FILE="/tmp/pmg_portal_backup_$(date +%Y%m%d_%H%M%S).sql"
    if [ "$POSTGRES_HOST" = "127.0.0.1" ] || [ "$POSTGRES_HOST" = "localhost" ]; then
        sudo -u postgres pg_dump "$POSTGRES_DB" > "$BACKUP_FILE"
        echo "Database backup saved to: $BACKUP_FILE"
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
    sudo sed -i 's/^ENABLE_DEV_FEATURES=false/ENABLE_DEV_FEATURES=true/' "$PROD_DIR/.env" || true
    
    # Run migrations (will add dev features)
    echo "Running migrations..."
    cd "$PROD_DIR/src"
    set -a
    source "$PROD_DIR/.env"
    set +a
    
    sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py migrate --noinput
    sudo -E "$PROD_DIR/src/.venv/bin/python" manage.py collectstatic --noinput
    
    # Restart service
    sudo systemctl restart pmg-portal.service
    
    echo ""
    echo -e "${GREEN}Merge complete!${NC}"
    echo "Production now has all development features."
    echo "Database backup: $BACKUP_FILE"
    echo ""
    echo "You can continue developing new features in development environment."
}

# Function to uninstall production
uninstall_production() {
    echo ""
    echo -e "${RED}=== Uninstalling Production Environment ===${NC}"
    echo ""
    echo -e "${RED}WARNING: This will remove the production installation.${NC}"
    
    if [ -t 0 ] && [ -t 1 ]; then
        read -rp "Remove production database? (y/N): " remove_db
        if [[ "$remove_db" =~ ^[Yy]$ ]]; then
            set -a
            source "$PROD_DIR/.env"
            set +a
            
            if [ "${POSTGRES_HOST:-127.0.0.1}" = "127.0.0.1" ] || [ "${POSTGRES_HOST:-127.0.0.1}" = "localhost" ]; then
                echo "Removing production database..."
                sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"${POSTGRES_DB}\";" 2>/dev/null || true
                sudo -u postgres psql -c "DROP USER IF EXISTS \"${POSTGRES_USER}\";" 2>/dev/null || true
            fi
        fi
    fi
    
    echo "Stopping service..."
    sudo systemctl stop pmg-portal.service 2>/dev/null || true
    sudo systemctl disable pmg-portal.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/pmg-portal.service
    sudo systemctl daemon-reload
    
    echo "Removing application files..."
    sudo rm -rf "$PROD_DIR"
    
    echo -e "${GREEN}Production uninstall complete.${NC}"
}

# Function to uninstall development
uninstall_development() {
    echo ""
    echo -e "${RED}=== Uninstalling Development Environment ===${NC}"
    echo ""
    echo -e "${RED}WARNING: This will remove the development installation.${NC}"
    
    if [ -t 0 ] && [ -t 1 ]; then
        read -rp "Remove development database? (y/N): " remove_db
        if [[ "$remove_db" =~ ^[Yy]$ ]]; then
            set -a
            source "$DEV_DIR/.env"
            set +a
            
            if [ "${POSTGRES_HOST:-127.0.0.1}" = "127.0.0.1" ] || [ "${POSTGRES_HOST:-127.0.0.1}" = "localhost" ]; then
                echo "Removing development database..."
                sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"${POSTGRES_DB}\";" 2>/dev/null || true
                sudo -u postgres psql -c "DROP USER IF EXISTS \"${POSTGRES_USER}\";" 2>/dev/null || true
            fi
        fi
    fi
    
    echo "Stopping service..."
    sudo systemctl stop pmg-portal-dev.service 2>/dev/null || true
    sudo systemctl disable pmg-portal-dev.service 2>/dev/null || true
    sudo rm -f /etc/systemd/system/pmg-portal-dev.service
    sudo systemctl daemon-reload
    
    echo "Removing application files..."
    sudo rm -rf "$DEV_DIR"
    
    echo -e "${GREEN}Development uninstall complete.${NC}"
}

# Execute based on mode
case "$MODE" in
    install_prod)
        install_production
        ;;
    install_dev)
        install_development
        ;;
    install_both)
        install_production
        install_development
        ;;
    update_prod)
        update_production
        ;;
    update_dev)
        update_development
        ;;
    uninstall_prod)
        uninstall_production
        ;;
    uninstall_dev)
        uninstall_development
        ;;
    *)
        echo -e "${RED}Unknown mode: $MODE${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}=== Installation Wizard Complete ===${NC}"
echo ""
if [ "$PROD_EXISTS" = "true" ] || [ "$MODE" = "install_prod" ] || [ "$MODE" = "install_both" ]; then
    echo "Production:"
    echo "  Path: $PROD_DIR"
    echo "  Service: pmg-portal.service"
    echo "  Logs: sudo journalctl -u pmg-portal.service -f --no-pager"
fi
if [ "$DEV_EXISTS" = "true" ] || [ "$MODE" = "install_dev" ] || [ "$MODE" = "install_both" ]; then
    echo "Development:"
    echo "  Path: $DEV_DIR"
    echo "  Service: pmg-portal-dev.service"
    echo "  Logs: sudo journalctl -u pmg-portal-dev.service -f --no-pager"
fi
echo ""
