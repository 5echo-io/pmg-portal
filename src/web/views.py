"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Web views (landing, debug)
Path: src/web/views.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
import os
import logging
from pathlib import Path
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.http import JsonResponse
from django.db import connection

def landing(request):
    # If user is authenticated, redirect to portal, otherwise to login
    if request.user.is_authenticated:
        return redirect("/portal/")
    return redirect("/account/login/")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def debug_view(request):
    """Debug view for system information and logs."""
    debug_data = {
        "system": {},
        "django": {},
        "database": {},
        "files": {},
        "logs": [],
    }
    
    try:
        # System info
        import sys
        import django
        debug_data["system"]["python_version"] = sys.version
        debug_data["system"]["django_version"] = django.get_version()
        debug_data["system"]["debug"] = settings.DEBUG
        debug_data["system"]["base_dir"] = str(settings.BASE_DIR)
        
        # Database info
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            debug_data["database"]["postgres_version"] = cursor.fetchone()[0] if cursor.rowcount > 0 else "Unknown"
            cursor.execute("SELECT current_database();")
            debug_data["database"]["database_name"] = cursor.fetchone()[0] if cursor.rowcount > 0 else "Unknown"
        
        # File paths
        version_paths = [
            Path(settings.BASE_DIR.parent) / "VERSION",
            Path(settings.BASE_DIR) / ".." / "VERSION",
            Path("/opt/pmg-portal/VERSION"),
        ]
        debug_data["files"]["version_file"] = None
        for vp in version_paths:
            if vp.exists():
                debug_data["files"]["version_file"] = str(vp)
                try:
                    debug_data["files"]["version_content"] = vp.read_text(encoding='utf-8').strip()
                except Exception as e:
                    debug_data["files"]["version_error"] = str(e)
                break
        
        changelog_paths = [
            Path(settings.BASE_DIR.parent) / "CHANGELOG.md",
            Path(settings.BASE_DIR) / ".." / "CHANGELOG.md",
            Path("/opt/pmg-portal/CHANGELOG.md"),
        ]
        debug_data["files"]["changelog_file"] = None
        for cp in changelog_paths:
            if cp.exists():
                debug_data["files"]["changelog_file"] = str(cp)
                debug_data["files"]["changelog_size"] = cp.stat().st_size
                break
        
        # Recent logs (if available)
        logger = logging.getLogger('django')
        if hasattr(logger, 'handlers'):
            debug_data["logs"] = ["Log handlers available"]
        
        # Context processor test
        debug_data["django"]["context_processors"] = [
            "portal.context_processors.user_customers",
            "portal.context_processors.footer_info",
        ]
        
    except Exception as e:
        debug_data["error"] = str(e)
        import traceback
        debug_data["traceback"] = traceback.format_exc()
    
    if request.GET.get('format') == 'json':
        return JsonResponse(debug_data)
    
    return render(request, "web/debug.html", {
        "debug_data": debug_data,
    })
