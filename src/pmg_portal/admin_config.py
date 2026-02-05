"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Admin site customization (whitelabel)
Path: src/pmg_portal/admin_config.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.contrib import admin

# Whitelabel admin site
admin.site.site_header = "PMG Portal Administration"
admin.site.site_title = "PMG Portal Admin"
admin.site.index_title = "Administration"
