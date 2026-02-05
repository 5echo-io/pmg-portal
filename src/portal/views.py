from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CustomerMembership

@login_required
def portal_home(request):
    try:
        memberships = (
            CustomerMembership.objects
            .select_related("customer")
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
        links = customer.links.all()

        return render(
            request,
            "portal/customer_home.html",
            {
                "customer": customer,
                "memberships": memberships,
                "active_role": active.role,
                "links": links,
            },
        )
    except Exception:
        # Fallback to no_customer template on any error
        return render(request, "portal/no_customer.html")
