#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Install on Ubuntu (wizard, deps, migrations, admin, systemd)
# Path: scripts/install.sh
set -euo pipefail

APP_NAME="pmg-portal"
APP_DIR="/opt/pmg-portal"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$APP_DIR/src"

echo "=== Installing $APP_NAME ==="

sudo mkdir -p "$APP_DIR"
sudo rsync -a --delete "$REPO_DIR/" "$APP_DIR/"

echo "Installing OS dependencies..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip postgresql postgresql-client rsync gettext libjpeg-dev libpng-dev zlib1g-dev

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

echo "=== Install wizard (.env) ==="
if [ -f "$APP_DIR/.env" ]; then
  echo "Existing .env found. Using it as defaults."
  set -a
  source "$APP_DIR/.env"
  set +a
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
ENABLE_DEV_FEATURES_DEFAULT="${ENABLE_DEV_FEATURES:-false}"
DEV_ACCESS_USERS_DEFAULT="${DEV_ACCESS_USERS:-}"

prompt_default DJANGO_SECRET_KEY "DJANGO_SECRET_KEY (leave blank to auto-generate)" "$DJANGO_SECRET_KEY_DEFAULT"
if [ -z "$DJANGO_SECRET_KEY" ]; then
  DJANGO_SECRET_KEY="$(python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
)"
fi
prompt_default DJANGO_DEBUG "DJANGO_DEBUG (true/false)" "$DJANGO_DEBUG_DEFAULT"
prompt_default DJANGO_ALLOWED_HOSTS "DJANGO_ALLOWED_HOSTS (comma-separated, e.g. pmg-portal.example.com,localhost,127.0.0.1)" "$DJANGO_ALLOWED_HOSTS_DEFAULT"
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

# Ask if user wants development environment
echo ""
echo "=== Development Environment Setup ==="
if [ -t 0 ] && [ -t 1 ]; then
    read -rp "Do you want to set up a development environment alongside production? (y/N): " setup_dev
else
    setup_dev="N"
fi

if [[ "$setup_dev" =~ ^[Yy]$ ]]; then
    SETUP_DEV_ENV="true"
    echo "Development environment will be set up automatically."
else
    SETUP_DEV_ENV="false"
    echo "Skipping development environment setup."
fi

prompt_default ENABLE_DEV_FEATURES "ENABLE_DEV_FEATURES (true/false - enable development features like Facility management, admin only)" "$ENABLE_DEV_FEATURES_DEFAULT"
prompt_default DEV_ACCESS_USERS "DEV_ACCESS_USERS (comma-separated emails/usernames, leave empty for all superusers)" "$DEV_ACCESS_USERS_DEFAULT"

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

# --- Development Features ---
# Enable development features (Facility management, etc.) - admin/superuser only
ENABLE_DEV_FEATURES=$ENABLE_DEV_FEATURES
# Restrict dev access to specific superusers (leave empty for all superusers)
DEV_ACCESS_USERS=$DEV_ACCESS_USERS
EOF

escape_psql_literal() {
  printf "%s" "$1" | sed "s/'/''/g"
}

escape_psql_identifier() {
  printf "%s" "$1" | sed 's/"/""/g'
}

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

echo "Creating venv..."
cd "$SRC_DIR"
sudo python3 -m venv "$SRC_DIR/.venv"
sudo "$SRC_DIR/.venv/bin/pip" install --upgrade pip
sudo "$SRC_DIR/.venv/bin/pip" install -r "$SRC_DIR/requirements.txt"

echo "Creating media directory..."
MEDIA_DIR="$APP_DIR/media"
sudo mkdir -p "$MEDIA_DIR"
# Set ownership: check systemd service file for User, fallback to root (default in pmg-portal.service)
# Media directory should be writable by the service user
SERVICE_USER="root"  # Default from pmg-portal.service
if [ -f "$APP_DIR/deploy/systemd/pmg-portal.service" ]; then
  # Try to extract User from service file if specified
  EXTRACTED_USER=$(grep -E "^User=" "$APP_DIR/deploy/systemd/pmg-portal.service" | cut -d'=' -f2 | tr -d ' ' || echo "")
  if [ -n "$EXTRACTED_USER" ]; then
    SERVICE_USER="$EXTRACTED_USER"
  fi
fi
sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$MEDIA_DIR"
sudo chmod -R 755 "$MEDIA_DIR"

echo "Running migrations + collectstatic + compilemessages..."
set -a
source "$APP_DIR/.env"
set +a

# Migrations include accounts: syncs User.username from User.email (email-as-primary)
sudo -E "$SRC_DIR/.venv/bin/python" manage.py migrate --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
sudo -E "$SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0

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

echo "Installing systemd service..."
sudo cp "$APP_DIR/deploy/systemd/pmg-portal.service" /etc/systemd/system/pmg-portal.service
sudo systemctl daemon-reload
sudo systemctl enable --now pmg-portal.service

# Set up development environment if requested
if [ "$SETUP_DEV_ENV" = "true" ]; then
    echo ""
    echo "=== Setting up Development Environment ==="
    
    DEV_DIR="/opt/pmg-portal-dev"
    DEV_SRC_DIR="$DEV_DIR/src"
    
    # Extract domain from ALLOWED_HOSTS for dev subdomain
    DEV_DOMAIN=""
    if [ -n "$DJANGO_ALLOWED_HOSTS" ]; then
        # Get first domain (not localhost/127.0.0.1)
        FIRST_DOMAIN=$(echo "$DJANGO_ALLOWED_HOSTS" | cut -d',' -f1 | tr -d ' ')
        if [ "$FIRST_DOMAIN" != "localhost" ] && [ "$FIRST_DOMAIN" != "127.0.0.1" ]; then
            DEV_DOMAIN="dev.$FIRST_DOMAIN"
        fi
    fi
    
    # Build dev ALLOWED_HOSTS
    DEV_ALLOWED_HOSTS="$DJANGO_ALLOWED_HOSTS"
    if [ -n "$DEV_DOMAIN" ]; then
        DEV_ALLOWED_HOSTS="$DEV_DOMAIN,$DEV_ALLOWED_HOSTS"
    fi
    
    # Create development directory
    echo "Creating development directory..."
    sudo mkdir -p "$DEV_DIR"
    sudo rsync -a --exclude='.env' --exclude='.venv' --exclude='staticfiles' --exclude='media' "$REPO_DIR/" "$DEV_DIR/"
    
    # Create development .env
    echo "Creating development .env file..."
    sudo tee "$DEV_DIR/.env" >/dev/null <<EOF
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
POSTGRES_DB=${POSTGRES_DB}_dev
POSTGRES_USER=${POSTGRES_USER}_dev
POSTGRES_PASSWORD=$POSTGRES_PASSWORD

# --- Runtime ---
APP_BIND=0.0.0.0:8098

# --- Development Features ---
# Enable development features (Facility management, etc.) - admin/superuser only
ENABLE_DEV_FEATURES=true
# Restrict dev access to specific superusers (leave empty for all superusers)
DEV_ACCESS_USERS=
EOF
    
    # Set up development database
    if [ "$POSTGRES_HOST" = "127.0.0.1" ] || [ "$POSTGRES_HOST" = "localhost" ]; then
        echo "Configuring development Postgres database..."
        db_user_ident="$(echo "${POSTGRES_USER}_dev" | sed 's/"/""/g')"
        db_name_ident="$(echo "${POSTGRES_DB}_dev" | sed 's/"/""/g')"
        db_user_lit="$(echo "${POSTGRES_USER}_dev" | sed "s/'/''/g")"
        db_pass_lit="$(echo "$POSTGRES_PASSWORD" | sed "s/'/''/g")"
        db_name_lit="$(echo "${POSTGRES_DB}_dev" | sed "s/'/''/g")"
        
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
    fi
    
    # Create development venv
    echo "Creating development virtual environment..."
    cd "$DEV_SRC_DIR"
    sudo python3 -m venv "$DEV_SRC_DIR/.venv"
    sudo "$DEV_SRC_DIR/.venv/bin/pip" install --upgrade pip
    sudo "$DEV_SRC_DIR/.venv/bin/pip" install -r "$DEV_SRC_DIR/requirements.txt"
    
    # Create development media directory
    echo "Creating development media directory..."
    DEV_MEDIA_DIR="$DEV_DIR/media"
    sudo mkdir -p "$DEV_MEDIA_DIR"
    sudo chown -R root:root "$DEV_MEDIA_DIR"
    sudo chmod -R 755 "$DEV_MEDIA_DIR"
    
    # Run development migrations
    echo "Running development migrations + collectstatic + compilemessages..."
    set -a
    source "$DEV_DIR/.env"
    set +a
    
    sudo -E "$DEV_SRC_DIR/.venv/bin/python" manage.py migrate --noinput
    sudo -E "$DEV_SRC_DIR/.venv/bin/python" manage.py collectstatic --noinput
    sudo -E "$DEV_SRC_DIR/.venv/bin/python" manage.py compilemessages --verbosity 0
    
    # Create development admin if missing
    echo "Creating development admin (if missing)..."
    sudo -E "$DEV_SRC_DIR/.venv/bin/python" - <<'PY'
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
    
    # Create development systemd service
    echo "Installing development systemd service..."
    sudo tee /etc/systemd/system/pmg-portal-dev.service > /dev/null <<EOF
[Unit]
Description=PMG Portal Development (Gunicorn)
After=network.target

[Service]
Type=simple
WorkingDirectory=$DEV_SRC_DIR
EnvironmentFile=$DEV_DIR/.env
ExecStart=$DEV_SRC_DIR/.venv/bin/gunicorn pmg_portal.wsgi:application --bind \${APP_BIND} --workers 2 --access-logfile -
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable --now pmg-portal-dev.service
    
    echo ""
    echo -e "${GREEN}Development environment set up successfully!${NC}"
    echo "  Path: $DEV_DIR"
    echo "  Port: 8098"
    if [ -n "$DEV_DOMAIN" ]; then
        echo "  Domain: $DEV_DOMAIN"
    fi
    echo "  Database: ${POSTGRES_DB}_dev"
    echo "  Service: pmg-portal-dev.service"
fi

echo ""
echo "Done."
echo "Open: http://$APP_BIND (or via your reverse proxy)"
if [ "$SETUP_DEV_ENV" = "true" ]; then
    echo "Development: http://0.0.0.0:8098"
    if [ -n "$DEV_DOMAIN" ]; then
        echo "Development Domain: http://$DEV_DOMAIN"
    fi
fi
echo "Logs: sudo journalctl -u pmg-portal.service -f --no-pager"
if [ "$SETUP_DEV_ENV" = "true" ]; then
    echo "Dev Logs: sudo journalctl -u pmg-portal-dev.service -f --no-pager"
fi
