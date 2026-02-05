"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Context processors for templates
Path: src/portal/context_processors.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from pathlib import Path
from django.conf import settings

def footer_info(request):
    """Add footer information to templates. Only runs for portal templates, not admin."""
    # Always return safe defaults first
    defaults = {
        "app_version": "Unknown",
        "changelog_preview": "",
        "changelog_full": "",
        "copyright_year": "2026",
    }
    
    # Skip for admin pages to avoid errors
    if not request or not hasattr(request, 'path') or request.path.startswith('/admin/'):
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
                    
                    # Determine which section to show based on version
                    if version.startswith("0.1.0-alpha") or "alpha" in version.lower() or "beta" in version.lower():
                        # Alpha/beta version - show Unreleased section
                        if "## [Unreleased]" in content:
                            unreleased = content.split("## [Unreleased]")[1].split("## [")[0]
                            changelog_section = unreleased.strip()
                            show_changelog_button = True
                    else:
                        # Major release - find matching version section
                        # Extract major version (e.g., "0.1.0" from "0.1.0-alpha.5")
                        major_version = version.split('-')[0] if '-' in version else version
                        version_pattern = f"## [{major_version}"
                        if version_pattern in content:
                            # Find the section for this version
                            parts = content.split(version_pattern)
                            if len(parts) > 1:
                                version_section = parts[1].split("## [")[0]
                                changelog_section = version_section.strip()
                                show_changelog_button = True
                        elif "## [Unreleased]" in content:
                            # Fallback to Unreleased if version section not found
                            unreleased = content.split("## [Unreleased]")[1].split("## [")[0]
                            changelog_section = unreleased.strip()
                            show_changelog_button = True
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
