"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Admin configuration for portal models
Path: src/portal/admin.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import path
from .models import Customer, CustomerMembership, PortalLink
from .forms import BulkCustomerMembershipForm

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
        """Get queryset - optimize only for changelist."""
        qs = super().get_queryset(request)
        # Only optimize for changelist view
        try:
            if hasattr(request, 'resolver_match') and request.resolver_match:
                url_name = getattr(request.resolver_match, 'url_name', '')
                if url_name and 'changelist' in url_name:
                    return qs.prefetch_related("customermembership_set", "links")
        except Exception:
            pass
        return qs
    
    def member_count(self, obj):
        """Return member count, safely handling new objects."""
        if not obj or not obj.pk:
            return "-"
        try:
            # Try to use prefetched data if available
            if hasattr(obj, '_prefetched_objects_cache'):
                cache = obj._prefetched_objects_cache
                if 'customermembership_set' in cache:
                    return len(cache['customermembership_set'])
            # Fallback to count query
            return obj.customermembership_set.count()
        except Exception:
            return "-"
    member_count.short_description = "Members"
    
    def link_count(self, obj):
        """Return link count, safely handling new objects."""
        if not obj or not obj.pk:
            return "-"
        try:
            # Try to use prefetched data if available
            if hasattr(obj, '_prefetched_objects_cache'):
                cache = obj._prefetched_objects_cache
                if 'links' in cache:
                    return len(cache['links'])
            # Fallback to count query
            return obj.links.count()
        except Exception:
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
    change_list_template = "admin/portal/customermembership/change_list.html"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-add/', self.admin_site.admin_view(self.bulk_add_view), name='portal_customermembership_bulk_add'),
        ]
        return custom_urls + urls
    
    def bulk_add_view(self, request):
        """Custom view for bulk adding CustomerMemberships."""
        if request.method == 'POST':
            form = BulkCustomerMembershipForm(request.POST)
            if form.is_valid():
                created, skipped = form.save()
                if created:
                    messages.success(request, f'Created {len(created)} customer membership(s).')
                if skipped:
                    messages.info(request, f'Updated {len(skipped)} existing membership(s).')
                return redirect('admin:portal_customermembership_changelist')
        else:
            form = BulkCustomerMembershipForm()
        
        # Set user queryset for autocomplete
        from django.contrib.auth import get_user_model
        User = get_user_model()
        form.fields['user'].queryset = User.objects.all()
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Bulk Add Customer Memberships',
            'form': form,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request, None),
        }
        return render(request, 'admin/portal/customermembership/bulk_add.html', context)

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
