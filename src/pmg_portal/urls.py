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
from django.conf import settings
from django.conf.urls.static import static

# Import admin config for whitelabel
from . import admin_config  # noqa: F401

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    # Custom admin (new UI) at /admin/ (namespace admin_app for {% url 'admin_app:...' %})
    path("admin/", include(("admin_app.urls", "admin_app"))),
    # Django's built-in admin at /admin-django/ (no collision)
    path("admin-django/", admin.site.urls),
    path("account/", include("accounts.urls")),
    # Portal at site root: / and /switch/<id>/
    path("", include("portal.urls")),
    path("debug/", include("web.urls")),
]

# Serve media files (in development, or as fallback in production if nginx is not configured)
# In production, nginx should serve /media/ directly for better performance
# Note: static() works in both DEBUG and non-DEBUG modes, but nginx is preferred for production
if settings.MEDIA_ROOT.exists():
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
