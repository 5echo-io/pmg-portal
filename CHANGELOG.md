# Changelog

All notable changes to this project will be documented in this file.
This project follows Semantic Versioning (SemVer).

## [Unreleased]
Added:
- Interactive install wizard to collect .env values and bootstrap local Postgres

Changed:
- Default admin password to "admin" and skip creation if any superuser exists
- Default app bind port to 8097
- Default APP_BIND to 0.0.0.0:8097 (was 127.0.0.1:8097) for reverse proxy compatibility
- Improved install wizard DJANGO_ALLOWED_HOSTS prompt with example

Fixed:
- Local Postgres bootstrap in installer (role/db creation)
- Static files not loading (added WhiteNoise middleware for production static file serving)
- 500 error after login redirect (improved error handling in portal_home view)
- "View site" button redirect error (fixed landing view to check authentication)
- Whitelabeled admin site (removed "Django administration" branding)

## [0.1.0-alpha.1] - Initial foundation
Added:
- Login-first site flow
- Registration page (optional)
- Customer model and membership
- Customer portal landing page
- Admin setup and default admin bootstrap
