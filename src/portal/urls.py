from django.urls import path
from .views import portal_home, switch_customer, check_updates, set_language_custom, facility_list, facility_detail

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
    path("about/check-updates/", check_updates, name="check_updates"),
    path("i18n/setlang/", set_language_custom, name="set_language_custom"),
    path("facilities/", facility_list, name="facility_list"),
    path("facilities/<int:pk>/", facility_detail, name="facility_detail"),
]
