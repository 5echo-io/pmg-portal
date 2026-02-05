from django.contrib import admin
from .models import Customer, CustomerMembership, PortalLink

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")

@admin.register(CustomerMembership)
class CustomerMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "customer", "role")
    list_filter = ("role", "customer")
    search_fields = ("user__username", "customer__name")

@admin.register(PortalLink)
class PortalLinkAdmin(admin.ModelAdmin):
    list_display = ("customer", "title", "url", "sort_order")
    list_filter = ("customer",)
    search_fields = ("title", "url", "customer__name")
