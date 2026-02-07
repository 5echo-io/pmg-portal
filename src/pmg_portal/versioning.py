"""
App version tracking for backwards compatibility across upgrades and downgrades.
Stores the installed app version in the database so we can detect downgrades
and ensure backup/restore and migrations work across versions.
"""
from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings

# Key used in SystemInfo for stored app version
VERSION_KEY = "app_version"

# Semver-like: allow digits and dots, optional -beta.x / -alpha.x
VERSION_RE = re.compile(r"^(\d+(?:\.\d+)*(?:-[a-zA-Z0-9.]+)?)\s*$")


def _version_paths() -> list[Path]:
    """Return paths to VERSION file in deployment order."""
    base = Path(settings.BASE_DIR)
    return [
        base.parent / "VERSION",   # /opt/pmg-portal/VERSION
        base / ".." / "VERSION",
        Path("/opt/pmg-portal/VERSION"),
    ]


def get_current_version() -> str | None:
    """Read current app version from VERSION file. Returns None if not found."""
    for vp in _version_paths():
        try:
            p = vp.resolve()
            if p.exists() and p.is_file():
                raw = p.read_text(encoding="utf-8").strip()
                m = VERSION_RE.match(raw)
                if m:
                    return m.group(1).strip()
                return raw.strip() or None
        except (OSError, ValueError):
            continue
    return None


def _parse_version(v: str) -> tuple[tuple[int, ...], str]:
    """Parse version string into (tuple of ints, suffix). E.g. '4.8.0-beta.2' -> ((4,8,0), '-beta.2')."""
    v = (v or "").strip()
    suffix = ""
    if "-" in v:
        v, suffix = v.split("-", 1)
        suffix = "-" + suffix
    parts = []
    for s in v.split("."):
        try:
            parts.append(int(s))
        except ValueError:
            break
    return (tuple(parts), suffix)


def version_compare(current: str | None, stored: str | None) -> int:
    """
    Compare two version strings. Returns -1 if current < stored, 0 if equal, 1 if current > stored.
    None is treated as oldest (e.g. fresh install).
    """
    if current is None and stored is None:
        return 0
    if current is None:
        return -1
    if stored is None:
        return 1
    (cur_parts, cur_suffix) = _parse_version(current)
    (stored_parts, stored_suffix) = _parse_version(stored)
    if cur_parts < stored_parts:
        return -1
    if cur_parts > stored_parts:
        return 1
    if cur_suffix < stored_suffix:
        return -1
    if cur_suffix > stored_suffix:
        return 1
    return 0


def get_stored_version() -> str | None:
    """Read app version stored in database. Returns None if table doesn't exist or key missing."""
    try:
        from portal.models import SystemInfo
        row = SystemInfo.objects.filter(key=VERSION_KEY).first()
        return (row.value.strip() or None) if row else None
    except Exception:
        return None


def set_stored_version(version: str | None) -> None:
    """Write current app version to database (called after successful migrate)."""
    from portal.models import SystemInfo
    value = (version or "").strip()
    obj, _ = SystemInfo.objects.update_or_create(
        key=VERSION_KEY,
        defaults={"value": value},
    )


def check_version_compatibility() -> tuple[bool, str | None]:
    """
    Check if current code version is compatible with the database.
    Returns (True, None) if ok (upgrade, same, or fresh).
    Returns (False, message) if downgrade detected (stored version > current).
    """
    current = get_current_version()
    stored = get_stored_version()
    cmp = version_compare(current, stored)
    if cmp >= 0:
        return True, None
    # Downgrade: stored > current
    msg = (
        f"Version downgrade detected. Database was last used with version {stored!r}, "
        f"but current code is {current!r}. To downgrade safely: run migrations backwards to match "
        f"this version (e.g. python manage.py migrate portal <migration_name>), then restart. "
        f"See BACKWARDS_COMPATIBILITY.md."
    )
    return False, msg
