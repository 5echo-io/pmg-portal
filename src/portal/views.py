"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Portal views
Path: src/portal/views.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings
from django.utils import translation
from pathlib import Path
import re
import urllib.request
import urllib.error
import json
from .models import CustomerMembership, Customer

def _portal_home_context(request, customer, links, active_role=None, memberships=None):
    """Build context for portal home (full page or fragment)."""
    return {
        "customer": customer,
        "memberships": memberships or [],
        "active_role": active_role,
        "links": links,
    }

@login_required
def portal_home(request):
    is_htmx = request.headers.get("HX-Request") == "true"
    try:
        # Superusers: all customers; others: only memberships
        if request.user.is_superuser:
            from types import SimpleNamespace
            customers = list(Customer.objects.prefetch_related("links").order_by("name"))
            if not customers:
                if is_htmx:
                    r = render(request, "portal/fragments/no_customer_content.html", {})
                    r["HX-Trigger"] = '{"setTitle": {"title": "No customer access | PMG Portal"}}'
                    return r
                return render(request, "portal/no_customer.html")
            # Resolve active from session or first
            active_customer_id = request.session.get("active_customer_id")
            active_customer = None
            for c in customers:
                if c.id == active_customer_id:
                    active_customer = c
                    break
            if not active_customer:
                active_customer = customers[0]
                request.session["active_customer_id"] = active_customer.id
            customer = active_customer
            links = list(customer.links.all())
            ctx = _portal_home_context(request, customer, links, memberships=[SimpleNamespace(customer=c) for c in customers])
        else:
            memberships = (
                CustomerMembership.objects.filter(user=request.user)
                .select_related("customer")
                .prefetch_related("customer__links")
                .order_by("customer__name")
            )
            memberships_list = list(memberships)
            if not memberships_list:
                if is_htmx:
                    r = render(request, "portal/fragments/no_customer_content.html", {})
                    r["HX-Trigger"] = '{"setTitle": {"title": "No customer access | PMG Portal"}}'
                    return r
                return render(request, "portal/no_customer.html")

            active_customer_id = request.session.get("active_customer_id")
            active = None
            for m in memberships_list:
                if m.customer_id == active_customer_id:
                    active = m
                    break
            if not active:
                active = memberships_list[0]
                request.session["active_customer_id"] = active.customer_id
            customer = active.customer
            links = list(customer.links.all())
            ctx = _portal_home_context(request, customer, links, active.role, memberships_list)

        if is_htmx:
            r = render(request, "portal/fragments/customer_home_content.html", ctx)
            r["HX-Trigger"] = '{"setTitle": {"title": "' + (customer.name + " | PMG Portal").replace('"', '\\"') + '"}}'
            return r
        return render(request, "portal/customer_home.html", ctx)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Error in portal_home view")
        if is_htmx:
            r = render(request, "portal/fragments/no_customer_content.html", {})
            r["HX-Trigger"] = '{"setTitle": {"title": "PMG Portal"}}'
            return r
        return render(request, "portal/no_customer.html")

@login_required
def switch_customer(request, customer_id):
    """Switch active customer; always redirect to portal home (/) after switch."""
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("/")

    # Superusers can switch to any customer (no membership required)
    if request.user.is_superuser:
        customer = get_object_or_404(Customer, pk=customer_id)
        request.session["active_customer_id"] = customer_id
        messages.success(request, f"Switched to {customer.name}")
        return redirect("/")

    # Verify user has access to this customer
    membership = get_object_or_404(
        CustomerMembership,
        user=request.user,
        customer_id=customer_id,
    )
    request.session["active_customer_id"] = customer_id
    messages.success(request, f"Switched to {membership.customer.name}")
    return redirect("/")


@login_required
@require_POST
def check_updates(request):
    """Check for updates from GitHub main branch (admin only)."""
    if not request.user.is_superuser:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    # Clear cache to force fresh check
    cache_key = "pmg_portal_latest_version"
    cache.delete(cache_key)
    
    # Get current version
    current_version = "Unknown"
    version_paths = [
        Path(settings.BASE_DIR.parent) / "VERSION",
        Path(settings.BASE_DIR) / ".." / "VERSION",
        Path("/opt/pmg-portal/VERSION"),
    ]
    for vp in version_paths:
        try:
            if vp.exists() and vp.is_file():
                current_version = vp.read_text(encoding='utf-8').strip()
                break
        except (OSError, IOError, UnicodeDecodeError, PermissionError):
            continue
    
    has_update = False
    latest_version = None
    
    try:
        github_repo = "5echo-io/pmg-portal"
        github_branch = "main"
        github_path = "VERSION"
        api_url = f"https://api.github.com/repos/{github_repo}/contents/{github_path}?ref={github_branch}"
        
        req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if "content" in data:
                import base64
                latest_version = base64.b64decode(data["content"]).decode('utf-8').strip()
                
                def normalize_version(v):
                    v_clean = re.sub(r'-[a-z]+\.\d+$', '', v.strip())
                    parts = v_clean.split('.')
                    if len(parts) >= 3:
                        return tuple(int(p) for p in parts[:3])
                    return (0, 0, 0)
                
                current_norm = normalize_version(current_version)
                latest_norm = normalize_version(latest_version)
                has_update = latest_norm > current_norm
        
        # Cache for 1 hour
        cache.set(cache_key, (latest_version, has_update), 3600)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Update check failed: {e}")
    
    return JsonResponse({
        "has_update": has_update,
        "latest_version": latest_version,
        "current_version": current_version,
    })


@require_POST
def set_language_custom(request):
    """Custom set_language view that saves user preference."""
    from django.views.i18n import set_language as django_set_language
    
    # Call Django's set_language view first
    response = django_set_language(request)
    
    # If user is authenticated, save language preference to session
    if request.user.is_authenticated:
        language = request.POST.get('language', '')
        if language in dict(settings.LANGUAGES):
            # Store in session for persistence
            request.session['user_preferred_language'] = language
    
    return response
