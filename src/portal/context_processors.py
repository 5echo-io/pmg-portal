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
    """Add footer information to all templates."""
    version = "Unknown"
    changelog_preview = ""
    
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
            except (OSError, IOError, UnicodeDecodeError):
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
                    # Extract Unreleased section
                    if "## [Unreleased]" in content:
                        unreleased = content.split("## [Unreleased]")[1].split("## [")[0]
                        # Get first 10 lines of changes
                        lines = [l.strip() for l in unreleased.split("\n") if l.strip() and not l.strip().startswith("#")]
                        changelog_preview = "\n".join(lines[:10])
                    break
            except (OSError, IOError, UnicodeDecodeError):
                continue
    except Exception:
        # Silently fail - footer will show defaults
        pass
    
    return {
        "app_version": version,
        "changelog_preview": changelog_preview,
        "copyright_year": "2026",
    }
