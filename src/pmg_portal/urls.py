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

# Import admin config for whitelabel
from . import admin_config  # noqa: F401

urlpatterns = [
    # Custom admin (new UI) at /admin/
    path("admin/", include("admin_app.urls")),
    # Django's built-in admin at /admin-django/ (no collision)
    path("admin-django/", admin.site.urls),
    path("account/", include("accounts.urls")),
    path("portal/", include("portal.urls")),
    path("", include("web.urls")),
]
