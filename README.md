# PMG Portal (Foundation)

A Django + Postgres portal foundation:
- Login-first site (landing redirects to login)
- User registration (optional)
- Admin-only interface (Django Admin)
- Customers (organizations) as groups of users
- Users can belong to multiple customers
- Simple customer portal pages (same template/layout for all customers)

## Quick start (Ubuntu)
1) Install Postgres and create database/user (see .env.example)
2) Copy .env.example to .env and edit values
3) Run:
   sudo bash scripts/install.sh

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
