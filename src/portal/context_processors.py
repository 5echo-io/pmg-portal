"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Context processors for templates
Path: src/portal/context_processors.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from pathlib import Path
from types import SimpleNamespace
from django.conf import settings
from django.utils import translation
from django.core.cache import cache
import re
import urllib.request
import urllib.error
import json
from django.db.models import Q, F
from .models import CustomerMembership, Customer, PortalUserPreference, Facility


def language_menu(request):
    """Add current language and other languages for the language switcher (avatar menu and login page)."""
    current = translation.get_language() or settings.LANGUAGE_CODE
    # Normalize to base code (e.g. en-us -> en)
    current_base = current.split("-")[0] if current else "en"
    languages = list(settings.LANGUAGES)
    current_name = dict(languages).get(current_base, "English")
    other_languages = [{"code": code, "name": name} for code, name in languages if code != current_base]
    return {
        "current_language_code": current_base,
        "current_language_name": current_name,
        "other_languages": other_languages,
    }


def user_customers(request):
    """Add user's customer list to all templates. Superusers get all customers."""
    if not request or not request.user or not request.user.is_authenticated:
        return {
            "user_customers": [],
            "active_customer_id": None,
        }

    # Cache key based on user ID and authentication status
    cache_key = f"user_customers_{request.user.id}"
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        user_customers_list = cached_result
    else:
        # Superusers see and can switch to all customers (no membership required)
        if request.user.is_superuser:
            customers = Customer.objects.order_by("name")
            # Wrap in objects with .customer so templates can use item.customer.id / item.customer.name
            user_customers_list = [SimpleNamespace(customer=c) for c in customers]
        else:
            memberships = (
                CustomerMembership.objects.filter(user=request.user)
                .select_related("customer")
                .order_by("customer__name")
            )
            user_customers_list = list(memberships)
        
        # Cache for 5 minutes (300 seconds) - invalidate on customer/membership changes
        cache.set(cache_key, user_customers_list, 300)

    # Resolve active_customer_id from session
    active_customer_id = request.session.get("active_customer_id")
    if active_customer_id is not None:
        if request.user.is_superuser:
            if not Customer.objects.filter(pk=active_customer_id).exists():
                active_customer_id = None
        else:
            if not any(m.customer_id == active_customer_id for m in user_customers_list):
                active_customer_id = None

    # Auto-select first customer only if user has exactly one customer
    # If user has multiple customers, they must explicitly choose
    if active_customer_id is None and len(user_customers_list) == 1:
        first = user_customers_list[0]
        active_customer_id = getattr(first, "customer_id", None) or first.customer.id
        # Save to session so it persists
        request.session["active_customer_id"] = active_customer_id

    # Get facilities for active customer
    user_facilities = []
    if active_customer_id:
        try:
            customer = Customer.objects.get(pk=active_customer_id)
            user_facilities = customer.facilities.filter(is_active=True).order_by("name")
        except Customer.DoesNotExist:
            pass
    
    # Theme preference for portal (light/dark/system). Prefer customer-specific over global (customer_id=None).
    portal_theme = "system"
    if request.user and request.user.is_authenticated:
        prefs = (
            PortalUserPreference.objects.filter(user=request.user)
            .filter(Q(customer_id=active_customer_id) | Q(customer__isnull=True))
            .order_by(F("customer_id").desc(nulls_last=True))
            .first()
        )
        if prefs:
            portal_theme = prefs.theme

    return {
        "user_customers": user_customers_list,
        "active_customer_id": active_customer_id,
        "user_facilities": user_facilities,
        "portal_theme": portal_theme,
    }

def footer_info(request):
    """Add footer information to all templates (portal and admin)."""
    # Always return safe defaults first
    defaults = {
        "app_version": "Unknown",
        "changelog_preview": "",
        "changelog_full": "",
        "copyright_year": "2026",
        "show_changelog_button": False,
        "release_notes_body": "",
        "release_notes_version": "",
    }
    
    # Return defaults if no request
    if not request or not hasattr(request, 'path'):
        return defaults
    
    # Cache footer info for 1 hour (3600 seconds) - version/changelog rarely changes
    cache_key = "footer_info"
    cached_result = cache.get(cache_key)
    
    if cached_result is not None:
        result = cached_result
    else:
        version = "Unknown"
        changelog_section = ""  # Will contain unreleased or current major version section
        changelog_full = ""
        show_changelog_button = False

        try:
            # Try multiple possible locations for VERSION file
            possible_paths = [
                Path(settings.BASE_DIR.parent) / "VERSION",  # /opt/pmg-portal/VERSION
                Path(settings.BASE_DIR) / ".." / "VERSION",   # Alternative path
                Path("/opt/pmg-portal/VERSION"),              # Absolute path
            ]

            for version_file in possible_paths:
                try:
                    if version_file.exists() and version_file.is_file():
                        version = version_file.read_text(encoding='utf-8').strip()
                        break
                except (OSError, IOError, UnicodeDecodeError, PermissionError):
                    continue

            # Try multiple possible locations for CHANGELOG file
            changelog_paths = [
                Path(settings.BASE_DIR.parent) / "CHANGELOG.md",
                Path(settings.BASE_DIR) / ".." / "CHANGELOG.md",
                Path("/opt/pmg-portal/CHANGELOG.md"),
            ]

            for changelog_file in changelog_paths:
                try:
                    if changelog_file.exists() and changelog_file.is_file():
                        content = changelog_file.read_text(encoding='utf-8')
                        changelog_full = content  # Store full changelog for modal
                        show_changelog_button = True

                        # Full release = plain MAJOR.MINOR.PATCH with no build (alpha/beta/rc). Any build suffix → Unreleased
                        is_full_major = (
                            "beta" not in version.lower()
                            and "alpha" not in version.lower()
                            and "rc" not in version.lower()
                            and not version.strip().startswith("0.")
                        )

                        if is_full_major:
                            # Full MAJOR release: show all sections for this major (e.g. all ## [1.x.x])
                            major_num = version.strip().split("-")[0].split(".")[0]
                            sections = []
                            rest = content
                            while "## [" in rest:
                                i = rest.index("## [")
                                segment = rest[i:]
                                j = segment[4:].find("## [")
                                block = segment[: 4 + j].rstrip() if j != -1 else segment.rstrip()
                                rest = segment[4 + j:] if j != -1 else ""
                                title = block[4 : block.index("]") + 1] if "]" in block else ""
                                if title.startswith(f"{major_num}."):
                                    sections.append(block)
                            if sections:
                                changelog_section = "\n\n".join(sections)
                            elif "## [Unreleased]" in content:
                                after = content.split("## [Unreleased]", 1)[1]
                                unreleased = after.split("\n## ")[0].strip()
                                changelog_section = unreleased or "Ingen endringer listet."
                            else:
                                changelog_section = "Ingen endringer listet."
                        else:
                            # Pre-release (beta/alpha/rc): show section for current version if present, else [Unreleased]
                            version_header = f"## [{version}]"
                            if version_header in content:
                                after = content.split(version_header, 1)[1]
                                section = after.split("\n## ")[0].strip()
                                # Drop optional date line (e.g. "- 2026-02-07") on first line
                                if section.startswith("- "):
                                    section = "\n".join(section.split("\n")[1:]).strip()
                                changelog_section = section or "Ingen endringer listet for denne versjonen."
                            elif "## [Unreleased]" in content:
                                after = content.split("## [Unreleased]", 1)[1]
                                unreleased = after.split("\n## ")[0].strip()
                                if unreleased and not unreleased.startswith("Pre-release builds"):
                                    changelog_section = unreleased
                                else:
                                    changelog_section = unreleased or "Ingen unreleased endringer."
                            else:
                                changelog_section = "Ingen endringer listet."
                        break
                except (OSError, IOError, UnicodeDecodeError, PermissionError):
                    continue
        except Exception as e:
            # Silently fail - footer will show defaults
            import logging
            logger = logging.getLogger(__name__)
            if settings.DEBUG:
                logger.exception("Error in footer_info context processor")
            return defaults

        result = {
            "app_version": version,
            "changelog_section": changelog_section,
            "changelog_full": changelog_full,
            "show_changelog_button": show_changelog_button,
            "copyright_year": "2026",
            "release_notes_body": "",
            "release_notes_version": "",
        }
        cache.set(cache_key, result, 3600)

    # Augment with release notes (language-dependent, so not cached)
    _get_release_notes_for_request(request, result)
    return result


def _get_release_notes_for_request(request, footer_result):
    """
    Augment footer result with release notes for the current version and language.
    Only for final releases (no -beta, -alpha, -rc). Not cached (language-dependent).
    """
    version = (footer_result.get("app_version") or "").strip()
    if not version:
        return
    if "beta" in version.lower() or "alpha" in version.lower() or "rc" in version.lower():
        return
    if version.startswith("0."):
        return
    # Normalize to MAJOR.MINOR.PATCH for lookup (e.g. 4.8.0)
    release_key = version.split("-")[0].strip()
    lang = (translation.get_language() or getattr(request, "LANGUAGE_CODE", None) or "en").split("-")[0]
    if lang not in ("nb", "no", "en"):
        lang = "en"
    if lang == "no":
        lang = "nb"
    notes_paths = [
        Path(settings.BASE_DIR.parent) / "RELEASE_NOTES.json",
        Path(settings.BASE_DIR) / ".." / "RELEASE_NOTES.json",
        Path("/opt/pmg-portal/RELEASE_NOTES.json"),
    ]
    for path in notes_paths:
        try:
            if path.exists() and path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and release_key in data:
                    entry = data[release_key]
                    if isinstance(entry, dict):
                        body = entry.get(lang) or entry.get("nb") or entry.get("en") or ""
                    elif isinstance(entry, str):
                        body = entry
                    else:
                        body = ""
                    if body:
                        footer_result["release_notes_body"] = body
                        footer_result["release_notes_version"] = release_key
                break
        except (OSError, IOError, UnicodeDecodeError, json.JSONDecodeError):
            continue


def theme_customizations(request):
    """
    Add theme override CSS for system customization (Admin → System customization).
    Only overrides stored in DB are applied; defaults come from theme-dark.css / theme-light.css.
    """
    try:
        from admin_app.theme_settings import get_theme_customizations, build_theme_override_css
        overrides = get_theme_customizations()
        css = build_theme_override_css(overrides)
        return {"theme_customizations_css": css, "theme_customizations": overrides}
    except Exception:
        return {"theme_customizations_css": "", "theme_customizations": {"dark": {}, "light": {}}}


def about_info(request):
    """Add About modal info: version check for admins, general info for all."""
    has_update = False
    latest_version = None
    
    # Only check for updates if user is superuser/admin
    if request and request.user and request.user.is_authenticated and request.user.is_superuser:
        # Cache the check for 1 hour to avoid hitting GitHub API too often
        cache_key = "pmg_portal_latest_version"
        cached = cache.get(cache_key)
        
        if cached is not None:
            latest_version, has_update = cached
        else:
            try:
                # Get current version
                current_version = "Unknown"
                version_paths = [
                    Path(settings.BASE_DIR.parent) / "VERSION",
                    Path(settings.BASE_DIR) / ".." / "VERSION",
                    Path("/opt/pmg-portal/VERSION"),
                ]
                for vp in version_paths:
                    try:
                        if vp.exists() and vp.is_file():
                            current_version = vp.read_text(encoding='utf-8').strip()
                            break
                    except (OSError, IOError, UnicodeDecodeError, PermissionError):
                        continue
                
                # Fetch latest version from GitHub main branch
                # GitHub API: GET /repos/{owner}/{repo}/contents/{path}?ref={branch}
                github_repo = "5echo-io/pmg-portal"
                github_branch = "main"
                github_path = "VERSION"
                api_url = f"https://api.github.com/repos/{github_repo}/contents/{github_path}?ref={github_branch}"
                
                req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github.v3+json"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    if "content" in data:
                        import base64
                        latest_version = base64.b64decode(data["content"]).decode('utf-8').strip()
                        
                        # Compare versions (simple string comparison for now)
                        # Extract version numbers (e.g., "1.17.39-beta.14" -> compare "1.17.39")
                        def normalize_version(v):
                            # Remove build suffix and extract MAJOR.MINOR.PATCH
                            v_clean = re.sub(r'-[a-z]+\.\d+$', '', v.strip())
                            parts = v_clean.split('.')
                            if len(parts) >= 3:
                                return tuple(int(p) for p in parts[:3])
                            return (0, 0, 0)
                        
                        current_norm = normalize_version(current_version)
                        latest_norm = normalize_version(latest_version)
                        has_update = latest_norm > current_norm
                
                # Cache for 1 hour (3600 seconds)
                cache.set(cache_key, (latest_version, has_update), 3600)
            except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception) as e:
                # Silently fail - no update info available
                import logging
                logger = logging.getLogger(__name__)
                if settings.DEBUG:
                    logger.debug(f"Could not check for updates: {e}")
                latest_version = None
                has_update = False
    
    return {
        "has_update_available": has_update,
        "latest_version": latest_version,
    }
