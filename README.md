# PMG Portal (Foundation)

A Django + Postgres portal foundation:
- Login-first site (landing redirects to login)
- User registration (optional)
- Admin-only interface (Django Admin)
- Customers (organizations) as groups of users
- Users can belong to multiple customers
- Simple customer portal pages (same template/layout for all customers)

## Quick start (Ubuntu)

### Option 1: One-line install from GitHub (Recommended)

**Fresh Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/dev/install.sh | sudo bash
```

**Update Existing Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/dev/install.sh | sudo bash
```
The installer will automatically detect if PMG Portal is already installed and prompt you to choose:
- **1) Update** - Preserves database and `.env` file, updates code and dependencies
- **2) Uninstall** - Removes everything including database (with confirmation prompt)
- **3) Cancel** - Exit without changes

**Interactive Mode:**
When run in an interactive terminal, you'll be prompted to choose between Update/Uninstall/Cancel.
When run non-interactively (piped from curl), it defaults to Update mode.

**What the installer does:**
- Installs OS dependencies (Python, Postgres, etc.)
- Interactive wizard to configure `.env` file
- Sets up local Postgres database and user
- Creates Python virtual environment
- Installs Python dependencies
- Runs Django migrations
- Collects static files
- Creates default admin user (if none exists)
- Sets up systemd service

### Option 2: Manual installation
1) Install Postgres and create database/user (see .env.example)
2) Copy .env.example to .env and edit values
3) Run:
   ```bash
   sudo bash scripts/install.sh
   ```

## Default admin
Created automatically from env:
- DEFAULT_ADMIN_USERNAME
- DEFAULT_ADMIN_EMAIL
- DEFAULT_ADMIN_PASSWORD

## Services
- systemd unit: deploy/systemd/pmg-portal.service
- optional nginx: deploy/nginx/pmg-portal.conf

## Debug
- Runtime logs:
  sudo journalctl -u pmg-portal.service -f --no-pager

- App self-test:
  sudo bash scripts/self-test.sh
