# Changelog

All notable changes to this project will be documented in this file.
This project follows Semantic Versioning (SemVer).

## [Unreleased]
Added:
- Interactive install wizard to collect .env values and bootstrap local Postgres
- Improved admin interface with helpful descriptions and member/link counts
- Setup guide documentation (SETUP_GUIDE.md)
- Standalone installer script (install.sh) that can be run via curl from GitHub
- Installer detects existing installation and offers update/uninstall options
- Footer with copyright, version, and changelog button
- Changelog modal dialog showing version-specific changes (unreleased or major release)
- Dark mode scrollbar styling
- Initial database migrations for portal models
- Bulk add CustomerMemberships feature integrated into regular add form (multi-select customers)
- Customer admins can now manage memberships for their own customer
- Improved README.md with detailed installation and update instructions
- Modernized Django admin interface with dark theme matching portal design

Changed:
- Default admin password to "admin" and skip creation if any superuser exists
- Default app bind port to 8097
- Default APP_BIND to 0.0.0.0:8097 (was 127.0.0.1:8097) for reverse proxy compatibility
- Improved install wizard DJANGO_ALLOWED_HOSTS prompt with example
- Enhanced admin interface for Customers, CustomerMemberships, and Portal Links
- Improved topbar design with better button styling and username separation
- Admin button only visible to superusers (removed from login page)
- Footer simplified (removed Quick Links section)
- Changelog button styled to match other footer links
- Made 5echo.io clickable link in footer
- Registration text updated to reflect PMG and Customer admin access assignment
- CustomerMembership admin: multi-select customers when adding, single select when editing

Fixed:
- Local Postgres bootstrap in installer (role/db creation)
- Static files not loading (added WhiteNoise middleware for production static file serving)
- 500 error after login redirect (improved error handling in portal_home view)
- "View site" button redirect error (fixed landing view to check authentication)
- Whitelabeled admin site (removed "Django administration" branding)
- 500 error when adding Customer (fixed member_count/link_count methods to handle new objects)
- Installer interactive prompts when piped from curl (defaults to update mode in non-interactive)
- 500 error when saving Customer in admin (optimized queryset and fixed admin_order_field)
- 500 error in admin save and portal links (fixed context processor file reading, improved error handling)
- 500 error when saving in admin (context processor now skips admin pages, improved admin queryset handling)
- 500 errors on admin changelist and save operations (improved get_queryset URL detection, added comprehensive error handling)
- Database tables missing error (created initial migrations for portal models)
- 500 error when adding CustomerMembership (fixed form fields configuration for add/edit modes)
- 500 error when accessing CustomerMembership changelist (removed bulk_add URL reference)
- Modernized Django admin interface with dark theme matching portal design

## [0.1.0-alpha.1] - Initial foundation
Added:
- Login-first site flow
- Registration page (optional)
- Customer model and membership
- Customer portal landing page
- Admin setup and default admin bootstrap
