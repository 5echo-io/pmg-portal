"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Portal app configuration
Path: src/portal/apps.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.apps import AppConfig
from django.core.cache import cache


class PortalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portal"
    
    def ready(self):
        """Register signals when app is ready."""
        from django.db.models.signals import post_save, post_delete
        from .models import Customer, CustomerMembership
        
        def invalidate_user_customers_cache(sender, instance, **kwargs):
            """Invalidate user_customers cache when Customer or CustomerMembership changes."""
            # If it's a CustomerMembership, invalidate cache for that user
            if isinstance(instance, CustomerMembership):
                cache_key = f"user_customers_{instance.user_id}"
                cache.delete(cache_key)
            # If it's a Customer, invalidate cache for all users with memberships
            elif isinstance(instance, Customer):
                # Invalidate cache for all users with memberships for this customer
                # This is a bit expensive, but ensures cache consistency
                # In practice, we could be more selective, but for simplicity we clear all
                # The cache will rebuild on next request
                from .models import CustomerMembership
                user_ids = CustomerMembership.objects.filter(customer=instance).values_list('user_id', flat=True)
                for user_id in user_ids:
                    cache.delete(f"user_customers_{user_id}")
                # Also clear superuser cache (they see all customers)
                # We use a pattern to clear all user_customers_* keys
                # For simplicity, we'll let the cache expire naturally (5 min) or clear on next superuser request
        
        # Connect signals
        post_save.connect(invalidate_user_customers_cache, sender=Customer)
        post_save.connect(invalidate_user_customers_cache, sender=CustomerMembership)
        post_delete.connect(invalidate_user_customers_cache, sender=Customer)
        post_delete.connect(invalidate_user_customers_cache, sender=CustomerMembership)
