# BUILDLOG

- 2026-02-05 (Europe/Oslo)
  - Branch: dev (suggested)
  - Version: 0.1.0-alpha.4
  - Summary:
    - Changed default APP_BIND to 0.0.0.0:8097 for reverse proxy compatibility

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
