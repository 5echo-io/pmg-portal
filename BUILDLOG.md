# BUILDLOG

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.7
  - Summary:
    - Improved UI/UX: better topbar button styling, admin visibility controls
    - Added bulk add CustomerMemberships feature
    - Simplified footer design
    - Made 5echo.io clickable link

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.6
  - Summary:
    - Created initial migrations for portal models (fixes missing database tables)
    - Fixed admin 500 errors with improved error handling
    - Improved changelog modal to show version-specific sections
    - Removed changelog preview text from footer, only button remains
    - Added dark mode scrollbar styling
    - Added logging configuration for better debugging
    - Improved topbar design with better button styling
    - Admin button only visible to superusers
    - Removed Admin link from login page
    - Added bulk add CustomerMemberships feature
    - Made 5echo.io clickable in footer
    - Simplified footer (removed Quick Links)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.5
  - Summary:
    - Fixed installer interactive mode detection (auto-defaults to update when piped)
    - Improved non-interactive installation experience
    - Added footer with copyright, version, and changelog preview
    - Added changelog modal dialog for viewing full changelog
    - Fixed 500 error when saving Customer in admin (context processor now skips admin pages)
    - Improved admin queryset handling to avoid errors during save operations
    - Fixed context processor file reading errors causing admin save failures
    - Improved portal_home view error handling and query optimization
    - Comprehensive fix for admin 500 errors: improved get_queryset URL detection, added try/except blocks
    - Added logging configuration for better debugging

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.4
  - Summary:
    - Added standalone installer (install.sh) for curl-based installation
    - Installer detects existing installation and offers update/uninstall
    - Update mode preserves database and .env configuration
    - Fixed interactive prompts in non-interactive mode (defaults to update)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.4
  - Summary:
    - Changed default APP_BIND to 0.0.0.0:8097 for reverse proxy compatibility
    - Fixed static files not loading: added WhiteNoise middleware for production
    - Updated templates to use Django static tag
    - Fixed 500 errors after login and "View site" button
    - Whitelabeled admin site (PMG Portal branding)
    - Improved admin interface with descriptions and counts
    - Added setup guide documentation
    - Fixed 500 error when adding Customer (member_count/link_count methods)

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.3
  - Summary:
    - Set default bind port to 8097
    - Fixed local Postgres bootstrap in install wizard

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.2
  - Summary:
    - Added interactive install wizard with .env prompts
    - Bootstrapped local Postgres during install when applicable
    - Updated default admin credentials to admin/admin and superuser check

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.1
  - Summary:
    - Created initial Django + Postgres portal foundation
    - Added install/update/reinstall/uninstall scripts
    - Added systemd + optional nginx config
