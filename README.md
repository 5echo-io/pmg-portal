# PMG Portal (Foundation)

A Django + Postgres portal foundation:
- Login-first site (landing redirects to login)
- User registration (optional)
- Admin-only interface (Django Admin)
- Customers (organizations) as groups of users
- Users can belong to multiple customers
- Simple customer portal pages (same template/layout for all customers)

## Quick start (Ubuntu)

### One-line installation

**Install or Update PMG Portal:**
```bash
sudo apt install curl -y && curl -fsSL https://raw.githubusercontent.com/5echo-11/pmg-portal/main/scripts/install.sh | sudo bash
```

The installer automatically detects if PMG Portal is already installed and presents options:

**If already installed:**
- **1) Update Production** - Preserves database and configuration, updates code and dependencies only
- **2) Reinstall Production** - Reinstalls application, choose to keep or delete database
- **3) Uninstall Production** - Removes application, choose to keep or delete database
- **0) Cancel** - Exit without changes

**If not installed:**
- Starts fresh installation with configuration wizard

**What the installer does:**

**Fresh Installation:**
- Installs OS dependencies (Python, Postgres, Git, etc.)
- Interactive wizard to configure `.env` file
- Sets up local Postgres database and user (if using localhost)
- Creates Python virtual environment
- Installs Python dependencies
- Runs Django migrations
- Collects static files
- Creates default admin user (if none exists)
- Sets up systemd service

**Update:**
- Downloads latest code from GitHub main branch
- Preserves `.env` configuration
- Preserves database (no data loss)
- Preserves virtual environment
- Updates Python dependencies
- Runs migrations
- Collects static files
- Restarts service

**Reinstall:**
- Removes application files
- Option to keep or delete database
- Runs full installation wizard again
- Creates new database if deleted

**Uninstall:**
- Option to keep or delete database
- Removes application files
- Removes systemd service

### Manual installation

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
