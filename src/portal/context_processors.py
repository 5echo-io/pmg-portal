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
from .models import CustomerMembership, Customer


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

    # Resolve active_customer_id from session
    active_customer_id = request.session.get("active_customer_id")
    if active_customer_id is not None:
        if request.user.is_superuser:
            if not Customer.objects.filter(pk=active_customer_id).exists():
                active_customer_id = None
        else:
            if not any(m.customer_id == active_customer_id for m in user_customers_list):
                active_customer_id = None

    if active_customer_id is None and user_customers_list:
        first = user_customers_list[0]
        active_customer_id = getattr(first, "customer_id", None) or first.customer.id

    return {
        "user_customers": user_customers_list,
        "active_customer_id": active_customer_id,
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
    }
    
    # Return defaults if no request
    if not request or not hasattr(request, 'path'):
        return defaults
    
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
                        # Non–full MAJOR (0.x, beta, alpha): short view always shows Unreleased (one section only)
                        if "## [Unreleased]" in content:
                            after = content.split("## [Unreleased]", 1)[1]
                            unreleased = after.split("\n## ")[0].strip()
                            changelog_section = unreleased or "Ingen unreleased endringer."
                        else:
                            changelog_section = "Ingen unreleased endringer."
                    break
            except (OSError, IOError, UnicodeDecodeError, PermissionError):
                continue
    except Exception as e:
        # Silently fail - footer will show defaults
        # Log error only if DEBUG is enabled
        import logging
        logger = logging.getLogger(__name__)
        if settings.DEBUG:
            logger.exception("Error in footer_info context processor")
        return defaults
    
    return {
        "app_version": version,
        "changelog_section": changelog_section,
        "changelog_full": changelog_full,
        "show_changelog_button": show_changelog_button,
        "copyright_year": "2026",
    }
