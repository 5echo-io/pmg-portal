from django.urls import path
from .views import landing, debug_view

urlpatterns = [
    path("", landing, name="landing"),
    path("debug/", debug_view, name="debug"),
]
