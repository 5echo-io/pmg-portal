from django.urls import path
from .views import (
    portal_home,
    switch_customer,
    check_updates,
    set_language_custom,
    facility_list,
    facility_detail,
    facility_service_log_detail,
    facility_device_detail,
    facility_network_documentation_pdf,
    portal_search,
    set_portal_preference,
    datasheet_list,
    datasheet_by_slug,
    datasheet_pdf,
)

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("datasheets/", datasheet_list, name="datasheet_list"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
    path("about/check-updates/", check_updates, name="check_updates"),
    path("i18n/setlang/", set_language_custom, name="set_language_custom"),
    path("facilities/", facility_list, name="facility_list"),
    path("facilities/<slug:slug>/", facility_detail, name="facility_detail"),
    path("facilities/<slug:slug>/service/<int:log_id>/", facility_service_log_detail, name="facility_service_log_detail"),
    path("facilities/<slug:slug>/devices/<int:device_id>/", facility_device_detail, name="facility_device_detail"),
    path("facilities/<slug:slug>/network-documentation/pdf/", facility_network_documentation_pdf, name="facility_network_documentation_pdf"),
    path("datasheet/<slug:slug>/", datasheet_by_slug, name="datasheet_by_slug"),
    path("datasheet/<slug:slug>/pdf/", datasheet_pdf, name="datasheet_pdf"),
    path("api/search/", portal_search, name="portal_search"),
    path("api/preferences/", set_portal_preference, name="set_portal_preference"),
]
