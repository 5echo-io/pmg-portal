"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: URL routing
Path: src/pmg_portal/urls.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("accounts.urls")),
    path("portal/", include("portal.urls")),
    path("", include("web.urls")),
]
