"""
Custom admin views. Staff required; some actions require superuser.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST, require_http_methods
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
import os
import tempfile
from pathlib import Path

from portal.models import (
    Customer,
    CustomerMembership,
    PortalLink,
    Facility,
    Rack,
    RackSeal,
    NetworkDevice,
    IPAddress,
    FacilityDocument,
)
from django.utils import timezone
from django.utils.translation import gettext as _


def _get_cancel_url(request, default):
    """Return URL for Cancel button: request.GET next, or same-origin referer, or default."""
    next_url = request.GET.get("next")
    if next_url:
        return next_url
    referer = request.META.get("HTTP_REFERER") or ""
    if referer and getattr(settings, "ALLOWED_HOSTS", None):
        try:
            from urllib.parse import urlparse
            ref_host = urlparse(referer).netloc
            req_host = request.get_host()
            if ref_host == req_host and referer.startswith((request.scheme + "://", "//")):
                return referer
        except Exception:
            pass
    return default

User = get_user_model()


def staff_required(view_func):
    """Require user to be staff."""
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


def superuser_required(view_func):
    """Require user to be superuser (for User/Role management)."""
    return login_required(user_passes_test(lambda u: u.is_superuser)(view_func))


@staff_required
def admin_home(request):
    """Admin landing page with User management and Portal management boxes."""
    return render(request, "admin_app/home.html")


# ----- Users (superuser only) -----
@superuser_required
def user_list(request):
    qs = User.objects.all().order_by("username")
    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
        )
    is_staff = request.GET.get("staff", "")
    if is_staff == "1":
        qs = qs.filter(is_staff=True)
    elif is_staff == "0":
        qs = qs.filter(is_staff=False)
    is_active = request.GET.get("active", "")
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)
    paginator = Paginator(qs, 20)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)
    return render(
        request,
        "admin_app/user_list.html",
        {"page_obj": page_obj, "total_count": paginator.count, "search": search},
    )


@superuser_required
def user_add(request):
    from .forms import UserCreationForm
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created.")
            return redirect("admin_app:admin_user_list")
    else:
        form = UserCreationForm()
    return render(request, "admin_app/user_form.html", {"form": form, "user_obj": None})


@superuser_required
def user_detail(request, pk):
    """Modern user card view showing all user information."""
    user_obj = get_object_or_404(User, pk=pk)
    memberships = CustomerMembership.objects.filter(user=user_obj).select_related("customer").order_by("customer__name")
    
    return render(
        request,
        "admin_app/user_card.html",
        {
            "user_obj": user_obj,
            "memberships": memberships,
        },
    )


@superuser_required
def user_edit(request, pk):
    from .forms import UserEditForm
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect("admin_app:admin_user_detail", pk=user_obj.pk)
    else:
        form = UserEditForm(instance=user_obj)
    return render(request, "admin_app/user_form.html", {"form": form, "user_obj": user_obj})


@superuser_required
@require_POST
def user_delete(request, pk):
    """Delete a user and all related data."""
    user_obj = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user_obj == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("admin_app:admin_user_list")
    
    username = user_obj.username
    
    # Delete user (this will cascade delete CustomerMembership)
    user_obj.delete()
    
    messages.success(request, f"User '{username}' has been deleted.")
    return redirect("admin_app:admin_user_list")


# ----- Roles (Groups, superuser only) -----
@superuser_required
def role_list(request):
    qs = Group.objects.all().order_by("name")
    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(name__icontains=search)
    # Annotate with user count per group (simple: count users in each group)
    roles = []
    for g in qs:
        roles.append({"group": g, "user_count": g.user_set.count()})
    return render(request, "admin_app/role_list.html", {"roles": roles, "search": search})


@superuser_required
def role_add(request):
    from .forms import RoleForm
    if request.method == "POST":
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Role created.")
            return redirect("admin_app:admin_role_list")
    else:
        form = RoleForm()
    return render(request, "admin_app/role_form.html", {"form": form, "role": None})


@superuser_required
def role_edit(request, pk):
    from .forms import RoleForm
    role = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Role updated.")
            return redirect("admin_app:admin_role_list")
    else:
        form = RoleForm(instance=role)
    return render(request, "admin_app/role_form.html", {"form": form, "role": role})


# ----- Customers (staff) -----
@staff_required
def customer_list(request):
    qs = Customer.objects.all().order_by("name")
    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search) | Q(slug__icontains=search) | Q(org_number__icontains=search)
        )
    paginator = Paginator(qs, 20)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)
    return render(
        request,
        "admin_app/customer_list.html",
        {"page_obj": page_obj, "total_count": paginator.count, "search": search},
    )


@staff_required
def customer_add(request):
    from .forms import CustomerForm
    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Customer created.")
            return redirect("admin_app:admin_customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()
    return render(request, "admin_app/customer_form.html", {"form": form, "customer": None})


@staff_required
def customer_detail(request, pk):
    """Modern customer card view showing all customer information."""
    customer = get_object_or_404(Customer, pk=pk)
    memberships = CustomerMembership.objects.filter(customer=customer).select_related("user").order_by("user__username")
    portal_links = PortalLink.objects.filter(customer=customer).order_by("sort_order", "title")
    
    return render(
        request,
        "admin_app/customer_card.html",
        {
            "customer": customer,
            "memberships": memberships,
            "portal_links": portal_links,
        },
    )


@staff_required
@require_POST
def customer_logo_upload(request, pk):
    """Handle logo upload via AJAX."""
    customer = get_object_or_404(Customer, pk=pk)
    
    if "logo" not in request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)
    
    logo_file = request.FILES["logo"]
    
    # Validate file type
    if not logo_file.content_type.startswith("image/"):
        return JsonResponse({"error": "File must be an image"}, status=400)
    
    # Store old logo info before saving new one
    old_logo_name = None
    old_logo_path = None
    if customer.logo:
        try:
            old_logo_name = customer.logo.name
            old_logo_path = customer.logo.path
        except Exception:
            pass
    
    # Save new logo
    import logging
    logger = logging.getLogger(__name__)
    
    # Ensure media directory exists before saving
    from django.conf import settings
    media_root = settings.MEDIA_ROOT
    customer_logos_dir = media_root / "customer_logos"
    try:
        customer_logos_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured customer_logos directory exists: {customer_logos_dir}")
    except Exception as e:
        logger.error(f"Failed to create customer_logos directory: {e}")
    
    # Save the logo
    logger.info(f"About to save logo file: {logo_file.name}, size: {logo_file.size}")
    
    # Explicitly save the file to storage before assigning to model
    # This ensures the file is actually written to disk
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    # Read file content
    logo_file.seek(0)  # Reset file pointer
    file_content = logo_file.read()
    logo_file.seek(0)  # Reset again for Django
    
    # Generate filename
    import uuid
    file_ext = os.path.splitext(logo_file.name)[1]
    unique_filename = f"{os.path.splitext(logo_file.name)[0]}_{uuid.uuid4().hex[:8]}{file_ext}"
    storage_path = f"customer_logos/{unique_filename}"
    
    # Save file to storage
    try:
        saved_name = default_storage.save(storage_path, ContentFile(file_content))
        logger.info(f"File saved to storage: {saved_name}")
        
        # Now assign to model
        customer.logo = saved_name
        customer.save()
        
        # Verify the file exists
        if default_storage.exists(saved_name):
            logger.info(f"Verified file exists in storage: {saved_name}")
        else:
            logger.error(f"File does not exist in storage after save: {saved_name}")
    except Exception as e:
        logger.error(f"Error saving file to storage: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Fallback to original method
        customer.logo = logo_file
        customer.save()
    
    # Refresh from database to get updated logo info
    customer.refresh_from_db()
    
    # Verify file was saved
    if customer.logo:
        try:
            saved_path = customer.logo.path
            file_exists = os.path.exists(saved_path)
            logger.info(f"Logo saved: {customer.logo.name}, path: {saved_path}, exists: {file_exists}")
            if not file_exists:
                logger.warning(f"Logo file not found at expected path: {saved_path}")
                # List directory contents to debug
                try:
                    if os.path.exists(customer_logos_dir):
                        files_in_dir = os.listdir(customer_logos_dir)
                        logger.info(f"Files in customer_logos directory: {files_in_dir}")
                    else:
                        logger.warning(f"customer_logos directory does not exist: {customer_logos_dir}")
                except Exception as e:
                    logger.error(f"Error listing directory: {e}")
                logger.info(f"MEDIA_ROOT: {media_root}, exists: {media_root.exists()}")
                # Check permissions
                try:
                    import stat
                    if os.path.exists(media_root):
                        st = os.stat(media_root)
                        logger.info(f"MEDIA_ROOT permissions: {oct(stat.S_IMODE(st.st_mode))}, owner: {st.st_uid}, group: {st.st_gid}")
                except Exception as e:
                    logger.error(f"Error checking permissions: {e}")
        except Exception as e:
            logger.error(f"Error checking logo path: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Delete old logo file if it exists and is different from new one
    if old_logo_path and old_logo_name:
        try:
            # Check if old file is different from new file
            if customer.logo and customer.logo.name != old_logo_name:
                if os.path.exists(old_logo_path):
                    os.remove(old_logo_path)
                    logger.info(f"Deleted old logo: {old_logo_path}")
                    # Also try to remove directory if empty
                    try:
                        old_dir = os.path.dirname(old_logo_path)
                        if os.path.exists(old_dir) and not os.listdir(old_dir):
                            os.rmdir(old_dir)
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Failed to delete old logo: {e}")
    
    # Get logo URL - always return URL even if file check fails
    logo_url = None
    if customer.logo and customer.logo.name:
        try:
            logo_url = customer.logo_url()
        except Exception as e:
            logger.error(f"Error getting logo_url: {e}")
        
        # Fallback: construct URL manually
        if not logo_url:
            from django.conf import settings
            logo_url = settings.MEDIA_URL + customer.logo.name
    
    return JsonResponse({"success": True, "logo_url": logo_url})


@staff_required
@require_POST
def customer_logo_delete(request, pk):
    """Handle logo deletion via AJAX."""
    customer = get_object_or_404(Customer, pk=pk)
    
    if not customer.logo:
        return JsonResponse({"error": "No logo to delete"}, status=400)
    
    try:
        logo_path = None
        logo_name = customer.logo.name
        
        # Get path before deletion
        try:
            logo_path = customer.logo.path
        except Exception:
            pass
        
        # Delete the logo field (this should delete the file via Django's storage)
        customer.logo.delete(save=False)  # Don't save yet
        customer.save()  # Save the model
        
        # Also try to remove file manually if still exists
        if logo_path and os.path.exists(logo_path):
            try:
                os.remove(logo_path)
                # Try to remove empty directory
                try:
                    logo_dir = os.path.dirname(logo_path)
                    if os.path.exists(logo_dir) and not os.listdir(logo_dir):
                        os.rmdir(logo_dir)
                except Exception:
                    pass
            except Exception:
                pass
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting logo: {e}")
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"success": True})


@staff_required
def customer_edit(request, pk):
    from .forms import CustomerForm
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # Store old logo info before form processing
        old_logo_name = None
        old_logo_path = None
        if customer.logo:
            try:
                old_logo_name = customer.logo.name
                old_logo_path = customer.logo.path
            except Exception:
                pass
        
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            # Check if a new logo file was actually uploaded
            new_logo_uploaded = 'logo' in request.FILES and request.FILES['logo']
            
            # Save the form (this will save the new logo if uploaded)
            saved_customer = form.save()
            
            # If a new logo was uploaded and we had an old one, delete the old file
            if new_logo_uploaded and old_logo_path and old_logo_name:
                try:
                    # Refresh to get new logo name
                    saved_customer.refresh_from_db()
                    # Only delete if the new logo is different from the old one
                    if not saved_customer.logo or saved_customer.logo.name != old_logo_name:
                        if os.path.exists(old_logo_path):
                            os.remove(old_logo_path)
                            # Try to remove empty directory
                            try:
                                old_dir = os.path.dirname(old_logo_path)
                                if os.path.exists(old_dir) and not os.listdir(old_dir):
                                    os.rmdir(old_dir)
                            except Exception:
                                pass
                except Exception:
                    pass  # Silently fail if file deletion fails
            
            messages.success(request, "Customer updated.")
            return redirect("admin_app:admin_customer_detail", pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, "admin_app/customer_form.html", {"form": form, "customer": customer})


@staff_required
@require_POST
def customer_delete(request, pk):
    """Delete a customer and all related data."""
    customer = get_object_or_404(Customer, pk=pk)
    customer_name = customer.name
    
    # Delete customer (this will cascade delete CustomerMembership and PortalLink)
    # The model's delete() method will also handle logo file deletion
    customer.delete()
    
    messages.success(request, f"Customer '{customer_name}' has been deleted.")
    return redirect("admin_app:admin_customer_list")


# ----- Customer access (CustomerMembership, staff) -----
@staff_required
def customer_access_list(request):
    qs = CustomerMembership.objects.select_related("user", "customer").all().order_by("customer__name", "user__username")
    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(user__username__icontains=search)
            | Q(user__email__icontains=search)
            | Q(customer__name__icontains=search)
        )
    role_filter = request.GET.get("role", "")
    if role_filter:
        qs = qs.filter(role=role_filter)
    customer_filter = request.GET.get("customer", "")
    if customer_filter:
        qs = qs.filter(customer_id=customer_filter)
    paginator = Paginator(qs, 20)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)
    customers = Customer.objects.all().order_by("name")
    return render(
        request,
        "admin_app/customer_access_list.html",
        {
            "page_obj": page_obj,
            "total_count": paginator.count,
            "search": search,
            "customers": customers,
        },
    )


@staff_required
def customer_access_add(request):
    from .forms import CustomerMembershipForm
    customer_id = request.GET.get("customer")
    redirect_to = request.GET.get("redirect_to", "admin_app:admin_customer_access_list")
    
    if request.method == "POST":
        form = CustomerMembershipForm(request.POST)
        if form.is_valid():
            membership = form.save()
            messages.success(request, "Access added.")
            # If customer_id was provided, redirect to customer card
            if customer_id:
                return redirect("admin_app:admin_customer_detail", pk=customer_id)
            return redirect(redirect_to)
    else:
        form = CustomerMembershipForm()
        # Pre-select customer if provided
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
                form.fields["customer"].initial = customer
            except Customer.DoesNotExist:
                pass
    return render(request, "admin_app/customer_access_form.html", {"form": form, "membership": None})


@staff_required
def customer_access_edit(request, pk):
    from .forms import CustomerMembershipForm
    membership = get_object_or_404(CustomerMembership, pk=pk)
    customer_id = request.GET.get("customer")
    redirect_to = request.GET.get("redirect_to", "admin_app:admin_customer_access_list")
    
    if request.method == "POST":
        form = CustomerMembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, "Access updated.")
            # If customer_id was provided, redirect to customer card
            if customer_id:
                return redirect("admin_app:admin_customer_detail", pk=customer_id)
            return redirect(redirect_to)
    else:
        form = CustomerMembershipForm(instance=membership)
    return render(request, "admin_app/customer_access_form.html", {"form": form, "membership": membership})


# ----- Portal links (staff) -----
@staff_required
def portal_link_list(request):
    qs = PortalLink.objects.select_related("customer").all().order_by("customer__name", "sort_order", "title")
    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(title__icontains=search) | Q(url__icontains=search) | Q(customer__name__icontains=search)
        )
    customer_filter = request.GET.get("customer", "")
    if customer_filter:
        qs = qs.filter(customer_id=customer_filter)
    paginator = Paginator(qs, 20)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)
    customers = Customer.objects.all().order_by("name")
    return render(
        request,
        "admin_app/portal_link_list.html",
        {
            "page_obj": page_obj,
            "total_count": paginator.count,
            "search": search,
            "customers": customers,
        },
    )


@staff_required
def portal_link_add(request):
    from .forms import PortalLinkForm
    customer_id = request.GET.get("customer")
    redirect_to = request.GET.get("redirect_to", "admin_app:admin_portal_link_list")
    
    if request.method == "POST":
        form = PortalLinkForm(request.POST)
        if form.is_valid():
            link = form.save()
            messages.success(request, "Portal link created.")
            # If customer_id was provided, redirect to customer card
            if customer_id:
                return redirect("admin_app:admin_customer_detail", pk=customer_id)
            return redirect(redirect_to)
    else:
        form = PortalLinkForm()
        # Pre-select customer if provided
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
                form.fields["customer"].initial = customer
            except Customer.DoesNotExist:
                pass
    return render(request, "admin_app/portal_link_form.html", {"form": form, "link": None})


@staff_required
def portal_link_edit(request, pk):
    from .forms import PortalLinkForm
    link = get_object_or_404(PortalLink, pk=pk)
    customer_id = request.GET.get("customer")
    redirect_to = request.GET.get("redirect_to", "admin_app:admin_portal_link_list")
    
    if request.method == "POST":
        form = PortalLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, "Portal link updated.")
            # If customer_id was provided, redirect to customer card
            if customer_id:
                return redirect("admin_app:admin_customer_detail", pk=customer_id)
            return redirect(redirect_to)
    else:
        form = PortalLinkForm(instance=link)
    return render(request, "admin_app/portal_link_form.html", {"form": form, "link": link})


# ----- Facilities (staff) -----
@staff_required
def facility_list(request):
    qs = Facility.objects.all().order_by("name")
    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(
            Q(name__icontains=search) | Q(slug__icontains=search) | Q(address__icontains=search) | Q(city__icontains=search)
        )
    is_active = request.GET.get("active", "")
    if is_active == "1":
        qs = qs.filter(is_active=True)
    elif is_active == "0":
        qs = qs.filter(is_active=False)
    paginator = Paginator(qs, 20)
    page = request.GET.get("page", 1)
    page_obj = paginator.get_page(page)
    return render(
        request,
        "admin_app/facility_list.html",
        {"page_obj": page_obj, "total_count": paginator.count, "search": search},
    )


@staff_required
def facility_add(request):
    from .forms import FacilityForm
    if request.method == "POST":
        form = FacilityForm(request.POST)
        if form.is_valid():
            facility = form.save()
            messages.success(request, _("Facility created."))
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = FacilityForm()
    cancel_url = _get_cancel_url(request, reverse("admin_app:admin_facility_list"))
    return render(request, "admin_app/facility_form.html", {"form": form, "facility": None, "cancel_url": cancel_url})


@staff_required
def facility_detail(request, slug):
    """Modern facility card view showing all facility information."""
    facility = get_object_or_404(Facility, slug=slug)
    customers = facility.customers.all().order_by("name")
    racks = facility.racks.filter(is_active=True).order_by("name")
    network_devices = facility.network_devices.filter(is_active=True).order_by("rack", "rack_position", "name")
    ip_addresses = facility.ip_addresses.all().order_by("ip_address")
    documents = facility.documents.all().order_by("-uploaded_at")
    
    return render(
        request,
        "admin_app/facility_card.html",
        {
            "facility": facility,
            "customers": customers,
            "racks": racks,
            "network_devices": network_devices,
            "ip_addresses": ip_addresses,
            "documents": documents,
        },
    )


@staff_required
def facility_edit(request, slug):
    from .forms import FacilityForm
    facility = get_object_or_404(Facility, slug=slug)
    in_modal = request.GET.get("modal") == "1"
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.method == "POST":
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, _("Facility updated."))
            if in_modal:
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = FacilityForm(instance=facility)
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else _get_cancel_url(request, detail_url)
    return render(request, "admin_app/facility_form.html", {"form": form, "facility": facility, "cancel_url": cancel_url})


@staff_required
@require_POST
def facility_delete(request, slug):
    """Delete a facility and all related data."""
    facility = get_object_or_404(Facility, slug=slug)
    facility_name = facility.name
    
    # Delete facility (this will cascade delete related models)
    facility.delete()
    
    messages.success(request, _("Facility '%(name)s' has been deleted.") % {"name": facility_name})
    return redirect("admin_app:admin_facility_list")


def _modal_close_html(message_type):
    """Return minimal HTML that posts message to parent and closes modal (for use in iframe)."""
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Lukker</title></head>
<body>
<p>Lukker...</p>
<script>
(function() {
  try {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: '%s' }, '*');
    }
  } catch (e) {}
})();
</script>
</body></html>"""
    return HttpResponse(html % message_type, content_type="text/html; charset=utf-8")


@staff_required
def facility_modal_close(request, facility_slug):
    """Minimal page loaded in iframe after modal form save; sends postMessage so parent closes modal and reloads."""
    get_object_or_404(Facility, slug=facility_slug)
    return _modal_close_html("pmg-facility-modal-close")


@staff_required
def rack_modal_close(request, facility_slug, rack_id):
    """Minimal page loaded in iframe after rack modal form save; sends postMessage so parent closes modal and reloads."""
    get_object_or_404(Rack, pk=rack_id, facility__slug=facility_slug)
    return _modal_close_html("pmg-rack-edit-saved")


@staff_required
def facility_customers_edit(request, facility_slug):
    """Edit facility customer access (checkboxes); used in modal from facility detail."""
    from .forms import FacilityCustomersEditForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    in_modal = request.GET.get("modal") == "1"
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.method == "POST":
        form = FacilityCustomersEditForm(request.POST, facility=facility)
        if form.is_valid():
            form.save(facility)
            messages.success(request, _("Customer access updated."))
            if in_modal:
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect(detail_url)
    else:
        form = FacilityCustomersEditForm(facility=facility)
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else detail_url
    return render(request, "admin_app/facility_customers_edit.html", {
        "form": form,
        "facility": facility,
        "cancel_url": cancel_url,
    })


@staff_required
@require_POST
def facility_customer_remove(request, facility_slug, customer_id):
    """Remove a customer from the facility's access list."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    customer = get_object_or_404(Customer, pk=customer_id)
    if not facility.customers.filter(pk=customer_id).exists():
        messages.error(request, _("That customer does not have access to this facility."))
        return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    
    facility.customers.remove(customer)
    messages.success(request, _("'%(name)s' no longer has access to this facility.") % {"name": customer.name})
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


@staff_required
def facility_customer_add(request, facility_slug):
    """Add a customer to the facility's access list."""
    from .forms import FacilityCustomerAddForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    in_modal = request.GET.get("modal") == "1"
    if request.method == "POST":
        form = FacilityCustomerAddForm(request.POST, facility=facility)
        if form.is_valid():
            customer = form.cleaned_data["customer"]
            facility.customers.add(customer)
            messages.success(request, _("'%(name)s' now has access to this facility.") % {"name": customer.name})
            if in_modal:
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect(detail_url)
    else:
        form = FacilityCustomerAddForm(facility=facility)
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else detail_url
    return render(request, "admin_app/facility_customer_add.html", {
        "form": form,
        "facility": facility,
        "cancel_url": cancel_url,
    })


# ----- Racks -----
@staff_required
def rack_add(request, facility_slug):
    """Add a new rack to a facility."""
    from .forms import RackForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    
    in_modal = request.GET.get("modal") == "1"
    return_to_facility = request.GET.get("return_to") == "facility"
    if request.method == "POST":
        form = RackForm(request.POST, facility=facility)
        if form.is_valid():
            rack = form.save(commit=False)
            rack.facility = facility
            rack.save()
            messages.success(request, "Rack created.")
            if in_modal and request.POST.get("return_to") == "facility":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_rack_detail", facility_slug=facility.slug, rack_id=rack.pk)
    else:
        form = RackForm(facility=facility)
    
    facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if (in_modal and return_to_facility) else _get_cancel_url(request, facility_url)
    return render(request, "admin_app/rack_form.html", {
        "form": form,
        "facility": facility,
        "rack": None,
        "cancel_url": cancel_url,
        "return_to_facility": return_to_facility,
        "in_modal": in_modal,
    })


@staff_required
def rack_detail(request, facility_slug, rack_id):
    """View rack details with interactive rack visualization."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    rack = get_object_or_404(Rack, pk=rack_id, facility=facility)
    active_seals = rack.get_active_seals()
    all_seals = rack.seals.all().order_by("-installed_at")
    devices = rack.get_devices_by_position()
    
    # Create a list of U positions (1 to height_units)
    u_positions = list(range(1, rack.height_units + 1))
    # Create a dict mapping U position to device
    devices_by_position = {device.rack_position: device for device in devices if device.rack_position}
    
    return render(request, "admin_app/rack_detail.html", {
        "facility": facility,
        "rack": rack,
        "active_seals": active_seals,
        "all_seals": all_seals,
        "devices": devices,
        "u_positions": u_positions,
        "devices_by_position": devices_by_position,
    })


@staff_required
def rack_edit(request, facility_slug, rack_id):
    """Edit a rack."""
    from .forms import RackForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    rack = get_object_or_404(Rack, pk=rack_id, facility=facility)
    
    in_modal = request.GET.get("modal") == "1"
    return_to_facility = request.GET.get("return_to") == "facility"
    if request.method == "POST":
        form = RackForm(request.POST, instance=rack, facility=facility)
        if form.is_valid():
            form.save()
            messages.success(request, "Rack updated.")
            if in_modal and request.POST.get("return_to") == "facility":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            detail_url = reverse("admin_app:admin_rack_detail", kwargs={"facility_slug": facility.slug, "rack_id": rack.pk})
            if in_modal:
                return redirect("admin_app:admin_rack_modal_close", facility_slug=facility.slug, rack_id=rack.pk)
            return redirect(detail_url)
    else:
        form = RackForm(instance=rack, facility=facility)
    
    detail_url = reverse("admin_app:admin_rack_detail", kwargs={"facility_slug": facility.slug, "rack_id": rack.pk})
    facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if in_modal and return_to_facility:
        cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug})
    elif in_modal:
        cancel_url = reverse("admin_app:admin_rack_modal_close", kwargs={"facility_slug": facility.slug, "rack_id": rack.pk})
    else:
        cancel_url = _get_cancel_url(request, detail_url)
    return render(request, "admin_app/rack_form.html", {
        "form": form,
        "facility": facility,
        "rack": rack,
        "cancel_url": cancel_url,
        "return_to_facility": return_to_facility,
        "in_modal": in_modal,
    })


@staff_required
@require_POST
def rack_delete(request, facility_slug, rack_id):
    """Delete a rack."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    rack = get_object_or_404(Rack, pk=rack_id, facility=facility)
    rack_name = rack.name
    
    rack.delete()
    
    messages.success(request, f"Rack '{rack_name}' has been deleted.")
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


# ----- Rack Seals -----
@staff_required
def rack_seal_add(request, facility_slug, rack_id):
    """Add a seal to a rack."""
    from .forms import RackSealForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    rack = get_object_or_404(Rack, pk=rack_id, facility=facility)
    
    if request.method == "POST":
        form = RackSealForm(request.POST, rack=rack, user=request.user)
        if form.is_valid():
            seal = form.save(commit=False)
            seal.rack = rack
            seal.installed_by = request.user
            seal.save()
            messages.success(request, f"Seal '{seal.seal_id}' installed.")
            return redirect("admin_app:admin_rack_detail", facility_slug=facility.slug, rack_id=rack.pk)
    else:
        form = RackSealForm(rack=rack, user=request.user)
    
    # Cancel goes back to rack detail with Seals tab active
    cancel_url = reverse("admin_app:admin_rack_detail", kwargs={"facility_slug": facility.slug, "rack_id": rack.pk}) + "#seals"
    return render(request, "admin_app/rack_seal_form.html", {
        "form": form,
        "facility": facility,
        "rack": rack,
        "cancel_url": cancel_url,
    })


@staff_required
def rack_seal_remove(request, facility_slug, rack_id, seal_id):
    """Remove a seal from a rack."""
    from .forms import RackSealRemovalForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    rack = get_object_or_404(Rack, pk=rack_id, facility=facility)
    seal = get_object_or_404(RackSeal, pk=seal_id, rack=rack)
    
    if seal.removed_at:
        messages.error(request, "This seal has already been removed.")
        return redirect("admin_app:admin_rack_detail", facility_slug=facility.slug, rack_id=rack.pk)
    
    if request.method == "POST":
        form = RackSealRemovalForm(request.POST, instance=seal, user=request.user)
        if form.is_valid():
            seal = form.save(commit=False)
            seal.removed_at = timezone.now()
            seal.removed_by = request.user
            seal.save()
            messages.success(request, f"Seal '{seal.seal_id}' removed.")
            return redirect("admin_app:admin_rack_detail", facility_slug=facility.slug, rack_id=rack.pk)
    else:
        form = RackSealRemovalForm(instance=seal, user=request.user)
    
    cancel_url = reverse("admin_app:admin_rack_detail", kwargs={"facility_slug": facility.slug, "rack_id": rack.pk}) + "#seals"
    return render(request, "admin_app/rack_seal_remove_form.html", {
        "form": form,
        "facility": facility,
        "rack": rack,
        "seal": seal,
        "cancel_url": cancel_url,
    })


# ----- Network Devices (global list) -----
@staff_required
def network_device_list(request):
    """List all network devices across facilities with search and filter."""
    qs = NetworkDevice.objects.select_related("facility", "rack").filter(is_active=True).order_by("facility__name", "name")
    search = (request.GET.get("q") or "").strip()
    facility_slug = request.GET.get("facility") or ""
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(serial_number__icontains=search)
            | Q(manufacturer__icontains=search)
            | Q(model__icontains=search)
        )
    if facility_slug:
        qs = qs.filter(facility__slug=facility_slug)
    facilities = Facility.objects.filter(is_active=True).order_by("name")
    total_count = qs.count()
    paginator = Paginator(qs, 25)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "admin_app/network_device_list.html", {
        "page_obj": page_obj,
        "total_count": total_count,
        "search": search,
        "facility_slug": facility_slug,
        "facilities": facilities,
    })


# ----- Network Devices (per-facility add/edit) -----
@staff_required
def network_device_add(request, facility_slug, rack_id=None, rack_position=None):
    """Add a new network device to a facility, optionally to a specific rack and position."""
    from .forms import NetworkDeviceForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    rack = None
    if rack_id:
        rack = get_object_or_404(Rack, pk=rack_id, facility=facility)
    
    in_modal = request.GET.get("modal") == "1"
    rack_detail_url = reverse("admin_app:admin_rack_detail", kwargs={"facility_slug": facility.slug, "rack_id": rack.pk}) if rack else None
    if request.method == "POST":
        form = NetworkDeviceForm(request.POST, facility=facility, rack=rack, rack_position=rack_position)
        if form.is_valid():
            device = form.save(commit=False)
            device.facility = facility
            if rack:
                device.rack = rack
            if rack_position:
                device.rack_position = rack_position
            device.save()
            messages.success(request, "Network device created.")
            if rack:
                if in_modal:
                    return redirect("admin_app:admin_rack_modal_close", facility_slug=facility.slug, rack_id=rack.pk)
                return redirect(rack_detail_url)
            else:
                facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
                if in_modal or request.POST.get("return_to") == "facility":
                    return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
                return redirect(facility_url)
    else:
        form = NetworkDeviceForm(facility=facility, rack=rack, rack_position=rack_position)
    
    return_to_facility = request.GET.get("return_to") == "facility" and not rack
    if rack:
        cancel_url = reverse("admin_app:admin_rack_modal_close", kwargs={"facility_slug": facility.slug, "rack_id": rack.pk}) if in_modal else (rack_detail_url + "#devices")
    else:
        facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
        cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if (in_modal and return_to_facility) else _get_cancel_url(request, facility_url)
    return render(request, "admin_app/network_device_form.html", {
        "form": form,
        "facility": facility,
        "rack": rack,
        "device": None,
        "cancel_url": cancel_url,
        "return_to_facility": return_to_facility,
    })


@staff_required
def network_device_edit(request, facility_slug, device_id):
    """Edit a network device."""
    from .forms import NetworkDeviceForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    device = get_object_or_404(NetworkDevice, pk=device_id, facility=facility)
    in_modal = request.GET.get("modal") == "1"
    return_to_facility = request.GET.get("return_to") == "facility"
    rack_detail_url = reverse("admin_app:admin_rack_detail", kwargs={"facility_slug": facility.slug, "rack_id": device.rack.pk}) if device.rack else None
    facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.method == "POST":
        form = NetworkDeviceForm(request.POST, instance=device, facility=facility)
        if form.is_valid():
            form.save()
            messages.success(request, "Network device updated.")
            if device.rack:
                if in_modal:
                    return redirect("admin_app:admin_rack_modal_close", facility_slug=facility.slug, rack_id=device.rack.pk)
                return redirect(rack_detail_url)
            else:
                if in_modal or request.POST.get("return_to") == "facility":
                    return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
                return redirect(facility_url)
    else:
        form = NetworkDeviceForm(instance=device, facility=facility)
    
    if device.rack:
        cancel_url = reverse("admin_app:admin_rack_modal_close", kwargs={"facility_slug": facility.slug, "rack_id": device.rack.pk}) if in_modal else (rack_detail_url + "#devices")
    else:
        cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if (in_modal and return_to_facility) else _get_cancel_url(request, facility_url)
    return render(request, "admin_app/network_device_form.html", {
        "form": form,
        "facility": facility,
        "rack": device.rack,
        "device": device,
        "cancel_url": cancel_url,
        "return_to_facility": return_to_facility,
    })


@staff_required
@require_POST
def network_device_remove_from_rack(request, facility_slug, rack_id, device_id):
    """Remove a device from a rack (clear rack and rack_position)."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    rack = get_object_or_404(Rack, pk=rack_id, facility=facility)
    device = get_object_or_404(NetworkDevice, pk=device_id, facility=facility, rack=rack)
    
    device.rack = None
    device.rack_position = None
    device.save()
    
    messages.success(request, f"Device '{device.name}' removed from rack.")
    return redirect("admin_app:admin_rack_detail", facility_slug=facility.slug, rack_id=rack.pk)


@staff_required
@require_POST
def network_device_delete(request, facility_slug, device_id):
    """Delete a network device."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    device = get_object_or_404(NetworkDevice, pk=device_id, facility=facility)
    device_name = device.name
    device.delete()
    messages.success(request, f"Device '{device_name}' has been deleted.")
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


# ----- IP Addresses -----
def _debug_log(hypothesis_id, location, message, data=None):
    # #region agent log
    try:
        import json
        _p = Path(__file__).resolve().parent.parent.parent / ".cursor" / "debug.log"
        _p.parent.mkdir(parents=True, exist_ok=True)
        with open(_p, "a", encoding="utf-8") as _f:
            _f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data or {}, "timestamp": __import__("time").time() * 1000}) + "\n")
    except Exception:
        pass
    # #endregion

@staff_required
def ip_address_add(request, facility_slug):
    """Add an IP address to a facility."""
    # #region agent log
    _debug_log("H4", "views.py:ip_address_add:entry", "ip_address_add called", {"path": request.path, "method": request.method, "GET": dict(request.GET), "facility_slug": facility_slug})
    # #endregion
    from .forms import IPAddressForm
    try:
        facility = get_object_or_404(Facility, slug=facility_slug)
    except Exception as e:
        # #region agent log
        _debug_log("H2", "views.py:ip_address_add:get_facility", "get_object_or_404 raised", {"error": type(e).__name__, "message": str(e)})
        # #endregion
        raise
    # #region agent log
    _debug_log("H2", "views.py:ip_address_add:after_facility", "facility resolved", {"facility_pk": facility.pk, "facility_name": getattr(facility, "name", None)})
    # #endregion
    in_modal = request.GET.get("modal") == "1"
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    
    if request.method == "POST":
        form = IPAddressForm(request.POST, facility=facility)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.facility = facility
            obj.save()
            messages.success(request, _("IP address %(ip)s added.") % {"ip": str(obj.ip_address)})
            if in_modal:
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = IPAddressForm(facility=facility)
    
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else _get_cancel_url(request, detail_url)
    # #region agent log
    _debug_log("H3", "views.py:ip_address_add:before_render", "about to render template", {"template": "admin_app/ip_address_form.html", "in_modal": in_modal, "form_errors": form.errors if hasattr(form, "errors") else None})
    # #endregion
    try:
        response = render(request, "admin_app/ip_address_form.html", {
            "form": form,
            "facility": facility,
            "ip_address": None,
            "cancel_url": cancel_url,
            "in_modal": in_modal,
        })
        # #region agent log
        _debug_log("H3", "views.py:ip_address_add:after_render", "render succeeded", {"status": response.status_code})
        # #endregion
        return response
    except Exception as e:
        # #region agent log
        _debug_log("H1", "views.py:ip_address_add:render_exception", "render raised (template or variable error)", {"error": type(e).__name__, "message": str(e)})
        _debug_log("H5", "views.py:ip_address_add:render_exception", "render raised", {"error": type(e).__name__, "message": str(e)})
        # #endregion
        raise


@staff_required
def ip_address_edit(request, facility_slug, ip_id):
    """Edit an IP address."""
    from .forms import IPAddressForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    ip_address = get_object_or_404(IPAddress, pk=ip_id, facility=facility)
    
    if request.method == "POST":
        form = IPAddressForm(request.POST, instance=ip_address, facility=facility)
        if form.is_valid():
            form.save()
            messages.success(request, "IP address updated.")
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = IPAddressForm(instance=ip_address, facility=facility)
    
    cancel_url = _get_cancel_url(request, reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug}))
    return render(request, "admin_app/ip_address_form.html", {
        "form": form,
        "facility": facility,
        "ip_address": ip_address,
        "cancel_url": cancel_url,
    })


@staff_required
@require_POST
def ip_address_delete(request, facility_slug, ip_id):
    """Delete an IP address."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    ip_address = get_object_or_404(IPAddress, pk=ip_id, facility=facility)
    addr = str(ip_address.ip_address)
    ip_address.delete()
    messages.success(request, f"IP address {addr} has been deleted.")
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


# ----- Facility Documents -----
@staff_required
def facility_document_upload(request, facility_slug):
    """Upload a document to a facility."""
    from .forms import FacilityDocumentForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    in_modal = request.GET.get("modal") == "1"
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    
    if request.method == "POST":
        form = FacilityDocumentForm(request.POST, request.FILES, facility=facility)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.facility = facility
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, _("Document '%(title)s' uploaded.") % {"title": doc.title})
            if in_modal:
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = FacilityDocumentForm(facility=facility)
    
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else _get_cancel_url(request, detail_url)
    return render(request, "admin_app/facility_document_form.html", {
        "form": form,
        "facility": facility,
        "cancel_url": cancel_url,
        "in_modal": in_modal,
    })


@staff_required
@require_POST
def facility_document_delete(request, facility_slug, doc_id):
    """Delete a facility document."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    doc = get_object_or_404(FacilityDocument, pk=doc_id, facility=facility)
    title = doc.title
    doc.delete()
    messages.success(request, f"Document '{title}' has been deleted.")
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


# ----- Backup & Restore (superuser only) -----
@superuser_required
@require_http_methods(["GET", "POST"])
def backup_restore(request):
    """Server management: create full backup (download) or restore from uploaded backup file."""
    from . import backup_restore as br

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "backup":
            try:
                data = br.create_backup_archive()
                filename = f"pmg-portal-backup-{timezone.now().strftime('%Y%m%d-%H%M%S')}.tar.gz"
                response = HttpResponse(data, content_type="application/gzip")
                response["Content-Disposition"] = f'attachment; filename="{filename}"'
                response["Content-Length"] = len(data)
                return response
            except Exception as e:
                messages.error(request, str(e))
                return redirect("admin_app:admin_backup_restore")

        if action == "restore":
            backup_file = request.FILES.get("backup_file")
            if not backup_file:
                messages.error(request, "Please select a backup file to restore.")
                return redirect("admin_app:admin_backup_restore")
            if not backup_file.name.endswith(".tar.gz"):
                messages.error(request, "Backup file must be a .tar.gz file.")
                return redirect("admin_app:admin_backup_restore")
            try:
                with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
                    for chunk in backup_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name
                try:
                    valid, err = br.validate_backup_archive(Path(tmp_path))
                    if not valid:
                        messages.error(request, err or "Backup file validation failed.")
                        return redirect("admin_app:admin_backup_restore")
                    br.restore_from_archive(Path(tmp_path))
                    messages.success(request, "Restore completed successfully. Database and media have been restored.")
                finally:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
            except Exception as e:
                messages.error(request, f"Restore failed: {e}")
            return redirect("admin_app:admin_backup_restore")

    return render(request, "admin_app/backup_restore.html")
