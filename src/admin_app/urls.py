"""
Custom admin URL routes. All under /admin/ (Django admin is at /admin-django/).
"""
from django.urls import path

from . import views

urlpatterns = [
    path("", views.admin_home, name="admin_home"),
    path("users/", views.user_list, name="admin_user_list"),
    path("users/add/", views.user_add, name="admin_user_add"),
    path("users/<int:pk>/", views.user_detail, name="admin_user_detail"),
    path("users/<int:pk>/edit/", views.user_edit, name="admin_user_edit"),
    path("users/<int:pk>/delete/", views.user_delete, name="admin_user_delete"),
    path("roles/", views.role_list, name="admin_role_list"),
    path("roles/add/", views.role_add, name="admin_role_add"),
    path("roles/<int:pk>/edit/", views.role_edit, name="admin_role_edit"),
    path("customers/", views.customer_list, name="admin_customer_list"),
    path("customers/add/", views.customer_add, name="admin_customer_add"),
    path("customers/<int:pk>/", views.customer_detail, name="admin_customer_detail"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="admin_customer_edit"),
    path("customers/<int:pk>/delete/", views.customer_delete, name="admin_customer_delete"),
    path("customers/<int:pk>/logo/", views.customer_logo_upload, name="admin_customer_logo_upload"),
    path("customers/<int:pk>/logo/delete/", views.customer_logo_delete, name="admin_customer_logo_delete"),
    path("customers/access/", views.customer_access_list, name="admin_customer_access_list"),
    path("customers/access/add/", views.customer_access_add, name="admin_customer_access_add"),
    path("customers/access/<int:pk>/edit/", views.customer_access_edit, name="admin_customer_access_edit"),
    path("portal-links/", views.portal_link_list, name="admin_portal_link_list"),
    path("portal-links/add/", views.portal_link_add, name="admin_portal_link_add"),
    path("portal-links/<int:pk>/edit/", views.portal_link_edit, name="admin_portal_link_edit"),
    path("network-devices/", views.network_device_list, name="admin_network_device_list"),
    path("facilities/", views.facility_list, name="admin_facility_list"),
    path("facilities/add/", views.facility_add, name="admin_facility_add"),
    path("facilities/<slug:slug>/", views.facility_detail, name="admin_facility_detail"),
    path("facilities/<slug:slug>/edit/", views.facility_edit, name="admin_facility_edit"),
    path("facilities/<slug:slug>/delete/", views.facility_delete, name="admin_facility_delete"),
    path("facilities/<slug:facility_slug>/modal-close/", views.facility_modal_close, name="admin_facility_modal_close"),
    path("facilities/<slug:facility_slug>/customers/", views.facility_customers_edit, name="admin_facility_customers_edit"),
    path("facilities/<slug:facility_slug>/customers/add/", views.facility_customer_add, name="admin_facility_customer_add"),
    path("facilities/<slug:facility_slug>/customers/<int:customer_id>/remove/", views.facility_customer_remove, name="admin_facility_customer_remove"),
    # Racks
    path("facilities/<slug:facility_slug>/racks/add/", views.rack_add, name="admin_rack_add"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/", views.rack_detail, name="admin_rack_detail"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/edit/", views.rack_edit, name="admin_rack_edit"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/modal-close/", views.rack_modal_close, name="admin_rack_modal_close"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/delete/", views.rack_delete, name="admin_rack_delete"),
    # Rack Seals
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/seals/add/", views.rack_seal_add, name="admin_rack_seal_add"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/seals/<int:seal_id>/remove/", views.rack_seal_remove, name="admin_rack_seal_remove"),
    # Network Devices
    path("facilities/<slug:facility_slug>/devices/add/", views.network_device_add, name="admin_network_device_add"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/devices/add/", views.network_device_add, name="admin_network_device_add_to_rack"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/devices/add/<int:rack_position>/", views.network_device_add, name="admin_network_device_add_to_position"),
    path("facilities/<slug:facility_slug>/devices/<int:device_id>/edit/", views.network_device_edit, name="admin_network_device_edit"),
    path("facilities/<slug:facility_slug>/racks/<int:rack_id>/devices/<int:device_id>/remove/", views.network_device_remove_from_rack, name="admin_network_device_remove_from_rack"),
    path("facilities/<slug:facility_slug>/devices/<int:device_id>/delete/", views.network_device_delete, name="admin_network_device_delete"),
    # IP Addresses
    path("facilities/<slug:facility_slug>/ip/add/", views.ip_address_add, name="admin_ip_address_add"),
    path("facilities/<slug:facility_slug>/ip/<int:ip_id>/edit/", views.ip_address_edit, name="admin_ip_address_edit"),
    path("facilities/<slug:facility_slug>/ip/<int:ip_id>/delete/", views.ip_address_delete, name="admin_ip_address_delete"),
    # Facility Documents
    path("facilities/<slug:facility_slug>/documents/upload/", views.facility_document_upload, name="admin_facility_document_upload"),
    path("facilities/<slug:facility_slug>/documents/<int:doc_id>/delete/", views.facility_document_delete, name="admin_facility_document_delete"),
    # Server management (superuser only)
    path("server/backup-restore/", views.backup_restore, name="admin_backup_restore"),
]
