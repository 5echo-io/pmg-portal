#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/pmg-portal"
SERVICE="pmg-portal.service"

cmd="${1:-help}"

case "$cmd" in
  install)
    sudo bash "$APP_DIR/scripts/install.sh"
    ;;
  update)
    cd "$APP_DIR"
    sudo git pull origin dev
    sudo bash "$APP_DIR/scripts/update.sh"
    ;;
  reinstall)
    sudo bash "$APP_DIR/scripts/reinstall.sh"
    ;;
  uninstall)
    sudo bash "$APP_DIR/scripts/uninstall.sh"
    ;;
  restart)
    sudo systemctl restart "$SERVICE"
    sudo systemctl status "$SERVICE" --no-pager -l || true
    ;;
  status)
    sudo systemctl status "$SERVICE" --no-pager -l || true
    ;;
  logs)
    sudo journalctl -u "$SERVICE" -f --no-pager
    ;;
  self-test)
    sudo bash "$APP_DIR/scripts/self-test.sh"
    ;;
  ports)
    sudo ss -lntp | grep -E '(:8000|:8087|:8097)' || true
    ;;
  help|*)
    echo "Usage: sudo $APP_DIR/scripts/pmg-portal.sh {install|update|reinstall|uninstall|restart|status|logs|self-test|ports}"
    ;;
esac
