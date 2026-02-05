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
```bash
sudo apt install curl -y && curl -fsSL https://raw.githubusercontent.com/5echo-io/pmg-portal/dev/install.sh | sudo bash
```

The installer will:
- Detect if PMG Portal is already installed
- If installed: prompt to **Update** (preserves database) or **Uninstall**
- If not installed: run fresh installation wizard

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
