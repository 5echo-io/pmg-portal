#!/usr/bin/env bash
# Purpose: Uninstall app services and files (keeps Postgres DB by default)
set -euo pipefail

APP_DIR="/opt/pmg-portal"

echo "=== Uninstalling pmg-portal ==="

sudo systemctl stop pmg-portal.service || true
sudo systemctl disable pmg-portal.service || true
sudo rm -f /etc/systemd/system/pmg-portal.service
sudo systemctl daemon-reload

sudo rm -rf "$APP_DIR"

echo "Removed app files and systemd service."
echo "NOTE: Postgres database was NOT removed."
