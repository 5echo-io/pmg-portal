from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch
from django.contrib import messages
from .models import CustomerMembership, Customer

@login_required
def portal_home(request):
    try:
        memberships = (
            CustomerMembership.objects
            .select_related("customer")
            .prefetch_related("customer__links")
            .filter(user=request.user)
            .order_by("customer__name")
        )

        if not memberships.exists():
            return render(request, "portal/no_customer.html")

        # Get active customer from session, or use first one
        active_customer_id = request.session.get("active_customer_id")
        if active_customer_id:
            active = memberships.filter(customer_id=active_customer_id).first()
            if not active:
                # User no longer has access, reset to first
                active_customer_id = None
        
        if not active_customer_id:
            active = memberships.first()
            if active:
                request.session["active_customer_id"] = active.customer_id
        
        if not active or not active.customer:
            return render(request, "portal/no_customer.html")
            
        customer = active.customer
        # Use prefetched links if available, otherwise query
        links = list(customer.links.all())

        return render(
            request,
            "portal/customer_home.html",
            {
                "customer": customer,
                "memberships": list(memberships),
                "active_role": active.role,
                "links": links,
            },
        )
    except Exception as e:
        # Log error in production, but don't expose to user
        import logging
        logger = logging.getLogger(__name__)
        logger.exception("Error in portal_home view")
        # Fallback to no_customer template on any error
        return render(request, "portal/no_customer.html")

@login_required
def switch_customer(request, customer_id):
    """Switch active customer for the current user."""
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        referer = request.META.get("HTTP_REFERER", "/portal/")
        return redirect(referer)
    
    # Handle "All Customers" (customer_id = 0) for admin
    if customer_id == 0:
        request.session.pop("active_customer_id", None)
        messages.success(request, "Viewing all customers")
        referer = request.META.get("HTTP_REFERER", "/admin/")
        return redirect(referer)
    
    # Verify user has access to this customer
    membership = get_object_or_404(
        CustomerMembership,
        user=request.user,
        customer_id=customer_id
    )
    
    # Store in session
    request.session["active_customer_id"] = customer_id
    messages.success(request, f"Switched to {membership.customer.name}")
    
    # Redirect back to referer or portal home
    # If coming from profile page, redirect to portal instead
    referer = request.META.get("HTTP_REFERER", "/portal/")
    if "/account/profile/" in referer:
        return redirect("/portal/")
    return redirect(referer)
