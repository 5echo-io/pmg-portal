"""
System theme customizations (colors, etc.) stored in DB (SystemInfo).
Superusers can override CSS variables via Admin → Server management → System customization.
Defaults come from theme-dark.css and theme-light.css; only overrides are stored and applied.
Backup/restore includes the database, so customizations are preserved.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from django.core.cache import cache

logger = logging.getLogger(__name__)

THEME_CUSTOMIZATIONS_KEY = "theme_customizations"

# Default values from theme-dark.css (:root) and theme-light.css (html.theme-light).
# Used for admin form placeholders, reset-to-default, and validation.
# When adding new variables in theme-*.css, add them here for customization support.
DEFAULT_THEME_VARS = {
    "dark": {
        "--bg": "#0b1220",
        "--card": "#121b2d",
        "--topbar-bg": "#0c1426",
        "--footer-bg": "#0c1426",
        "--input-bg": "#0e1626",
        "--text": "#e9eef8",
        "--muted": "#a9b4c7",
        "--line": "#22304b",
        "--btn": "#1e2a44",
        "--btnHover": "#2a3a5c",
        "--accent": "#3b82f6",
        "--accent-hover": "#2563eb",
        "--accent-light": "#60a5fa",
        "--accent-rgb": "59, 130, 246",
        "--on-accent": "#ffffff",
        "--danger": "#b91c1c",
        "--danger-hover": "#991b1b",
        "--danger-rgb": "185, 28, 28",
        "--on-danger": "#ffffff",
        "--success": "#16a34a",
        "--success-light": "#4ade80",
        "--success-rgb": "22, 163, 74",
        "--warning-rgb": "245, 158, 11",
        "--shadow": "rgba(0, 0, 0, 0.25)",
        "--shadow-strong": "rgba(0, 0, 0, 0.4)",
        "--overlay": "rgba(0, 0, 0, 0.7)",
        "--focus-ring": "rgba(59, 130, 246, 0.4)",
        "--avatar-gradient-start": "#3b82f6",
        "--avatar-gradient-end": "#8b5cf6",
        "--toast-success-border": "rgba(22, 163, 74, 0.4)",
        "--toast-success-bg": "rgba(22, 163, 74, 0.12)",
        "--toast-error-border": "rgba(239, 68, 68, 0.4)",
        "--toast-error-bg": "rgba(239, 68, 68, 0.12)",
        "--toast-warning-border": "rgba(245, 158, 11, 0.4)",
        "--toast-warning-bg": "rgba(245, 158, 11, 0.12)",
        "--toast-info-border": "rgba(59, 130, 246, 0.4)",
        "--toast-info-bg": "rgba(59, 130, 246, 0.12)",
    },
    "light": {
        "--bg": "#f1f5f9",
        "--card": "#ffffff",
        "--topbar-bg": "#ffffff",
        "--footer-bg": "#f8fafc",
        "--input-bg": "#ffffff",
        "--text": "#0f172a",
        "--muted": "#475569",
        "--line": "#cbd5e1",
        "--btn": "#f1f5f9",
        "--btnHover": "#e2e8f0",
        "--accent": "#2563eb",
        "--accent-hover": "#1d4ed8",
        "--accent-light": "#3b82f6",
        "--accent-rgb": "37, 99, 235",
        "--on-accent": "#ffffff",
        "--danger": "#c53030",
        "--danger-hover": "#a61e1e",
        "--danger-rgb": "197, 48, 48",
        "--on-danger": "#ffffff",
        "--success": "#15803d",
        "--success-light": "#22c55e",
        "--success-rgb": "21, 128, 61",
        "--warning-rgb": "245, 158, 11",
        "--shadow": "rgba(0, 0, 0, 0.08)",
        "--shadow-strong": "rgba(0, 0, 0, 0.12)",
        "--overlay": "rgba(0, 0, 0, 0.5)",
        "--focus-ring": "rgba(37, 99, 235, 0.4)",
        "--avatar-gradient-start": "#3b82f6",
        "--avatar-gradient-end": "#8b5cf6",
        "--toast-success-border": "rgba(21, 128, 61, 0.4)",
        "--toast-success-bg": "rgba(21, 128, 61, 0.1)",
        "--toast-error-border": "rgba(220, 38, 38, 0.4)",
        "--toast-error-bg": "rgba(220, 38, 38, 0.1)",
        "--toast-warning-border": "rgba(245, 158, 11, 0.4)",
        "--toast-warning-bg": "rgba(245, 158, 11, 0.1)",
        "--toast-info-border": "rgba(37, 99, 235, 0.4)",
        "--toast-info-bg": "rgba(37, 99, 235, 0.1)",
    },
}

# Human-readable labels for admin form
VARIABLE_LABELS = {
    "--bg": "Page background",
    "--card": "Cards & modals",
    "--topbar-bg": "Topbar background",
    "--footer-bg": "Footer background",
    "--input-bg": "Input fields",
    "--text": "Main text",
    "--muted": "Muted text",
    "--line": "Borders & dividers",
    "--btn": "Button (default)",
    "--btnHover": "Button (hover)",
    "--accent": "Accent / primary",
    "--accent-hover": "Accent (hover)",
    "--accent-light": "Accent (light)",
    "--accent-rgb": "Accent (RGB, for opacity)",
    "--on-accent": "Text on accent",
    "--danger": "Danger / delete",
    "--danger-hover": "Danger (hover)",
    "--danger-rgb": "Danger (RGB)",
    "--on-danger": "Text on danger",
    "--success": "Success",
    "--success-light": "Success (light)",
    "--success-rgb": "Success (RGB)",
    "--warning-rgb": "Warning (RGB)",
    "--shadow": "Shadow",
    "--shadow-strong": "Shadow (strong)",
    "--overlay": "Modal overlay",
    "--focus-ring": "Focus ring",
    "--avatar-gradient-start": "Avatar gradient start",
    "--avatar-gradient-end": "Avatar gradient end",
    "--toast-success-border": "Toast success border",
    "--toast-success-bg": "Toast success bg",
    "--toast-error-border": "Toast error border",
    "--toast-error-bg": "Toast error bg",
    "--toast-warning-border": "Toast warning border",
    "--toast-warning-bg": "Toast warning bg",
    "--toast-info-border": "Toast info border",
    "--toast-info-bg": "Toast info bg",
}
THEME_VAR_ORDER = list(DEFAULT_THEME_VARS["dark"].keys())


def get_theme_customizations() -> dict[str, dict[str, str]]:
    """
    Return custom theme overrides from DB. Only keys that are customized are present.
    Returns {"dark": {...}, "light": {...}}. Empty dicts if none set.
    """
    cache_key = "theme_customizations"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        from portal.models import SystemInfo
        row = SystemInfo.objects.filter(key=THEME_CUSTOMIZATIONS_KEY).first()
        if not row or not row.value.strip():
            result = {"dark": {}, "light": {}}
        else:
            data = json.loads(row.value)
            if not isinstance(data, dict):
                result = {"dark": {}, "light": {}}
            else:
                dark = data.get("dark")
                light = data.get("light")
                result = {
                    "dark": dict(dark) if isinstance(dark, dict) else {},
                    "light": dict(light) if isinstance(light, dict) else {},
                }
        cache.set(cache_key, result, 300)
        return result
    except Exception as e:
        logger.exception("get_theme_customizations: %s", e)
        return {"dark": {}, "light": {}}


def set_theme_customizations(data: dict[str, Any]) -> None:
    """
    Save theme customizations to DB. data = {"dark": {"--accent": "#..."}, "light": {...}}.
    Only stores keys that are valid (exist in DEFAULT_THEME_VARS) and non-empty.
    """
    out = {"dark": {}, "light": {}}
    for theme in ("dark", "light"):
        defaults = DEFAULT_THEME_VARS.get(theme, {})
        incoming = data.get(theme)
        if not isinstance(incoming, dict):
            continue
        for key, value in incoming.items():
            if key in defaults and value is not None and str(value).strip():
                out[theme][key] = str(value).strip()
    try:
        from portal.models import SystemInfo
        value = json.dumps(out, indent=2)
        SystemInfo.objects.update_or_create(
            key=THEME_CUSTOMIZATIONS_KEY,
            defaults={"value": value},
        )
        cache.delete("theme_customizations")
    except Exception as e:
        logger.exception("set_theme_customizations: %s", e)
        raise


def get_default_theme_vars() -> dict[str, dict[str, str]]:
    """Return copy of default theme variables (for admin form and reset)."""
    return {
        "dark": dict(DEFAULT_THEME_VARS["dark"]),
        "light": dict(DEFAULT_THEME_VARS["light"]),
    }


def build_theme_override_css(overrides: dict[str, dict[str, str]]) -> str:
    """
    Build inline CSS block for theme overrides. Only outputs variables that are set.
    overrides = {"dark": {"--accent": "#..."}, "light": {...}}
    """
    lines = []
    if overrides.get("dark"):
        lines.append(":root {")
        for k, v in overrides["dark"].items():
            if k.startswith("--") and v:
                lines.append(f"  {k}: {v};")
        lines.append("}")
    if overrides.get("light"):
        lines.append("html.theme-light {")
        for k, v in overrides["light"].items():
            if k.startswith("--") and v:
                lines.append(f"  {k}: {v};")
        lines.append("}")
    return "\n".join(lines) if lines else ""
