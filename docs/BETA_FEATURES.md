# Development Features Management

This document explains how to set up and manage development features in PMG Portal.

## Overview

PMG Portal supports running separate production and development installations side-by-side. Development features (like Facility management) are controlled via feature flags and are restricted to superusers (admins) only.

## Architecture

### Separate Installations (Recommended)

**Production Installation:**
- Path: `/opt/pmg-portal`
- Port: `8097` (default)
- Database: `pmg_portal` (or custom)
- Branch: `main` (stable releases)

**Development Installation:**
- Path: `/opt/pmg-portal-beta` (or custom)
- Port: `8098` (or custom)
- Database: `pmg_portal_beta` (separate database recommended)
- Branch: `dev` (development/testing)

### Feature Flags

Beta features are controlled via environment variables in `.env`:

```bash
# Enable beta features (Facility management, etc.)
ENABLE_DEV_FEATURES=true

# Restrict dev access to specific superusers (comma-separated emails/usernames)
# Leave empty to allow all superusers
DEV_ACCESS_USERS=admin@example.com,developer@example.com
```

## Installation Guide

### 1. Production Installation (Main)

```bash
# Install from main branch
curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/main/install.sh | sudo bash

# Or manually:
cd /opt/pmg-portal
sudo git clone -b main https://github.com/5echo-io/pmg-portal.git .
sudo bash scripts/install.sh
```

**Production `.env` configuration:**
```bash
# Dev features disabled in production
ENABLE_DEV_FEATURES=false
DEV_ACCESS_USERS=

# Other settings...
APP_BIND=0.0.0.0:8097
POSTGRES_DB=pmg_portal
```

### 2. Beta/Alpha Installation (Dev)

```bash
# Create separate directory
sudo mkdir -p /opt/pmg-portal-beta
cd /opt/pmg-portal-beta

# Clone dev branch
sudo git clone -b dev https://github.com/5echo-10/pmg-portal.git .

# Run install wizard
sudo bash scripts/install.sh
```

**Development `.env` configuration:**
```bash
# Enable dev features
ENABLE_DEV_FEATURES=true

# Restrict access (optional - leave empty for all superusers)
DEV_ACCESS_USERS=admin@example.com,developer@example.com

# Use different port and database
APP_BIND=0.0.0.0:8098
POSTGRES_DB=pmg_portal_beta

# Other settings...
```

### 3. Separate Systemd Services

**Production service:** `/etc/systemd/system/pmg-portal.service`
```ini
[Unit]
Description=PMG Portal Production (Gunicorn)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/pmg-portal/src
EnvironmentFile=/opt/pmg-portal/.env
ExecStart=/opt/pmg-portal/src/.venv/bin/gunicorn pmg_portal.wsgi:application --bind ${APP_BIND} --workers 2
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
```

**Development service:** `/etc/systemd/system/pmg-portal-dev.service`
```ini
[Unit]
Description=PMG Portal Development (Gunicorn)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/pmg-portal-beta/src
EnvironmentFile=/opt/pmg-portal-beta/.env
ExecStart=/opt/pmg-portal-beta/src/.venv/bin/gunicorn pmg_portal.wsgi:application --bind ${APP_BIND} --workers 2
Restart=always
RestartSec=3
User=root

[Install]
WantedBy=multi-user.target
```

## Database Management

### Option 1: Separate Databases (Recommended)

**Pros:**
- Complete isolation between production and beta
- No risk of breaking production data
- Can test migrations safely

**Cons:**
- Need to sync data manually if needed
- More complex setup

**Setup:**
```bash
# Production database
POSTGRES_DB=pmg_portal

# Beta database
POSTGRES_DB=pmg_portal_beta
```

### Option 2: Shared Database (Advanced)

**Pros:**
- Same data in both environments
- Easier to test with real data

**Cons:**
- Risk of breaking production data
- Migrations must be compatible
- Not recommended for production use

**Warning:** Only use shared database if you understand the risks. Beta migrations should be forward-compatible with production code.

## Access Control

### Development Access Rules

1. **Dev features disabled** (`ENABLE_DEV_FEATURES=false`):
   - No dev features visible
   - All dev routes return 403/redirect

2. **Dev features enabled, no user restriction** (`DEV_ACCESS_USERS=` empty):
   - All superusers (admins) have access
   - Dev features visible in UI

3. **Dev features enabled, with user restriction** (`DEV_ACCESS_USERS=user1@example.com,user2@example.com`):
   - Only specified superusers have access
   - Others see dev features as disabled

**Important:** Dev features are **only accessible to superusers**, not regular staff users.

### Checking Beta Access

**In templates:**
```django
{% if dev_features_enabled and has_dev_access %}
  <!-- Dev feature UI -->
{% endif %}
```

**In views:**
```python
from portal.decorators import dev_required

@dev_required
def my_dev_view(request):
    # Only accessible to superusers with dev access
    pass
```

## Workflow

### Development Workflow

1. **Develop on dev branch:**
   ```bash
   cd /opt/pmg-portal-dev
   sudo git pull origin dev
   sudo bash scripts/update.sh
   ```

2. **Test in development installation:**
   - Access dev installation at `http://server:8098`
   - Test new features as superuser/admin
   - Verify migrations work

3. **When ready for production:**
   - Merge dev → main
   - Update production installation
   - Disable dev features in production

### Migration Workflow

**Important:** Migrations must be forward-compatible!

1. **Create migrations in dev:**
   ```bash
   cd /opt/pmg-portal-dev/src
   sudo -E .venv/bin/python manage.py makemigrations
   ```

2. **Test migrations in development:**
   ```bash
   sudo -E .venv/bin/python manage.py migrate
   ```

3. **Verify production code still works:**
   - Production code should handle missing tables gracefully
   - Or use feature flags to hide features until migrations are run

4. **Deploy to production:**
   ```bash
   cd /opt/pmg-portal
   sudo git pull origin main
   sudo bash scripts/update.sh  # Runs migrations automatically
   ```

## Removing Beta Installation

When development features are merged to production and released:

1. **Disable dev features in production:**
   ```bash
   # In production .env
   ENABLE_DEV_FEATURES=false
   ```

2. **Stop and remove dev service:**
   ```bash
   sudo systemctl stop pmg-portal-dev.service
   sudo systemctl disable pmg-portal-dev.service
   sudo rm /etc/systemd/system/pmg-portal-dev.service
   sudo systemctl daemon-reload
   ```

3. **Optional: Remove dev installation:**
   ```bash
   sudo rm -rf /opt/pmg-portal-dev
   ```

4. **Optional: Remove dev database:**
   ```bash
   sudo -u postgres psql -c "DROP DATABASE pmg_portal_dev;"
   ```

## Nginx Configuration (Optional)

If using reverse proxy, configure separate locations:

```nginx
# Production
location / {
    proxy_pass http://127.0.0.1:8097;
    # ... other settings
}

# Development (optional, restrict access)
location /dev/ {
    proxy_pass http://127.0.0.1:8098;
    # Restrict to specific IPs or use auth
    allow 10.0.0.0/8;
    deny all;
}
```

## Troubleshooting

### Dev features not showing

1. Check `ENABLE_DEV_FEATURES=true` in `.env`
2. Restart service: `sudo systemctl restart pmg-portal-dev.service`
3. Check user is superuser (admin) and optionally in `DEV_ACCESS_USERS`
4. Check logs: `sudo journalctl -u pmg-portal-dev.service -f`

### Migration conflicts

- Use separate databases for production and beta
- Test migrations in beta before deploying to production
- Ensure migrations are forward-compatible

### Port conflicts

- Use different ports for production (8097) and beta (8098)
- Update `APP_BIND` in respective `.env` files
- Update firewall rules if needed

## Best Practices

1. **Always use separate databases** for production and development
2. **Test migrations thoroughly** in development before production
3. **Dev features are admin-only** - only superusers can access
4. **Monitor dev installation** for errors and performance
5. **Keep dev in sync** with production data structure when possible
6. **Document dev features** and their status
7. **Remove dev installation** when features are merged to production
