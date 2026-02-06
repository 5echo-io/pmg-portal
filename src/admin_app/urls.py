"""
Custom admin URL routes. All under /admin/ (Django admin is at /admin-django/).
"""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_home, name="admin_home"),
    path("users/", views.user_list, name="admin_user_list"),
    path("users/add/", views.user_add, name="admin_user_add"),
    path("users/<int:pk>/edit/", views.user_edit, name="admin_user_edit"),
    path("roles/", views.role_list, name="admin_role_list"),
    path("roles/add/", views.role_add, name="admin_role_add"),
    path("roles/<int:pk>/edit/", views.role_edit, name="admin_role_edit"),
    path("customers/", views.customer_list, name="admin_customer_list"),
    path("customers/add/", views.customer_add, name="admin_customer_add"),
    path("customers/<int:pk>/", views.customer_detail, name="admin_customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="admin_customer_edit"),
    path("customers/<int:pk>/logo/", views.customer_logo_upload, name="admin_customer_logo_upload"),
    path("customers/<int:pk>/logo/delete/", views.customer_logo_delete, name="admin_customer_logo_delete"),
    path("customers/access/", views.customer_access_list, name="admin_customer_access_list"),
    path("customers/access/add/", views.customer_access_add, name="admin_customer_access_add"),
    path("customers/access/<int:pk>/edit/", views.customer_access_edit, name="admin_customer_access_edit"),
    path("portal-links/", views.portal_link_list, name="admin_portal_link_list"),
    path("portal-links/add/", views.portal_link_add, name="admin_portal_link_add"),
    path("portal-links/<int:pk>/edit/", views.portal_link_edit, name="admin_portal_link_edit"),
]
