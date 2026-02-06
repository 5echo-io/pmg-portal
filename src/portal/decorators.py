"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Custom decorators for development feature access control
Path: src/portal/decorators.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings


def dev_required(view_func):
    """
    Decorator to restrict access to development features.
    Only superusers (admins) can access dev features.
    If DEV_ACCESS_USERS is set, only those specific users have access.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if dev features are enabled
        if not settings.ENABLE_DEV_FEATURES:
            messages.error(request, "Development features are not enabled.")
            return redirect("portal_home")
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect("login")
        
        # Dev features are only for superusers (admins)
        if not request.user.is_superuser:
            messages.error(request, "Only administrators can access development features.")
            return redirect("portal_home")
        
        # If DEV_ACCESS_USERS is set, check if user is in the list
        if settings.DEV_ACCESS_USERS:
            user_identifier = request.user.email or request.user.username
            if user_identifier not in settings.DEV_ACCESS_USERS:
                messages.error(request, "You do not have access to development features.")
                return redirect("portal_home")
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
