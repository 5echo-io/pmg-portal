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
from django.db.models import Q
from .models import Customer, CustomerMembership, PortalLink
from .forms import CustomerMembershipForm

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
    
    Customer admins can manage memberships for their own customer.
    PMG admins (superusers) can manage all memberships.
    """
    list_display = ("user", "customer", "role")
    list_filter = ("role", "customer")
    search_fields = ("user__username", "user__email", "customer__name")
    autocomplete_fields = ("user",)
    form = CustomerMembershipForm
    
    def get_fieldsets(self, request, obj=None):
        """Return fieldsets based on add/edit mode."""
        if obj is None:
            # Adding: show customers (multi-select)
            return [
                (None, {'fields': ('user', 'customers', 'role')}),
            ]
        else:
            # Editing: show customer (single select)
            return [
                (None, {'fields': ('user', 'customer', 'role')}),
            ]
    
    def get_form(self, request, obj=None, **kwargs):
        """Return form with request context for permission filtering."""
        form_class = super().get_form(request, obj, **kwargs)
        
        class CustomerMembershipFormWithRequest(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request
                super().__init__(*args, **kwargs)
        
        return CustomerMembershipFormWithRequest
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # PMG admins see all memberships
            return qs
        else:
            # Customer admins only see memberships for their customer
            admin_customers = Customer.objects.filter(
                customermembership__user=request.user,
                customermembership__role=CustomerMembership.ROLE_ADMIN
            )
            return qs.filter(customer__in=admin_customers)
    
    def has_add_permission(self, request):
        """Allow customer admins to add memberships for their customer."""
        if request.user.is_superuser:
            return True
        # Check if user is a customer admin
        return CustomerMembership.objects.filter(
            user=request.user,
            role=CustomerMembership.ROLE_ADMIN
        ).exists()
    
    def has_change_permission(self, request, obj=None):
        """Allow customer admins to change memberships for their customer."""
        if request.user.is_superuser:
            return True
        if obj is None:
            return self.has_add_permission(request)
        # Check if user is admin for this customer
        return CustomerMembership.objects.filter(
            user=request.user,
            customer=obj.customer,
            role=CustomerMembership.ROLE_ADMIN
        ).exists()
    
    def has_delete_permission(self, request, obj=None):
        """Allow customer admins to delete memberships for their customer."""
        if request.user.is_superuser:
            return True
        if obj is None:
            return self.has_add_permission(request)
        # Check if user is admin for this customer
        return CustomerMembership.objects.filter(
            user=request.user,
            customer=obj.customer,
            role=CustomerMembership.ROLE_ADMIN
        ).exists()
    
    def save_model(self, request, obj, form, change):
        """Handle saving multiple memberships from multi-select when adding."""
        # If editing (change=True), use normal save
        if change:
            super().save_model(request, obj, form, change)
            return
        
        # If adding new, check for multi-select customers
        customers = form.cleaned_data.get('customers', [])
        if customers and len(customers) > 0:
            # Create/update memberships for each selected customer
            created_count = 0
            updated_count = 0
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            
            for customer in customers:
                membership, created = CustomerMembership.objects.get_or_create(
                    user=user,
                    customer=customer,
                    defaults={'role': role}
                )
                if not created:
                    # Update role if membership already exists
                    membership.role = role
                    membership.save()
                    updated_count += 1
                else:
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f'Created {created_count} customer membership(s).')
            if updated_count > 0:
                messages.info(request, f'Updated {updated_count} existing membership(s).')
        else:
            # Fallback to single customer (shouldn't happen with required field)
            super().save_model(request, obj, form, change)

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
