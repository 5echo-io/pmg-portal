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
from django.views.static import serve

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

# Serve media files
# In production, nginx should serve /media/ directly for better performance
# But we provide Django fallback in case nginx is not configured or not working
if settings.DEBUG:
    # In DEBUG mode, use static() helper
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, use serve view as fallback (nginx should handle this, but Django can serve if needed)
    from django.views.decorators.cache import never_cache
    urlpatterns += [
        path(f"{settings.MEDIA_URL.strip('/')}/<path:path>", never_cache(serve), {
            "document_root": str(settings.MEDIA_ROOT),
            "show_indexes": False,
        }),
    ]
