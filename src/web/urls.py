from django.urls import path
from .views import debug_view

urlpatterns = [
    path("", debug_view, name="debug"),
]
