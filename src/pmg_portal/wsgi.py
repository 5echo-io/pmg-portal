"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: WSGI entrypoint
Path: src/pmg_portal/wsgi.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmg_portal.settings")
application = get_wsgi_application()
