"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Portal app configuration
Path: src/portal/apps.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.apps import AppConfig

class PortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portal"
