#!/usr/bin/env bash
# Run Django manage.py with .env loaded (so POSTGRES_DB etc. are set).
# Use this for manual commands instead of calling manage.py directly.
# Usage: sudo bash /opt/pmg-portal/scripts/run_manage.sh <manage_command> [args...]
# Example: sudo bash /opt/pmg-portal/scripts/run_manage.sh showmigrations portal
# Example: sudo bash /opt/pmg-portal/scripts/run_manage.sh migrate --fake portal 0014
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="${APP_DIR:-$SCRIPT_DIR}"
SRC_DIR="$APP_DIR/src"

if [ ! -d "$APP_DIR" ]; then
  echo "ERROR: $APP_DIR not found." >&2
  exit 1
fi

if [ ! -f "$APP_DIR/.env" ]; then
  echo "ERROR: $APP_DIR/.env not found. Run install first." >&2
  exit 1
fi

cd "$SRC_DIR"
set -a
source "$APP_DIR/.env"
set +a

exec "$SRC_DIR/.venv/bin/python" manage.py "$@"
