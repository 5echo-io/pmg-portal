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
        # Read version
        version_file = Path(settings.BASE_DIR.parent) / "VERSION"
        if version_file.exists():
            version = version_file.read_text().strip()
        
        # Read changelog preview (first few lines of Unreleased section)
        changelog_file = Path(settings.BASE_DIR.parent) / "CHANGELOG.md"
        if changelog_file.exists():
            content = changelog_file.read_text()
            # Extract Unreleased section
            if "## [Unreleased]" in content:
                unreleased = content.split("## [Unreleased]")[1].split("## [")[0]
                # Get first 3 lines of changes
                lines = [l.strip() for l in unreleased.split("\n") if l.strip() and not l.strip().startswith("#")]
                changelog_preview = "\n".join(lines[:10])  # First 10 non-empty lines
    except Exception:
        pass
    
    return {
        "app_version": version,
        "changelog_preview": changelog_preview,
        "copyright_year": "2026",
    }
