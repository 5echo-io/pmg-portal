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
from django.urls import reverse
from django.db.models import Exists, OuterRef, Prefetch, Q
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
from django.utils import timezone
from .models import (
    CustomerMembership,
    Customer,
    Facility,
    PortalLink,
    Announcement,
    PortalUserPreference,
    NetworkDevice,
    FacilityDocument,
    ServiceLog,
    ServiceType,
    DeviceType,
    ProductDatasheet,
    DocumentTemplate,
    TechnicalSupportContact,
)


def _get_dashboard_widgets(user, customer_id):
    """Return list of enabled widget ids for this user/customer. Empty = use defaults."""
    prefs = PortalUserPreference.objects.filter(
        user=user
    ).filter(
        Q(customer_id=customer_id) | Q(customer__isnull=True)
    ).order_by("-customer_id").first()  # Prefer customer-specific
    if prefs and prefs.dashboard_widgets:
        return prefs.dashboard_widgets
    return PortalUserPreference.DEFAULT_WIDGETS


def _portal_home_context(request, customer, links, active_role=None, memberships=None):
    """Build context for portal home (full page or fragment)."""
    now = timezone.now()
    announcements = list(
        Announcement.objects.filter(customer=customer).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now)
        ).filter(
            Q(valid_until__isnull=True) | Q(valid_until__gte=now)
        ).select_related("created_by").order_by("-is_pinned", "-created_at")[:10]
    )
    facilities = Facility.objects.filter(customers=customer, is_active=True)
    facilities_count = facilities.count()
    devices_count = NetworkDevice.objects.filter(facility__customers=customer, is_active=True).count()
    quick_stats = {
        "facilities": facilities_count,
        "devices": devices_count,
        "links": len(links),
    }
    dashboard_widgets = _get_dashboard_widgets(request.user, customer.id)
    return {
        "customer": customer,
        "memberships": memberships or [],
        "active_role": active_role,
        "links": links,
        "announcements": announcements,
        "quick_stats": quick_stats,
        "dashboard_widgets": dashboard_widgets,
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
            # Resolve active from session
            active_customer_id = request.session.get("active_customer_id")
            active_customer = None
            if active_customer_id:
                for c in customers:
                    if c.id == active_customer_id:
                        active_customer = c
                        break
            
            # Auto-select if only one customer available
            if not active_customer and len(customers) == 1:
                active_customer = customers[0]
                request.session["active_customer_id"] = active_customer.id
            
            # If no active customer, show selection page
            if not active_customer:
                ctx = {
                    "customers": customers,
                    "is_superuser": True,
                }
                if is_htmx:
                    r = render(request, "portal/fragments/customer_selection_content.html", ctx)
                    r["HX-Trigger"] = '{"setTitle": {"title": "Select Customer | PMG Portal"}}'
                    return r
                return render(request, "portal/customer_selection.html", ctx)
            
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
            if active_customer_id:
                for m in memberships_list:
                    if m.customer_id == active_customer_id:
                        active = m
                        break
            
            # Auto-select if only one customer available
            if not active and len(memberships_list) == 1:
                active = memberships_list[0]
                request.session["active_customer_id"] = active.customer_id
            
            # If no active customer, show selection page
            if not active:
                customers = [m.customer for m in memberships_list]
                ctx = {
                    "customers": customers,
                    "memberships": memberships_list,
                    "is_superuser": False,
                }
                if is_htmx:
                    r = render(request, "portal/fragments/customer_selection_content.html", ctx)
                    r["HX-Trigger"] = '{"setTitle": {"title": "Select Customer | PMG Portal"}}'
                    return r
                return render(request, "portal/customer_selection.html", ctx)
            
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
    """Switch active customer; redirect back to the referring page after switch."""
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Get the referring page to redirect back to it
    referer = request.META.get('HTTP_REFERER', '/')

    # Superusers can switch to any customer (no membership required)
    if request.user.is_superuser:
        customer = get_object_or_404(Customer, pk=customer_id)
        request.session["active_customer_id"] = customer_id
        messages.success(request, f"Switched to {customer.name}")
        return redirect(referer)

    # Verify user has access to this customer
    membership = get_object_or_404(
        CustomerMembership,
        user=request.user,
        customer_id=customer_id,
    )
    request.session["active_customer_id"] = customer_id
    messages.success(request, f"Switched to {membership.customer.name}")
    return redirect(referer)


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


@login_required
def facility_list(request):
    """List all facilities the active customer has access to."""
    
    active_customer_id = request.session.get("active_customer_id")
    if not active_customer_id:
        messages.info(request, "Please select a customer profile to view facilities.")
        return redirect("portal_home")
    
    try:
        customer = Customer.objects.get(pk=active_customer_id)
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect("portal_home")
    
    # Get facilities for this customer
    facilities = Facility.objects.filter(customers=customer, is_active=True).order_by("name")
    
    is_htmx = request.headers.get("HX-Request") == "true"
    context = {
        "facilities": facilities,
        "customer": customer,
    }
    
    if is_htmx:
        r = render(request, "portal/fragments/facility_list_content.html", context)
        r["HX-Trigger"] = '{"setTitle": {"title": "Facilities | PMG Portal"}}'
        return r
    
    return render(request, "portal/facility_list.html", context)


@login_required
def facility_detail(request, slug):
    """Show detailed information about a facility."""
    facility = get_object_or_404(Facility, slug=slug, is_active=True)
    active_customer_id = request.session.get("active_customer_id")
    
    # Check if user's active customer has access to this facility
    if active_customer_id:
        try:
            customer = Customer.objects.get(pk=active_customer_id)
            if customer not in facility.customers.all():
                messages.error(request, "You do not have access to this facility.")
                return redirect("facility_list")
        except Customer.DoesNotExist:
            messages.error(request, "Customer not found.")
            return redirect("portal_home")
    else:
        messages.info(request, "Please select a customer profile to view facilities.")
        return redirect("portal_home")
    
    # Get related data
    racks = (
        facility.racks.filter(is_active=True)
        .annotate(has_sla=Exists(NetworkDevice.objects.filter(rack=OuterRef("pk"), is_sla=True)))
        .order_by("name")
    )
    network_devices = facility.network_devices.filter(is_active=True).select_related("product", "rack").order_by("rack", "rack_position", "name")
    ip_addresses = facility.ip_addresses.all().select_related("device").order_by("ip_address")
    documents = facility.documents.all().order_by("-uploaded_at")
    contacts = facility.contacts.all().order_by("sort_order", "name")
    service_logs = facility.service_logs.all().select_related("service_type").prefetch_related("attachments").order_by("-performed_at")
    service_type_filter = request.GET.get("service_type", "").strip()
    if service_type_filter:
        try:
            st = ServiceType.objects.get(slug=service_type_filter, is_active=True)
            service_logs = service_logs.filter(service_type=st)
        except ServiceType.DoesNotExist:
            pass
    service_types = ServiceType.objects.filter(is_active=True).order_by("sort_order", "name")

    # Unique product datasheets for device types used at this facility (alphabetical by title)
    from portal.models import ProductDatasheet
    device_type_ids = list(
        facility.network_devices.filter(is_active=True)
        .exclude(product_id__isnull=True)
        .values_list("product_id", flat=True)
        .distinct()
    )
    facility_datasheets = []
    if device_type_ids:
        seen = set()
        for ds in (
            ProductDatasheet.objects.filter(device_type_id__in=device_type_ids)
            .select_related("device_type")
            .order_by("title")
        ):
            if ds.device_type_id in seen:
                continue
            seen.add(ds.device_type_id)
            if ds.device_type and ds.device_type.slug:
                facility_datasheets.append(ds)
    facility_datasheets.sort(key=lambda d: (d.title or "").lower())

    # Serviceavtale: anlegget har serviceavtale hvis minst én enhet er markert med SLA
    has_serviceavtale = any(getattr(d, "is_sla", False) for d in network_devices)

    # Teknisk support / nøkkelperson (global, vist på anleggskortet)
    technical_support = TechnicalSupportContact.objects.filter(is_active=True).order_by("sort_order").first()

    # Statistics
    stats = {
        "racks_count": racks.count(),
        "network_devices_count": network_devices.count(),
        "ip_addresses_count": ip_addresses.count(),
        "documents_count": documents.count(),
        "service_logs_count": service_logs.count(),
    }

    is_htmx = request.headers.get("HX-Request") == "true"
    context = {
        "facility": facility,
        "customer": customer,
        "racks": racks,
        "network_devices": network_devices,
        "has_serviceavtale": has_serviceavtale,
        "technical_support": technical_support,
        "ip_addresses": ip_addresses,
        "documents": documents,
        "contacts": contacts,
        "service_logs": service_logs,
        "service_types": service_types,
        "service_type_filter": service_type_filter,
        "facility_datasheets": facility_datasheets,
        "stats": stats,
    }
    
    if is_htmx:
        r = render(request, "portal/fragments/facility_detail_content.html", context)
        r["HX-Trigger"] = '{"setTitle": {"title": "' + (facility.name + " | PMG Portal").replace('"', '\\"') + '"}}'
        return r
    
    return render(request, "portal/facility_detail.html", context)


@login_required
def facility_service_log_detail(request, slug, log_id):
    """Show a single service log entry for a facility."""
    facility = get_object_or_404(Facility, slug=slug, is_active=True)
    active_customer_id = request.session.get("active_customer_id")
    if not active_customer_id:
        messages.info(request, "Please select a customer profile to view facilities.")
        return redirect("portal_home")
    try:
        customer = Customer.objects.get(pk=active_customer_id)
        if customer not in facility.customers.all():
            messages.error(request, "You do not have access to this facility.")
            return redirect("facility_list")
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect("portal_home")

    service_log = get_object_or_404(
        ServiceLog.objects.select_related("service_type", "approved_by", "created_by").prefetch_related(
            "attachments",
            "serviced_devices__device",
        ),
        pk=log_id,
        facility=facility,
    )
    print_mode = request.GET.get("print") == "1"
    context = {
        "facility": facility,
        "customer": customer,
        "service_log": service_log,
        "print_mode": print_mode,
    }
    is_htmx = request.headers.get("HX-Request") == "true"
    if is_htmx:
        r = render(request, "portal/fragments/facility_service_log_detail.html", context)
        title = f"Servicelogg: {service_log.service_id} | {facility.name} | PMG Portal"
        r["HX-Trigger"] = '{"setTitle": {"title": "' + title.replace('"', '\\"') + '"}}'
        return r
    return render(request, "portal/facility_service_log_detail.html", context)


@login_required
def facility_service_log_pdf(request, slug, log_id):
    """Generate servicerapport PDF using the master document template (WeasyPrint)."""
    from django.template import Template, Context
    from io import BytesIO

    facility = get_object_or_404(Facility, slug=slug, is_active=True)
    active_customer_id = request.session.get("active_customer_id")
    if not active_customer_id:
        messages.info(request, "Please select a customer profile to view facilities.")
        return redirect("portal_home")
    try:
        customer = Customer.objects.get(pk=active_customer_id)
        if customer not in facility.customers.all():
            messages.error(request, "You do not have access to this facility.")
            return redirect("facility_list")
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect("portal_home")

    service_log = get_object_or_404(
        ServiceLog.objects.select_related("service_type", "approved_by", "facility").prefetch_related("serviced_devices__device"),
        pk=log_id,
        facility=facility,
    )
    template = DocumentTemplate.objects.filter(
        document_type=DocumentTemplate.DOCUMENT_TYPE_SERVICERAPPORT,
        is_default=True,
    ).first()
    if not template:
        template = DocumentTemplate.objects.filter(document_type=DocumentTemplate.DOCUMENT_TYPE_SERVICERAPPORT).first()
    if not template:
        messages.error(request, "No document template for servicerapport. Please contact the administrator.")
        return redirect("facility_service_log_detail", slug=slug, log_id=log_id)
    context = {
        "service_log": service_log,
        "facility": facility,
        "customer": customer,
        "now": timezone.now(),
    }
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        messages.error(request, "PDF generation is not available.")
        return redirect("facility_service_log_detail", slug=slug, log_id=log_id)
    t = Template(template.html_content)
    html_str = t.render(Context(context))
    buf = BytesIO()
    try:
        doc = HTML(string=html_str)
        stylesheets = [CSS(string=template.css_content)] if template.css_content else []
        doc.write_pdf(buf, stylesheets=stylesheets)
        buf.seek(0)
    except (OSError, AttributeError) as e:
        # Fallback to xhtml2pdf when WeasyPrint fails (missing Pango/Cairo or pydyf API mismatch)
        from xhtml2pdf import pisa
        doc_html = (
            f'<!DOCTYPE html><html><head><meta charset="utf-8"/>'
            + (f"<style>{template.css_content}</style>" if template.css_content else "")
            + "</head><body>"
            + html_str
            + "</body></html>"
        )
        buf = BytesIO()
        pisa_status = pisa.CreatePDF(doc_html.encode("utf-8"), dest=buf, encoding="utf-8")
        if pisa_status.err:
            if isinstance(e, OSError) and ("pango" in str(e).lower() or "cairo" in str(e).lower() or "cannot load library" in str(e).lower()):
                messages.error(
                    request,
                    "PDF generation failed: missing system libraries (Pango/Cairo). "
                    "Ask the server administrator to run: sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libcairo2",
                )
            else:
                messages.error(request, "PDF generation failed.")
            return redirect("facility_service_log_detail", slug=slug, log_id=log_id)
        buf.seek(0)
    filename = f"servicerapport-{service_log.service_id}-{timezone.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def facility_device_detail(request, slug, device_id):
    """Show a single network device at a facility (read-only info)."""
    facility = get_object_or_404(Facility, slug=slug, is_active=True)
    active_customer_id = request.session.get("active_customer_id")
    if not active_customer_id:
        messages.info(request, "Please select a customer profile to view facilities.")
        return redirect("portal_home")
    try:
        customer = Customer.objects.get(pk=active_customer_id)
        if customer not in facility.customers.all():
            messages.error(request, "You do not have access to this facility.")
            return redirect("facility_list")
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect("portal_home")

    device = get_object_or_404(
        NetworkDevice.objects.select_related("product", "rack").prefetch_related("ip_addresses"),
        pk=device_id,
        facility=facility,
        is_active=True,
    )
    context = {
        "facility": facility,
        "customer": customer,
        "device": device,
    }
    is_htmx = request.headers.get("HX-Request") == "true"
    if is_htmx:
        r = render(request, "portal/fragments/facility_device_detail.html", context)
        title = f"{device.name} | {facility.name} | PMG Portal"
        r["HX-Trigger"] = '{"setTitle": {"title": "' + title.replace('"', '\\"') + '"}}'
        return r
    return render(request, "portal/facility_device_detail.html", context)


@login_required
def facility_network_documentation_pdf(request, slug):
    """Export facility network documentation as PDF (equipment = network devices only, + IP overview)."""
    from io import BytesIO
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa

    facility = get_object_or_404(Facility, slug=slug, is_active=True)
    active_customer_id = request.session.get("active_customer_id")
    if not active_customer_id:
        messages.info(request, "Please select a customer profile.")
        return redirect("portal_home")
    try:
        customer = Customer.objects.get(pk=active_customer_id)
        if customer not in facility.customers.all():
            messages.error(request, "You do not have access to this facility.")
            return redirect("facility_list")
    except Customer.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect("portal_home")

    network_devices = facility.network_devices.filter(is_active=True).select_related("rack").order_by("rack", "rack_position", "name")
    ip_addresses = facility.ip_addresses.all().select_related("device").order_by("ip_address")
    html = render_to_string("portal/facility_network_documentation_pdf.html", {
        "facility": facility,
        "network_devices": network_devices,
        "ip_addresses": ip_addresses,
        "now": timezone.now(),
    })
    buf = BytesIO()
    pisa_status = pisa.CreatePDF(html.encode("utf-8"), dest=buf, encoding="utf-8")
    if pisa_status.err:
        messages.error(request, "PDF generation failed.")
        return redirect("facility_detail", slug=slug)
    buf.seek(0)
    filename = f"nettverksdokumentasjon-{facility.slug}-{timezone.now().strftime('%Y%m%d')}.pdf"
    response = HttpResponse(buf.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
def portal_search(request):
    """
    Global search for the active customer: facilities, devices, portal links, documents.
    Returns JSON: { "facilities": [...], "devices": [...], "links": [...], "documents": [...] }
    """
    active_customer_id = request.session.get("active_customer_id")
    if not active_customer_id:
        return JsonResponse({"facilities": [], "devices": [], "links": [], "documents": []})

    try:
        customer = Customer.objects.get(pk=active_customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({"facilities": [], "devices": [], "links": [], "documents": []})

    q = (request.GET.get("q") or "").strip()
    if not q:
        return JsonResponse({"facilities": [], "devices": [], "links": [], "documents": []})

    # Facilities (customer has access)
    facilities = Facility.objects.filter(customers=customer, is_active=True).filter(
        Q(name__icontains=q) | Q(description__icontains=q) | Q(address__icontains=q) | Q(city__icontains=q)
    ).order_by("name")[:15]
    # Network devices in customer's facilities
    devices = NetworkDevice.objects.filter(
        facility__customers=customer,
        facility__is_active=True,
        is_active=True,
    ).filter(
        Q(name__icontains=q) | Q(manufacturer__icontains=q) | Q(model__icontains=q) | Q(serial_number__icontains=q) | Q(description__icontains=q)
    ).select_related("facility").order_by("facility__name", "name")[:15]
    # Portal links
    links = PortalLink.objects.filter(customer=customer).filter(
        Q(title__icontains=q) | Q(description__icontains=q) | Q(url__icontains=q)
    ).order_by("sort_order", "title")[:15]
    # Facility documents (facilities customer has access to)
    documents = FacilityDocument.objects.filter(
        facility__customers=customer,
        facility__is_active=True,
    ).filter(
        Q(title__icontains=q) | Q(description__icontains=q)
    ).select_related("facility").order_by("-uploaded_at")[:10]

    def facility_item(f):
        return {"type": "facility", "id": f.id, "name": f.name, "slug": f.slug, "url": reverse("facility_detail", args=[f.slug])}

    def device_item(d):
        return {"type": "device", "id": d.id, "name": d.name, "facility": d.facility.name, "url": reverse("facility_detail", args=[d.facility.slug])}

    def link_item(l):
        return {"type": "link", "id": l.id, "title": l.title, "url": l.url}

    def doc_item(doc):
        return {"type": "document", "id": doc.id, "title": doc.title, "facility": doc.facility.name, "url": reverse("facility_detail", args=[doc.facility.slug])}

    return JsonResponse({
        "facilities": [facility_item(f) for f in facilities],
        "devices": [device_item(d) for d in devices],
        "links": [link_item(l) for l in links],
        "documents": [doc_item(d) for d in documents],
    })


@login_required
@require_POST
def set_portal_preference(request):
    """Save theme or dashboard_widgets preference. POST: theme=light|dark|system or dashboard_widgets=announcements,quick_stats,..."""
    active_customer_id = request.session.get("active_customer_id")
    customer_id = int(active_customer_id) if active_customer_id else None
    theme = (request.POST.get("theme") or "").strip()
    widgets_str = (request.POST.get("dashboard_widgets") or "").strip()

    if theme and theme in dict(PortalUserPreference.THEME_CHOICES):
        prefs, _ = PortalUserPreference.objects.get_or_create(
            user=request.user,
            customer_id=customer_id or None,
            defaults={"theme": theme, "dashboard_widgets": PortalUserPreference.DEFAULT_WIDGETS},
        )
        if prefs.theme != theme:
            prefs.theme = theme
            prefs.save(update_fields=["theme"])
        if request.headers.get("Accept", "").find("application/json") != -1:
            return JsonResponse({"ok": True, "theme": theme})
        return redirect(request.META.get("HTTP_REFERER", "/"))

    if widgets_str:
        widget_list = [w.strip() for w in widgets_str.split(",") if w.strip()]
        valid = {PortalUserPreference.WIDGET_ANNOUNCEMENTS, PortalUserPreference.WIDGET_QUICK_STATS, PortalUserPreference.WIDGET_RECENT_LINKS, PortalUserPreference.WIDGET_QUICK_LINKS}
        widget_list = [w for w in widget_list if w in valid]
        prefs, _ = PortalUserPreference.objects.get_or_create(
            user=request.user,
            customer_id=customer_id or None,
            defaults={"theme": PortalUserPreference.THEME_SYSTEM, "dashboard_widgets": widget_list or PortalUserPreference.DEFAULT_WIDGETS},
        )
        prefs.dashboard_widgets = widget_list or PortalUserPreference.DEFAULT_WIDGETS
        prefs.save(update_fields=["dashboard_widgets"])
        if request.headers.get("Accept", "").find("application/json") != -1:
            return JsonResponse({"ok": True, "dashboard_widgets": prefs.dashboard_widgets})
        return redirect(request.META.get("HTTP_REFERER", "/"))

    return JsonResponse({"ok": False}, status=400)


# ----- Product datasheet (public-style page at /datasheet/<slug>/) -----

@login_required
def datasheet_list(request):
    """List device types that have a product datasheet (portal overview)."""
    from django.db.models import Prefetch
    from django.utils.translation import gettext as _
    from portal.models import ProductDatasheet
    qs = DeviceType.objects.filter(
        is_active=True,
        datasheets__isnull=False,
    ).distinct().order_by("name").prefetch_related(
        Prefetch("datasheets", queryset=ProductDatasheet.objects.order_by("-updated_at"))
    )
    datasheet_items = []
    for dt in qs:
        primary = dt.datasheets.all()[0] if dt.datasheets.exists() else None
        datasheet_items.append({"device_type": dt, "datasheet": primary})
    return render(request, "portal/datasheet_list.html", {
        "datasheet_items": datasheet_items,
    })


@login_required
def datasheet_by_slug(request, slug):
    """Show product datasheet at /datasheet/<product-slug>/ (slug = DeviceType.slug)."""
    device_type = get_object_or_404(DeviceType, slug=slug, is_active=True)
    datasheet = (
        ProductDatasheet.objects.filter(device_type=device_type)
        .order_by("-updated_at")
        .first()
    )
    if not datasheet:
        return render(request, "portal/datasheet_not_found.html", {"device_type": device_type})
    import markdown
    content_html = ""
    if datasheet.content_md:
        content_html = markdown.markdown(
            datasheet.content_md,
            extensions=["tables", "nl2br"],
        )
    return render(request, "portal/datasheet_detail.html", {
        "datasheet": datasheet,
        "device_type": device_type,
        "content_html": content_html,
    })


@login_required
def datasheet_pdf(request, slug):
    """Download product datasheet as PDF with Park Media Group AS © year."""
    device_type = get_object_or_404(DeviceType, slug=slug, is_active=True)
    datasheet = (
        ProductDatasheet.objects.filter(device_type=device_type)
        .order_by("-updated_at")
        .first()
    )
    if not datasheet:
        return redirect("datasheet_by_slug", slug=slug)
    import markdown
    content_html = ""
    if datasheet.content_md:
        content_html = markdown.markdown(
            datasheet.content_md,
            extensions=["tables", "nl2br"],
        )
    from django.template.loader import render_to_string
    from django.utils import timezone
    from django.utils.translation import gettext as _
    year = timezone.now().year
    html = render_to_string("portal/datasheet_pdf.html", {
        "datasheet": datasheet,
        "device_type": device_type,
        "content_html": content_html,
        "copyright_year": year,
        "meta_created_label": _("Created"),
        "meta_updated_label": _("Last updated"),
        "pdf_title_suffix": _("Product datasheet"),
    })
    try:
        from xhtml2pdf import pisa
        from io import BytesIO
        result = BytesIO()
        pisa.CreatePDF(html.encode("utf-8"), result, encoding="utf-8")
        result.seek(0)
        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="datasheet-{slug}.pdf"'
        return response
    except Exception as e:
        from django.contrib import messages
        messages.error(request, f"PDF generation failed: {e}")
        return redirect("datasheet_by_slug", slug=slug)
