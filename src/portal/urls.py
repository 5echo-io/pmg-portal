from django.urls import path
from .views import (
    portal_home,
    switch_customer,
    check_updates,
    set_language_custom,
    facility_list,
    facility_detail,
    portal_search,
    set_portal_preference,
    datasheet_by_slug,
    datasheet_pdf,
)

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
    path("about/check-updates/", check_updates, name="check_updates"),
    path("i18n/setlang/", set_language_custom, name="set_language_custom"),
    path("facilities/", facility_list, name="facility_list"),
    path("facilities/<slug:slug>/", facility_detail, name="facility_detail"),
    path("datasheet/<slug:slug>/", datasheet_by_slug, name="datasheet_by_slug"),
    path("datasheet/<slug:slug>/pdf/", datasheet_pdf, name="datasheet_pdf"),
    path("api/search/", portal_search, name="portal_search"),
    path("api/preferences/", set_portal_preference, name="set_portal_preference"),
]
