#!/usr/bin/env bash
# Purpose: Reinstall code to /opt without touching database
set -euo pipefail

APP_DIR="/opt/pmg-portal"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Reinstalling pmg-portal (keeping DB) ==="

sudo systemctl stop pmg-portal.service || true

sudo mkdir -p "$APP_DIR"
sudo rsync -a --delete "$REPO_DIR/" "$APP_DIR/"

bash "$REPO_DIR/scripts/update.sh"
echo "Done."
