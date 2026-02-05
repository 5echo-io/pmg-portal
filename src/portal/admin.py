"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Admin configuration for portal models
Path: src/portal/admin.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.contrib import admin
from .models import Customer, CustomerMembership, PortalLink

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Customers = Client companies/organizations.
    Example: "Park Media Group AS", "Company ABC"
    """
    list_display = ("name", "slug", "member_count", "link_count")
    search_fields = ("name", "slug")
    
    prepopulated_fields = {"slug": ("name",)}
    
    def get_queryset(self, request):
        """Optimize queryset for list display."""
        qs = super().get_queryset(request)
        return qs.prefetch_related("customermembership_set", "links")
    
    def member_count(self, obj):
        if obj and obj.pk:
            return obj.customermembership_set.count()
        return "-"
    member_count.short_description = "Members"
    
    def link_count(self, obj):
        if obj and obj.pk:
            return obj.links.count()
        return "-"
    link_count.short_description = "Links"

@admin.register(CustomerMembership)
class CustomerMembershipAdmin(admin.ModelAdmin):
    """
    CustomerMembership = Links users to customers (which users belong to which companies).
    Role: "member" (regular access) or "admin" (customer admin privileges).
    """
    list_display = ("user", "customer", "role")
    list_filter = ("role", "customer")
    search_fields = ("user__username", "user__email", "customer__name")
    autocomplete_fields = ("user", "customer")

@admin.register(PortalLink)
class PortalLinkAdmin(admin.ModelAdmin):
    """
    Portal Links = Links shown on the customer's portal page (in "Quick links" section).
    These are NOT shown in the top navigation bar - they appear on the portal home page.
    """
    list_display = ("customer", "title", "url", "sort_order")
    list_filter = ("customer",)
    search_fields = ("title", "url", "customer__name")
    autocomplete_fields = ("customer",)
    list_editable = ("sort_order",)
