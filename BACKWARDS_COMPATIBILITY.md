<!--
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Upgrade/downgrade and backup compatibility guidelines
Path: BACKWARDS_COMPATIBILITY.md
Created: 2026-02-05
Last Modified: 2026-02-06
-->

# Backwards compatibility – PMG Portal

This document describes how we ensure the app can **upgrade and downgrade** between versions without servers ending up in an inconsistent state, and that **backup/restore** and the **install wizard** work across versions.

## Overview

- **Version is stored in the database** after each successful migration. On startup the app checks whether the code version is **newer** or **same** as the DB version. If the DB is newer (you have downgraded code), **requests are blocked** with 503 and a clear message until you have run migrations backward.
- **Backup format** is versioned. All format versions we support (e.g. `"1"`) can be restored by current and future app versions. Backup files also contain `app_version` (which version created the backup).
- **Install/update scripts** always run `set_stored_version` after `migrate`, so the stored version always matches the last run.

## Components

### 1. Stored app version (database)

- **Model:** `portal.SystemInfo` (key `app_version`, value = string from `VERSION` file).
- **Set by:** `manage.py set_stored_version` (run automatically after `migrate` in `scripts/update.sh` and `scripts/install.sh`).
- **Used by:** `VersionCompatibilityMiddleware` and `pmg_portal.versioning.check_version_compatibility()`.

### 2. Version check on startup

- **Middleware:** `pmg_portal.version_middleware.VersionCompatibilityMiddleware`.
- **Logic:** If **stored version > current code version** (downgrade without matching migration state), **503** is returned with explanatory HTML.
- **User solution:** Run migrations backward to the target version (see below), then restart the app.

### 3. Backup / Restore

- **Manifest:** `manifest.json` in each backup contains:
  - `version` – backup **format** version (e.g. `"1"`). Only changed when the backup format changes (new structure, not just app version). Validation accepts both string and integer (e.g. `1` or `"1"`) for compatibility.
  - `app_version` – app version that **created** the backup (from `VERSION`); optional in older backups.
- **Supported format versions:** `admin_app.backup_restore.SUPPORTED_BACKUP_FORMAT_VERSIONS` (currently format `"1"`). All listed formats can be restored by the current app, including backups from older app versions.
- **Upgrade:** A backup from v2.0.0 can be restored on v5.0.0. After restore the DB has the schema and data from the backup; stored `app_version` in DB will be that of the backup. That is OK – the app treats it as an “upgrade” (code newer than or equal to DB) and does not block.
- **Downgrade:** To go back to e.g. v2.0.0: install v2.0.0, restore a backup taken on v2 (or run migrations backward to v2’s migration point), start the app. Do not restore a backup from v5 on a v2 installation unless you know the format and schema are compatible.

### 4. Install wizard and .env

- New .env keys should have **default values** in `settings.py` (e.g. `env("NEW_KEY", "default")`), so older installations do not have to update .env to start.
- Install/update scripts do not change .env on update; they keep the existing .env. Exception: manual change or documented configuration migration.

## Upgrade (e.g. v2.0.0 → v5.0.0)

1. Deploy new code (v5.0.0).
2. Run as usual:  
   `sudo bash scripts/update.sh`  
   or  
   `sudo bash scripts/install.sh`  
   (choose Update).
3. Script runs `migrate`, then `set_stored_version`. DB now stores v5.0.0.
4. App starts; middleware sees code version >= stored version → no block.

## Downgrade (e.g. v5.0.0 → v2.0.0)

1. **Stop the service.**
2. **Deploy old code** (v2.0.0).
3. Run migrations **backward** to the migration point v2.0.0 expects, e.g.:
   ```bash
   cd /opt/pmg-portal/src
   sudo -E .venv/bin/python manage.py migrate portal 0006_device_type_and_product_fk   # example – check v2’s last migration
   sudo -E .venv/bin/python manage.py migrate admin_app 0001_add_admin_notifications   # if needed
   ```
4. Set stored version to current (v2), so middleware does not block:
   ```bash
   sudo -E .venv/bin/python manage.py set_stored_version
   ```
5. Start the service.

If you **do not** run migrations backward and start v2 code against a DB that has v5 migrations, the app will either fail (missing tables/columns) or middleware will return 503 because stored version (v5) is newer than code (v2). You must then either run migrations backward as above, or restore a backup taken before the upgrade.

## Features and files (moved / removed / added)

So that the app **remains functional regardless of version** when files are moved, removed or added:

- **One code version per deploy:** On upgrade you deploy new code (with new files/URLs/views); on downgrade you deploy old code (with old file structure). The running app always has the file structure that belongs to that version – as long as migrations and stored version are aligned (see above).
- **New files/views/URLs:** When you add a new feature (new template, new view, new URL), it does not affect older versions – they do not have that code. After downgrade you use old code that does not reference the new files.
- **Moving/removing files:** Do it in **new** commits/versions. Older versions still have the old paths. Avoid the **same** code version referring to a file that has been removed or moved in the same release (i.e. refactor move/remove in one consistent change).
- **Templates that may be missing:** If a view is used across versions but the template can vary, consider `get_template()` with fallback or try/except around `render` and return a simple message (e.g. 404 or “Not available in this version”) instead of letting TemplateDoesNotExist crash the request.
- **URLs:** Avoid a URL in an older version pointing to a view that no longer exists in that version (typically avoided by the whole urlconf being part of the same code version).

In short: **The app remains functional per version because each deploy is one code version with its files; migrations + set_stored_version ensure DB and code are in sync on upgrade and downgrade.**

## Rules for developers

1. **Migrations:** Write **reversible** migrations where possible (`RunPython` with `reverse_code`, `AlterField` that can be rolled back). This makes downgrade safer.
2. **Backup format:** When you change the **structure** of backup (new files in archive, different manifest structure), increment `BACKUP_FORMAT_VERSION` and add the **old** version to `SUPPORTED_BACKUP_FORMAT_VERSIONS` so older backup files can still be restored.
3. **VERSION file:** Keep `VERSION` updated on release. It is used for display and for version checks.
4. **New settings:** Use `env("NAME", "default")` for new .env variables so existing installations do not break.
5. **New files/features:** When adding or removing files/views/URLs, do it in one consistent version; on downgrade the code that does not reference the new files is deployed.

## Short answers to common questions

- **Can I restore a backup from v2 on v5?** Yes, if the backup format is supported (currently format "1").
- **Can I restore a backup from v5 on v2?** Only if the backup format is the same and the schema in the backup is compatible with v2 (typically a backup taken on v2).
- **Why do I get 503 after downgrade?** Because the DB still has a “newer” stored version. Run migrations backward and then `set_stored_version`, and the block is removed.
- **Do I need to do anything after restore?** No. Restore replaces the DB (and media); stored version in DB comes from the backup. The app will not block because code version is >= stored after restore (upgrade or same version).
