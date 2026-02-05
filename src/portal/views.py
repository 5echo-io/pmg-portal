from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.contrib import messages
from django.http import HttpResponse
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
