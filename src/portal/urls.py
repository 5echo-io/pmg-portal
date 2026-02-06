from django.urls import path
from django.conf import settings
from .views import portal_home, switch_customer, check_updates, set_language_custom

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
    path("about/check-updates/", check_updates, name="check_updates"),
    path("i18n/setlang/", set_language_custom, name="set_language_custom"),
]

# Only add facility routes if dev features are enabled and views exist
if settings.ENABLE_DEV_FEATURES:
    try:
        from .views import facility_list, facility_detail
        # Check if views are actual functions (not stubs)
        if callable(facility_list) and hasattr(facility_list, '__name__'):
            urlpatterns += [
                path("facilities/", facility_list, name="facility_list"),
                path("facilities/<int:pk>/", facility_detail, name="facility_detail"),
            ]
    except (ImportError, AttributeError):
        # Views don't exist or are stubs (old code), skip facility routes
        pass
