"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: ASGI entrypoint
Path: src/pmg_portal/asgi.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmg_portal.settings")
application = get_asgi_application()
