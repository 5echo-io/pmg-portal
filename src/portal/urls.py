from django.urls import path
from .views import portal_home, switch_customer

urlpatterns = [
    path("", portal_home, name="portal_home"),
    path("switch/<int:customer_id>/", switch_customer, name="switch_customer"),
]
