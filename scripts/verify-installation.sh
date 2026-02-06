#!/usr/bin/env bash
# Copyright (c) 2026 5echo.io
# Project: PMG Portal
# Purpose: Verify installation setup
# Path: scripts/verify-installation.sh
# Usage: sudo bash scripts/verify-installation.sh
set -euo pipefail

PROD_DIR="/opt/pmg-portal"
DEV_DIR="/opt/pmg-portal-dev"

echo "=== PMG Portal Installation Verification ==="
echo ""

# Check production
if [ -d "$PROD_DIR" ] && [ -f "$PROD_DIR/.env" ]; then
    echo "✓ Production installation found"
    echo "  Path: $PROD_DIR"
    
    # Check .env
    if [ -f "$PROD_DIR/.env" ]; then
        echo "  ✓ .env file exists"
        source "$PROD_DIR/.env"
        echo "  Database: $POSTGRES_DB"
        echo "  Port: $APP_BIND"
        echo "  ALLOWED_HOSTS: $DJANGO_ALLOWED_HOSTS"
        
        # Check for dev subdomain in production (should not be there)
        if [[ "$DJANGO_ALLOWED_HOSTS" == *"dev.portal.parkmediagroup.no"* ]]; then
            echo -e "  ${RED}✗ WARNING: dev subdomain found in production ALLOWED_HOSTS!${NC}"
        else
            echo "  ✓ No dev subdomain in production (correct)"
        fi
    fi
    
    # Check service
    if systemctl is-active --quiet pmg-portal.service; then
        echo "  ✓ Service is running"
    else
        echo -e "  ${RED}✗ Service is not running${NC}"
    fi
    
    # Check database
    if [ "${POSTGRES_HOST:-127.0.0.1}" = "127.0.0.1" ] || [ "${POSTGRES_HOST:-127.0.0.1}" = "localhost" ]; then
        DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" 2>/dev/null || echo "0")
        if [ "$DB_EXISTS" = "1" ]; then
            echo "  ✓ Database exists"
        else
            echo -e "  ${RED}✗ Database does not exist${NC}"
        fi
    fi
    
    echo ""
else
    echo "✗ Production installation not found"
    echo ""
fi

# Check development
if [ -d "$DEV_DIR" ] && [ -f "$DEV_DIR/.env" ]; then
    echo "✓ Development installation found"
    echo "  Path: $DEV_DIR"
    
    # Check .env
    if [ -f "$DEV_DIR/.env" ]; then
        echo "  ✓ .env file exists"
        set -a
        source "$DEV_DIR/.env"
        set +a
        echo "  Database: $POSTGRES_DB"
        echo "  Port: $APP_BIND"
        echo "  ALLOWED_HOSTS: $DJANGO_ALLOWED_HOSTS"
        echo "  ENABLE_DEV_FEATURES: $ENABLE_DEV_FEATURES"
        
        # Check for dev subdomain in development (should be there)
        if [[ "$DJANGO_ALLOWED_HOSTS" == *"dev.portal.parkmediagroup.no"* ]]; then
            echo "  ✓ Dev subdomain found in development ALLOWED_HOSTS (correct)"
        else
            echo -e "  ${YELLOW}⚠ Dev subdomain not found in development ALLOWED_HOSTS${NC}"
        fi
    fi
    
    # Check service
    if systemctl is-active --quiet pmg-portal-dev.service; then
        echo "  ✓ Service is running"
    else
        echo -e "  ${RED}✗ Service is not running${NC}"
    fi
    
    # Check database
    if [ "${POSTGRES_HOST:-127.0.0.1}" = "127.0.0.1" ] || [ "${POSTGRES_HOST:-127.0.0.1}" = "localhost" ]; then
        DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'" 2>/dev/null || echo "0")
        if [ "$DB_EXISTS" = "1" ]; then
            echo "  ✓ Database exists"
        else
            echo -e "  ${RED}✗ Database does not exist${NC}"
        fi
    fi
    
    echo ""
else
    echo "✗ Development installation not found"
    echo ""
fi

# Check ports
echo "Port status:"
sudo ss -lntp | grep -E '(:8097|:8098)' || echo "  No services listening on ports 8097 or 8098"

echo ""
echo "=== Verification Complete ==="
