from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Prefetch
from .models import CustomerMembership

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

        # For now: if multiple customers, show first one.
        # Later: add customer switcher (dropdown).
        active = memberships.first()
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
