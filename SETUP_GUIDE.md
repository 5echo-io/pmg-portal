<!--
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Setup and data model guide
Path: SETUP_GUIDE.md
Created: 2026-02-05
Last Modified: 2026-02-06
-->

# PMG Portal Setup Guide

## Data Model Overview

### 1. **Customers** = Client Companies/Organizations
   - Examples: "Park Media Group AS", "Company ABC", "Client XYZ"
   - Each customer represents a company/organization that uses the portal
   - **Where to create**: Admin → Customers → Add Customer

### 2. **CustomerMembership** = User-to-Customer Assignment
   - Links users to customers (which users belong to which companies)
   - **Role options**:
     - `member`: Regular access to the customer portal
     - `admin`: Customer admin privileges (can manage customer-specific settings)
   - **Where to create**: Admin → Customer Memberships → Add Customer Membership
   - **Important**: A user must have a CustomerMembership to access the portal

### 3. **Portal Links** = Links Shown on Portal Page
   - Links that appear in the "Quick links" section on the customer's portal page
   - **NOT** shown in the top navigation bar
   - Each link belongs to a specific customer
   - **Where to create**: Admin → Portal Links → Add Portal Link

### 4. **Groups** (Django built-in) = Permission Groups
   - Not currently used in this setup
   - Can be used for Django-level permissions if needed

## Setup Flow

### Step 1: Create a Customer
1. Go to Admin → Customers
2. Click "Add Customer"
3. Enter:
   - **Name**: "Park Media Group AS" (or your company name)
   - **Slug**: Auto-generated from name (e.g., "park-media-group-as")
4. Save

### Step 2: Assign Users to Customer
1. Go to Admin → Customer Memberships
2. Click "Add Customer Membership"
3. Select:
   - **User**: Choose a user (e.g., your admin user)
   - **Customer**: Select the customer you created
   - **Role**: Choose "member" or "admin"
4. Save

### Step 3: Add Portal Links (Optional)
1. Go to Admin → Portal Links
2. Click "Add Portal Link"
3. Enter:
   - **Customer**: Select the customer
   - **Title**: "Company Website" (or any title)
   - **URL**: https://example.com
   - **Description**: Optional description
   - **Sort order**: 100 (lower numbers appear first)
4. Save

## How It Works

- **Login**: Users log in with their username/password
- **Portal Access**: After login, users are redirected to `/portal/`
- **Customer Portal**: Shows the customer they're assigned to (via CustomerMembership)
- **Portal Links**: Appear in the "Quick links" section on the portal page
- **Multiple Customers**: If a user has multiple CustomerMemberships, they see the first one (customer switcher coming later)

## Troubleshooting

**Error: "column X does not exist" (e.g. `portal_facility.status_label_year does not exist`)?**  
- The database schema is behind the application code. Run migrations after every code deploy:  
  `sudo bash /opt/pmg-portal/scripts/update.sh`  
  Or only: `sudo bash /opt/pmg-portal/scripts/run_manage.sh migrate --noinput` then restart the service.

**Error: "relation \"portal_userprofile\" does not exist" (but 0021 is marked applied)?**  
- Migration state is out of sync (e.g. 0021 was faked or DB restored without the table). Re-run the affected migrations by clearing their state, then migrate:

```bash
# Use your actual DB name from .env (POSTGRES_DB). Example: pmg_portal
sudo -u postgres psql -d pmg_portal -c "DELETE FROM django_migrations WHERE app = 'portal' AND name IN ('0021_userprofile_and_tenant_roles', '0022_migrate_member_admin_to_user_administrator', '0023_sync_is_staff_from_roles');"
sudo bash /opt/pmg-portal/scripts/run_manage.sh migrate --noinput
sudo systemctl restart pmg-portal.service
```

Replace `pmg_portal` with the value of `POSTGRES_DB` from `/opt/pmg-portal/.env` if different.

**"No customer access" message after login?**
- Create a CustomerMembership linking your user to a Customer

**Portal links not showing?**
- Make sure you created Portal Links for the correct Customer
- Check that the user has a CustomerMembership for that Customer

**Can't see Customers/Memberships/Links in admin?**
- Make sure you're logged in as a superuser (admin account)

## Updating the app

**Important:** After every code update (e.g. `git pull` or new deploy), you must run the update script so **database migrations** are applied. Otherwise you may see errors like `column X does not exist`.

From the server (e.g. `/opt/pmg-portal`):

```bash
cd /opt/pmg-portal && sudo git pull origin dev && sudo bash scripts/update.sh
```

This pulls the latest code, then runs: stop service → reinstall Python deps → **migrate** (required for schema) → collectstatic → compilemessages → start service.

If you already pulled code but did not run `update.sh`, run migrations now:

```bash
sudo bash /opt/pmg-portal/scripts/update.sh
```

Or only migrations (if deps/static are already up to date):

```bash
sudo bash /opt/pmg-portal/scripts/run_manage.sh migrate --noinput
sudo bash /opt/pmg-portal/scripts/run_manage.sh set_stored_version
sudo systemctl restart pmg-portal.service
```

For **manual Django commands** (e.g. `showmigrations`, `migrate --fake`), use the wrapper so `.env` is loaded and `POSTGRES_DB` etc. are set:  
`sudo bash /opt/pmg-portal/scripts/run_manage.sh showmigrations portal`  
`sudo bash /opt/pmg-portal/scripts/run_manage.sh migrate --fake portal 0014`

## Internationalization (Languages)

The portal supports **Norwegian (Bokmål)** and **English**. Users can switch language from the avatar menu (when logged in) or from the login page footer. For adding or editing translated strings, see **[docs/I18N.md](docs/I18N.md)**.
