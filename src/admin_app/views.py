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
from django.utils.safestring import mark_safe
from django.utils.html import escape
import os
import tempfile
from pathlib import Path

from portal.models import (
    Customer,
    CustomerMembership,
    PortalLink,
    Announcement,
    Facility,
    Rack,
    RackSeal,
    DeviceType,
    DeviceCategory,
    Manufacturer,
    ProductDatasheet,
    NetworkDevice,
    IPAddress,
    FacilityDocument,
    ServiceLog,
    ServiceLogAttachment,
    ServiceLogDevice,
    ServiceType,
    ServiceVisit,
)
from admin_app.models import AdminNotification
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
        "admin_app/user/user_list.html",
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
    return render(request, "admin_app/user/user_form.html", {"form": form, "user_obj": None})


@superuser_required
def user_detail(request, pk):
    """Modern user card view showing all user information."""
    user_obj = get_object_or_404(User, pk=pk)
    memberships = CustomerMembership.objects.filter(user=user_obj).select_related("customer").order_by("customer__name")
    
    return render(
        request,
        "admin_app/user/user_card.html",
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
    return render(request, "admin_app/user/user_form.html", {"form": form, "user_obj": user_obj})


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
    return render(request, "admin_app/user/role_list.html", {"roles": roles, "search": search})


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
    return render(request, "admin_app/user/role_form.html", {"form": form, "role": None})


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
    return render(request, "admin_app/user/role_form.html", {"form": form, "role": role})


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
        "admin_app/customer/customer_list.html",
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
    return render(request, "admin_app/customer/customer_form.html", {"form": form, "customer": None})


@staff_required
def customer_detail(request, pk):
    """Modern customer card view showing all customer information."""
    customer = get_object_or_404(Customer, pk=pk)
    memberships = CustomerMembership.objects.filter(customer=customer).select_related("user").order_by("user__username")
    portal_links = PortalLink.objects.filter(customer=customer).order_by("sort_order", "title")
    
    return render(
        request,
        "admin_app/customer/customer_card.html",
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
    return render(request, "admin_app/customer/customer_form.html", {"form": form, "customer": customer})


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
        "admin_app/customer/customer_access_list.html",
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
    return render(request, "admin_app/customer/customer_access_form.html", {"form": form, "membership": None})


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
    return render(request, "admin_app/customer/customer_access_form.html", {"form": form, "membership": membership})


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
        "admin_app/portal/portal_link_list.html",
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
    return render(request, "admin_app/portal/portal_link_form.html", {"form": form, "link": None})


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
    return render(request, "admin_app/portal/portal_link_form.html", {"form": form, "link": link})


# ----- Announcements (staff) -----
@staff_required
def announcement_list(request):
    qs = Announcement.objects.select_related("customer", "created_by").all().order_by("-created_at")
    search = request.GET.get("q", "").strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(body__icontains=search) | Q(customer__name__icontains=search))
    customer_filter = request.GET.get("customer", "")
    if customer_filter:
        qs = qs.filter(customer_id=customer_filter)
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    customers = Customer.objects.all().order_by("name")
    return render(
        request,
        "admin_app/portal/announcement_list.html",
        {"page_obj": page_obj, "total_count": paginator.count, "search": search, "customers": customers, "customer_filter": customer_filter},
    )


@staff_required
def announcement_add(request):
    from .forms import AnnouncementForm
    customer_id = request.GET.get("customer")
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            ann = form.save(commit=False)
            ann.created_by = request.user
            ann.save()
            messages.success(request, "Announcement created.")
            return redirect("admin_app:admin_announcement_list")
    else:
        form = AnnouncementForm()
        if customer_id:
            try:
                form.fields["customer"].initial = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                pass
    return render(request, "admin_app/portal/announcement_form.html", {"form": form, "announcement": None})


@staff_required
def announcement_edit(request, pk):
    from .forms import AnnouncementForm
    ann = get_object_or_404(Announcement, pk=pk)
    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=ann)
        if form.is_valid():
            form.save()
            messages.success(request, "Announcement updated.")
            return redirect("admin_app:admin_announcement_list")
    else:
        form = AnnouncementForm(instance=ann)
    return render(request, "admin_app/portal/announcement_form.html", {"form": form, "announcement": ann})


@staff_required
@require_POST
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk)
    ann.delete()
    messages.success(request, "Announcement deleted.")
    return redirect("admin_app:admin_announcement_list")


# ----- Admin notifications (staff) -----
@staff_required
def admin_notification_list(request):
    """List notifications for current user (recipient) or sent by me; and create new."""
    # Notifications to me, or broadcast (recipient=None) for all staff
    from django.db.models import Q as DQ
    qs = AdminNotification.objects.filter(
        DQ(recipient=request.user) | DQ(recipient__isnull=True)
    ).select_related("created_by", "recipient").order_by("-created_at")
    unread_count = qs.filter(read_at__isnull=True).count()
    paginator = Paginator(qs, 30)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    staff_users = User.objects.filter(is_staff=True).order_by("username")
    return render(
        request,
        "admin_app/notifications/admin_notification_list.html",
        {"page_obj": page_obj, "unread_count": unread_count, "staff_users": staff_users},
    )


@staff_required
@require_POST
def admin_notification_mark_read(request, pk):
    notif = get_object_or_404(AdminNotification, pk=pk)
    # Only recipient can mark as read (for broadcast, recipient is None so any staff can mark — affects all; for per-user we check recipient)
    if notif.recipient and notif.recipient != request.user:
        return HttpResponse("Forbidden", status=403)
    notif.read_at = timezone.now()
    notif.save(update_fields=["read_at"])
    if request.headers.get("Accept", "").find("application/json") != -1:
        return JsonResponse({"ok": True})
    return redirect("admin_app:admin_notification_list")


@staff_required
def admin_notification_create(request):
    """Create a new admin notification (to a user or all staff)."""
    if request.method == "POST":
        recipient_id = request.POST.get("recipient", "").strip()
        title = request.POST.get("title", "").strip()
        message = request.POST.get("message", "").strip()
        link = request.POST.get("link", "").strip()
        link_label = request.POST.get("link_label", "").strip()
        if not title:
            messages.error(request, "Title is required.")
            return redirect("admin_app:admin_notification_list")
        recipient = None
        if recipient_id:
            recipient = get_object_or_404(User, pk=recipient_id, is_staff=True)
        notif = AdminNotification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            link=link,
            link_label=link_label or link,
            created_by=request.user,
        )
        messages.success(request, "Notification sent.")
        return redirect("admin_app:admin_notification_list")
    return redirect("admin_app:admin_notification_list")


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
        "admin_app/facility/facility_list.html",
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
    return render(request, "admin_app/facility/facility_form.html", {"form": form, "facility": None, "cancel_url": cancel_url})


@staff_required
def facility_detail(request, slug):
    """Modern facility card view showing all facility information."""
    facility = get_object_or_404(Facility, slug=slug)
    customers = facility.customers.all().order_by("name")
    racks = facility.racks.filter(is_active=True).order_by("name")
    network_devices = facility.network_devices.filter(is_active=True).order_by("rack", "rack_position", "name")
    ip_addresses = facility.ip_addresses.all().order_by("ip_address")
    documents = facility.documents.all().order_by("-uploaded_at")
    service_logs = facility.service_logs.all().select_related("service_type").prefetch_related("attachments").order_by("-performed_at")
    service_visits = facility.service_visits.all().select_related("service_log").order_by("scheduled_start")
    
    return render(
        request,
        "admin_app/facility/facility_card.html",
        {
            "facility": facility,
            "customers": customers,
            "racks": racks,
            "network_devices": network_devices,
            "ip_addresses": ip_addresses,
            "documents": documents,
            "service_logs": service_logs,
            "service_visits": service_visits,
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
    return render(request, "admin_app/facility/facility_form.html", {"form": form, "facility": facility, "cancel_url": cancel_url})


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
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.method == "POST":
        form = FacilityCustomersEditForm(request.POST, facility=facility)
        if form.is_valid():
            form.save(facility)
            messages.success(request, _("Customer access updated."))
            if in_modal or request.POST.get("modal") == "1":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect(detail_url)
    else:
        form = FacilityCustomersEditForm(facility=facility)
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else detail_url
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/facility_customers_edit_fragment.html", {
            "form": form,
            "facility": facility,
            "cancel_url": cancel_url,
            "in_modal": in_modal,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/facility_customers_edit.html", {
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
    return render(request, "admin_app/facility/facility_customer_add.html", {
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
    
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
    return_to_facility = request.GET.get("return_to") == "facility"
    if request.method == "POST":
        form = RackForm(request.POST, facility=facility)
        if form.is_valid():
            rack = form.save(commit=False)
            rack.facility = facility
            rack.save()
            messages.success(request, "Rack created.")
            if (in_modal or request.POST.get("modal") == "1") and request.POST.get("return_to") == "facility":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_rack_detail", facility_slug=facility.slug, rack_id=rack.pk)
    else:
        form = RackForm(facility=facility)
    
    facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if (in_modal and return_to_facility) else _get_cancel_url(request, facility_url)
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/rack_form_fragment.html", {
            "form": form,
            "facility": facility,
            "rack": None,
            "cancel_url": cancel_url,
            "return_to_facility": return_to_facility,
            "in_modal": in_modal,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/rack_form.html", {
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
    
    return render(request, "admin_app/facility/rack_detail.html", {
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
    
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
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
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/rack_form_fragment.html", {
            "form": form,
            "facility": facility,
            "rack": rack,
            "cancel_url": cancel_url,
            "return_to_facility": return_to_facility,
            "in_modal": in_modal,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/rack_form.html", {
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
    return render(request, "admin_app/facility/rack_seal_form.html", {
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
    return render(request, "admin_app/facility/rack_seal_remove_form.html", {
        "form": form,
        "facility": facility,
        "rack": rack,
        "seal": seal,
        "cancel_url": cancel_url,
    })


# ----- Devices (product types + instances) -----
@staff_required
def redirect_to_devices(request):
    """Redirect old /admin/network-devices/ to /admin/devices/."""
    return redirect("admin_app:admin_device_list")


@staff_required
def device_landing(request):
    """Landing page for device-related admin: types, categories, manufacturers, product datasheets."""
    from django.db.models import Count
    type_count = DeviceType.objects.filter(is_active=True).count()
    category_count = DeviceCategory.objects.count()
    manufacturer_count = Manufacturer.objects.count()
    datasheet_count = ProductDatasheet.objects.count()
    return render(request, "admin_app/device/device_landing.html", {
        "type_count": type_count,
        "category_count": category_count,
        "manufacturer_count": manufacturer_count,
        "datasheet_count": datasheet_count,
    })


@staff_required
def device_type_list(request):
    """List device types (products). Table: Name, Category, View. Add device (type) button on right."""
    qs = DeviceType.objects.filter(is_active=True).order_by("category", "name")
    search = (request.GET.get("q") or "").strip()
    category = request.GET.get("category") or ""
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(manufacturer__icontains=search)
            | Q(model__icontains=search)
            | Q(subcategory__icontains=search)
        )
    if category:
        qs = qs.filter(category=category)
    total_count = qs.count()
    paginator = Paginator(qs, 25)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    return render(request, "admin_app/device/device_type_list.html", {
        "page_obj": page_obj,
        "total_count": total_count,
        "search": search,
        "category": category,
        "category_choices": DeviceType.CATEGORY_CHOICES,
    })


@staff_required
def device_type_add(request):
    """Create a new device type (product)."""
    from .forms import DeviceTypeForm
    if request.method == "POST":
        form = DeviceTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _("Device type '%(name)s' created.") % {"name": form.instance.name})
            return redirect("admin_app:admin_device_type_detail", slug=form.instance.slug)
    else:
        form = DeviceTypeForm()
    return render(request, "admin_app/device/device_type_form.html", {
        "form": form,
        "device_type": None,
    })


@staff_required
def device_type_detail(request, slug):
    """View device type (product) and list its instances. Add instance button."""
    device_type = get_object_or_404(DeviceType, slug=slug)
    instances = device_type.instances.filter(is_active=True).select_related("facility", "rack").order_by("facility__name", "name")
    return render(request, "admin_app/device/device_type_detail.html", {
        "device_type": device_type,
        "instances": instances,
    })


@staff_required
def device_type_edit(request, slug):
    """Edit a device type (product)."""
    from .forms import DeviceTypeForm
    device_type = get_object_or_404(DeviceType, slug=slug)
    if request.method == "POST":
        form = DeviceTypeForm(request.POST, request.FILES, instance=device_type)
        if form.is_valid():
            form.save()
            messages.success(request, _("Device type updated."))
            return redirect("admin_app:admin_device_type_detail", slug=device_type.slug)
    else:
        form = DeviceTypeForm(instance=device_type)
    return render(request, "admin_app/device/device_type_form.html", {
        "form": form,
        "device_type": device_type,
    })


@staff_required
def device_instance_add(request, type_slug):
    """Add an instance (NetworkDevice) of this device type. Facility optional (can be 'Not assigned')."""
    from .forms import NetworkDeviceForm
    device_type = get_object_or_404(DeviceType, slug=type_slug)
    facilities = Facility.objects.filter(is_active=True).order_by("name")
    facility_slug = request.GET.get("facility") or (request.POST.get("facility") if request.method == "POST" else None)
    facility = None
    if facility_slug and facility_slug != "none":
        facility = get_object_or_404(Facility, slug=facility_slug)
    elif facility_slug == "none":
        facility = None  # Explicit: not assigned to any facility

    if request.method == "POST" and (facility is not None or request.POST.get("facility") == "none"):
        form = NetworkDeviceForm(request.POST, facility=facility)
        form.instance.product = device_type
        if facility is None:
            form.instance.facility = None
        if form.is_valid():
            form.save()
            messages.success(request, _("Device instance added."))
            in_modal = request.POST.get("in_modal") == "1"
            if in_modal and facility:
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_device_type_detail", slug=device_type.slug)
    elif request.method == "POST":
        form = NetworkDeviceForm(request.POST, facility=None)
        form.instance.product = device_type
        messages.error(request, _("Please select a facility or 'Not assigned'."))
    else:
        form = NetworkDeviceForm(facility=facility) if (facility is not None or facility_slug == "none") else None
        if form:
            form.instance.product = device_type

    if facility is None and facility_slug != "none" and not (request.method == "POST" and request.POST.get("facility") == "none"):
        return render(request, "admin_app/device/device_instance_add_choose_facility.html", {
            "device_type": device_type,
            "facilities": facilities,
        })
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/device/device_instance_form_fragment.html", {
            "form": form,
            "device_type": device_type,
            "facility": facility,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/device/device_instance_form.html", {
        "form": form,
        "device_type": device_type,
        "facility": facility,
    })


@staff_required
def device_instance_edit(request, type_slug, instance_pk):
    """Edit a device instance."""
    from .forms import NetworkDeviceForm
    device_type = get_object_or_404(DeviceType, slug=type_slug)
    instance = get_object_or_404(NetworkDevice, pk=instance_pk, product=device_type)
    facility = instance.facility
    if request.method == "POST":
        form = NetworkDeviceForm(request.POST, instance=instance, facility=facility)
        if form.is_valid():
            form.save()
            messages.success(request, _("Device instance updated."))
            return redirect("admin_app:admin_device_type_detail", slug=device_type.slug)
    else:
        form = NetworkDeviceForm(instance=instance, facility=facility)
    return render(request, "admin_app/device/device_instance_form.html", {
        "form": form,
        "device_type": device_type,
        "instance": instance,
        "facility": facility,
    })


@staff_required
@require_POST
def device_instance_delete(request, type_slug, instance_pk):
    """Delete (deactivate) a device instance."""
    device_type = get_object_or_404(DeviceType, slug=type_slug)
    instance = get_object_or_404(NetworkDevice, pk=instance_pk, product=device_type)
    name = instance.name
    instance.is_active = False
    instance.save()
    messages.success(request, _("Device instance '%(name)s' removed.") % {"name": name})
    return redirect("admin_app:admin_device_type_detail", slug=device_type.slug)


# ----- Device categories -----
@staff_required
def device_category_list(request):
    """List device categories (and subcategories)."""
    categories = DeviceCategory.objects.select_related("parent").order_by("parent__name", "name")
    return render(request, "admin_app/device/device_category_list.html", {"categories": categories})


@staff_required
def device_category_add(request):
    """Add a category or subcategory."""
    from .forms import DeviceCategoryForm
    if request.method == "POST":
        form = DeviceCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category '%(name)s' created.") % {"name": form.instance.name})
            return redirect("admin_app:admin_device_category_list")
    else:
        form = DeviceCategoryForm()
    return render(request, "admin_app/device/device_category_form.html", {"form": form, "category": None})


@staff_required
def device_category_edit(request, pk):
    """Edit a category."""
    from .forms import DeviceCategoryForm
    category = get_object_or_404(DeviceCategory, pk=pk)
    if request.method == "POST":
        form = DeviceCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category updated."))
            return redirect("admin_app:admin_device_category_list")
    else:
        form = DeviceCategoryForm(instance=category)
    return render(request, "admin_app/device/device_category_form.html", {"form": form, "category": category})


# ----- Manufacturers -----
@staff_required
def manufacturer_list(request):
    """List manufacturers."""
    manufacturers = Manufacturer.objects.order_by("name")
    return render(request, "admin_app/device/manufacturer_list.html", {"manufacturers": manufacturers})


@staff_required
def manufacturer_add(request):
    """Add a manufacturer."""
    from .forms import ManufacturerForm
    if request.method == "POST":
        form = ManufacturerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Manufacturer '%(name)s' created.") % {"name": form.instance.name})
            return redirect("admin_app:admin_manufacturer_list")
    else:
        form = ManufacturerForm()
    return render(request, "admin_app/device/manufacturer_form.html", {"form": form, "manufacturer": None})


@staff_required
def manufacturer_edit(request, pk):
    """Edit a manufacturer."""
    from .forms import ManufacturerForm
    manufacturer = get_object_or_404(Manufacturer, pk=pk)
    if request.method == "POST":
        form = ManufacturerForm(request.POST, instance=manufacturer)
        if form.is_valid():
            form.save()
            messages.success(request, _("Manufacturer updated."))
            return redirect("admin_app:admin_manufacturer_list")
    else:
        form = ManufacturerForm(instance=manufacturer)
    return render(request, "admin_app/device/manufacturer_form.html", {"form": form, "manufacturer": manufacturer})


# ----- Product datasheets -----
@staff_required
def product_datasheet_list(request):
    """List product datasheets (under Portal Management)."""
    datasheets = ProductDatasheet.objects.select_related("device_type", "uploaded_by").order_by("-updated_at")
    return render(request, "admin_app/device/product_datasheet_list.html", {"datasheets": datasheets})


@staff_required
def product_datasheet_create(request):
    """Create a product datasheet (Markdown and/or manufacturer PDF)."""
    from .forms import ProductDatasheetForm
    if request.method == "POST":
        form = ProductDatasheetForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.uploaded_by = request.user
            obj.save()
            messages.success(request, _("Datasheet '%(title)s' created.") % {"title": obj.title})
            return redirect("admin_app:admin_product_datasheet_list")
    else:
        form = ProductDatasheetForm()
    return render(request, "admin_app/device/product_datasheet_form.html", {"form": form, "is_edit": False})


@staff_required
def product_datasheet_edit(request, pk):
    """Edit a product datasheet."""
    from .forms import ProductDatasheetForm
    datasheet = get_object_or_404(ProductDatasheet, pk=pk)
    if request.method == "POST":
        form = ProductDatasheetForm(request.POST, request.FILES, instance=datasheet)
        if form.is_valid():
            form.save()
            messages.success(request, _("Datasheet '%(title)s' updated.") % {"title": datasheet.title})
            return redirect("admin_app:admin_product_datasheet_list")
    else:
        form = ProductDatasheetForm(instance=datasheet)
    return render(request, "admin_app/device/product_datasheet_form.html", {"form": form, "datasheet": datasheet, "is_edit": True})


@staff_required
@require_POST
def product_datasheet_delete(request, pk):
    """Delete a product datasheet."""
    datasheet = get_object_or_404(ProductDatasheet, pk=pk)
    title = datasheet.title
    datasheet.delete()
    messages.success(request, _("Datasheet '%(title)s' deleted.") % {"title": title})
    return redirect("admin_app:admin_product_datasheet_list")


@staff_required
def facility_device_choose_type(request, facility_slug):
    """From facility card: choose a device type, then add instance to this facility. Returns fragment when fragment=1."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    device_types = DeviceType.objects.filter(is_active=True).order_by("category", "name")
    if request.GET.get("fragment") != "1":
        return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    return render(request, "admin_app/facility/facility_device_choose_type_fragment.html", {
        "facility": facility,
        "device_types": device_types,
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
    
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
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
                if in_modal or request.POST.get("modal") == "1":
                    return redirect("admin_app:admin_rack_modal_close", facility_slug=facility.slug, rack_id=rack.pk)
                return redirect(rack_detail_url)
            else:
                facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
                if in_modal or request.POST.get("modal") == "1" or request.POST.get("return_to") == "facility":
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
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/device/network_device_form_fragment.html", {
            "form": form,
            "facility": facility,
            "rack": rack,
            "device": None,
            "cancel_url": cancel_url,
            "return_to_facility": return_to_facility,
            "in_modal": in_modal,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/device/network_device_form.html", {
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
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
    return_to_facility = request.GET.get("return_to") == "facility"
    rack_detail_url = reverse("admin_app:admin_rack_detail", kwargs={"facility_slug": facility.slug, "rack_id": device.rack.pk}) if device.rack else None
    facility_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.method == "POST":
        form = NetworkDeviceForm(request.POST, instance=device, facility=facility)
        if form.is_valid():
            form.save()
            messages.success(request, "Network device updated.")
            if device.rack:
                if in_modal or request.POST.get("modal") == "1":
                    return redirect("admin_app:admin_rack_modal_close", facility_slug=facility.slug, rack_id=device.rack.pk)
                return redirect(rack_detail_url)
            else:
                if in_modal or request.POST.get("return_to") == "facility" or request.POST.get("modal") == "1":
                    return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
                return redirect(facility_url)
    else:
        form = NetworkDeviceForm(instance=device, facility=facility)
    
    if device.rack:
        cancel_url = reverse("admin_app:admin_rack_modal_close", kwargs={"facility_slug": facility.slug, "rack_id": device.rack.pk}) if in_modal else (rack_detail_url + "#devices")
    else:
        cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if (in_modal and return_to_facility) else _get_cancel_url(request, facility_url)
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/device/network_device_form_fragment.html", {
            "form": form,
            "facility": facility,
            "rack": device.rack,
            "device": device,
            "cancel_url": cancel_url,
            "return_to_facility": return_to_facility,
            "in_modal": in_modal,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/device/network_device_form.html", {
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
def _ip_form_errors_html(form):
    """Return dict of field_name -> safe HTML for first error (or empty string). Avoids {% if %} in template."""
    out = {}
    for name in ("ip_address", "subnet", "reserved_for", "description", "device"):
        errors = form.errors.get(name)
        if errors:
            out[name] = mark_safe(f'<p class="form-error">{escape(str(errors[0]))}</p>')
        else:
            out[name] = mark_safe("")
    return out


@staff_required
def ip_address_add(request, facility_slug):
    """Add an IP address to a facility."""
    from .forms import IPAddressForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1" or request.POST.get("modal") == "1"
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
    delete_button_html = mark_safe("")  # Add form has no IP to delete
    page_title = _("Add IP Address")
    form_errors_html = _ip_form_errors_html(form)
    modal_hidden_field = mark_safe('<input type="hidden" name="modal" value="1">') if in_modal else mark_safe("")
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/ip_address_form_fragment.html", {
            "form": form,
            "facility": facility,
            "ip_address": None,
            "cancel_url": cancel_url,
            "in_modal": in_modal,
            "delete_button_html": delete_button_html,
            "page_title": page_title,
            "form_errors_html": form_errors_html,
            "modal_hidden_field": modal_hidden_field,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/ip_address_form.html", {
        "form": form,
        "facility": facility,
        "ip_address": None,
        "cancel_url": cancel_url,
        "in_modal": in_modal,
        "delete_button_html": delete_button_html,
        "page_title": page_title,
        "form_errors_html": form_errors_html,
        "modal_hidden_field": modal_hidden_field,
    })


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
    delete_url = reverse("admin_app:admin_ip_address_delete", kwargs={"facility_slug": facility.slug, "ip_id": ip_address.pk})
    delete_msg = escape(_("Are you sure you want to delete this IP address?"))
    delete_label = escape(_("Delete"))
    delete_button_html = mark_safe(f'<button type="button" class="form-btn form-btn-danger" data-delete-url="{delete_url}" data-delete-message="{delete_msg}">{delete_label}</button>')
    page_title = _("Edit IP Address")
    form_errors_html = _ip_form_errors_html(form)
    modal_hidden_field = mark_safe("")  # Edit form not used in facility modal
    return render(request, "admin_app/facility/ip_address_form.html", {
        "form": form,
        "facility": facility,
        "ip_address": ip_address,
        "cancel_url": cancel_url,
        "delete_button_html": delete_button_html,
        "page_title": page_title,
        "form_errors_html": form_errors_html,
        "modal_hidden_field": modal_hidden_field,
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
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    
    if request.method == "POST":
        form = FacilityDocumentForm(request.POST, request.FILES, facility=facility)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.facility = facility
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, _("Document '%(title)s' uploaded.") % {"title": doc.title})
            if in_modal or request.POST.get("modal") == "1":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = FacilityDocumentForm(facility=facility)
    
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else _get_cancel_url(request, detail_url)
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/facility_document_form_fragment.html", {
            "form": form,
            "facility": facility,
            "cancel_url": cancel_url,
            "in_modal": in_modal,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/facility_document_form.html", {
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


# ----- Facility Service Log / Servicerapport (full page, no modal) -----
@staff_required
def facility_service_log_add(request, facility_slug):
    """Add a new servicerapport (service report) – full page form."""
    from .forms import ServiceLogForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})

    if request.method == "POST":
        form = ServiceLogForm(request.POST, facility=facility)
        if form.is_valid():
            log = form.save(commit=False)
            log.facility = facility
            log.created_by = request.user
            log.save()
            messages.success(request, _("Servicerapport '%(id)s' opprettet. Du kan nå legge til enheter og vedlegg.") % {"id": log.service_id})
            return redirect("admin_app:admin_facility_service_log_edit", facility_slug=facility.slug, log_id=log.pk)
    else:
        form = ServiceLogForm(facility=facility)
        now = timezone.now()
        form.initial.setdefault("performed_at", now.strftime("%Y-%m-%dT%H:%M"))
        if facility.customers.exists():
            first_customer = facility.customers.first()
            form.initial.setdefault("customer_name", first_customer.name)
            form.initial.setdefault("customer_address", getattr(first_customer, "contact_info", "") or "")

    cancel_url = _get_cancel_url(request, detail_url)
    return render(request, "admin_app/facility/facility_servicerapport_form.html", {
        "form": form,
        "facility": facility,
        "service_log": None,
        "device_formset": None,
        "cancel_url": cancel_url,
    })


@staff_required
def facility_service_log_edit(request, facility_slug, log_id):
    """Edit a servicerapport – full page form with device formset."""
    from .forms import ServiceLogForm, ServiceLogDeviceForm
    from django.forms import inlineformset_factory

    facility = get_object_or_404(Facility, slug=facility_slug)
    service_log = get_object_or_404(ServiceLog, pk=log_id, facility=facility)
    detail_url = reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})

    ServiceLogDeviceFormSet = inlineformset_factory(
        ServiceLog,
        ServiceLogDevice,
        form=ServiceLogDeviceForm,
        extra=2,
        can_delete=True,
    )

    if request.method == "POST":
        form = ServiceLogForm(request.POST, instance=service_log, facility=facility)
        device_formset = ServiceLogDeviceFormSet(request.POST, instance=service_log)
        if form.is_valid() and device_formset.is_valid():
            form.save()
            device_formset.save()
            messages.success(request, _("Servicerapport '%(id)s' oppdatert.") % {"id": service_log.service_id})
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = ServiceLogForm(instance=service_log, facility=facility)
        device_formset = ServiceLogDeviceFormSet(instance=service_log)

    for f in device_formset.forms:
        if hasattr(f, "fields") and "device" in f.fields:
            f.fields["device"].queryset = NetworkDevice.objects.filter(facility=facility, is_active=True).order_by("name")

    cancel_url = _get_cancel_url(request, detail_url)
    return render(request, "admin_app/facility/facility_servicerapport_form.html", {
        "form": form,
        "facility": facility,
        "service_log": service_log,
        "device_formset": device_formset,
        "cancel_url": cancel_url,
    })


@staff_required
@require_POST
def facility_service_log_delete(request, facility_slug, log_id):
    """Delete a service log entry."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    service_log = get_object_or_404(ServiceLog, pk=log_id, facility=facility)
    service_id = service_log.service_id
    service_log.delete()
    messages.success(request, _("Service log '%(id)s' has been deleted.") % {"id": service_id})
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


@staff_required
def facility_service_log_attachment_upload(request, facility_slug, log_id):
    """Upload an attachment to a service log."""
    from .forms import ServiceLogAttachmentForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    service_log = get_object_or_404(ServiceLog, pk=log_id, facility=facility)
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"

    if request.method == "POST":
        form = ServiceLogAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            att = form.save(commit=False)
            att.service_log = service_log
            att.uploaded_by = request.user
            att.save()
            messages.success(request, _("Attachment added."))
            if in_modal or request.POST.get("modal") == "1":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
    else:
        form = ServiceLogAttachmentForm()

    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/facility_service_log_attachment_fragment.html", {
            "form": form,
            "facility": facility,
            "service_log": service_log,
            "cancel_url": cancel_url,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/facility_service_log_attachment_upload.html", {
        "form": form,
        "facility": facility,
        "service_log": service_log,
        "cancel_url": cancel_url,
    })


@staff_required
@require_POST
def facility_service_log_attachment_delete(request, facility_slug, log_id, attachment_id):
    """Delete a service log attachment."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    service_log = get_object_or_404(ServiceLog, pk=log_id, facility=facility)
    att = get_object_or_404(ServiceLogAttachment, pk=attachment_id, service_log=service_log)
    att.delete()
    messages.success(request, _("Attachment deleted."))
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


# ----- Service Types (admin) -----
@staff_required
def service_type_list(request):
    """List service types (categories for service logs)."""
    types = ServiceType.objects.all().order_by("sort_order", "name")
    return render(request, "admin_app/facility/service_type_list.html", {"service_types": types})


@staff_required
def service_type_add(request):
    from .forms import ServiceTypeForm
    if request.method == "POST":
        form = ServiceTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Service type added."))
            return redirect("admin_app:admin_service_type_list")
    else:
        form = ServiceTypeForm()
    return render(request, "admin_app/facility/service_type_form.html", {"form": form, "service_type": None})


@staff_required
def service_type_edit(request, pk):
    from .forms import ServiceTypeForm
    st = get_object_or_404(ServiceType, pk=pk)
    if request.method == "POST":
        form = ServiceTypeForm(request.POST, instance=st)
        if form.is_valid():
            form.save()
            messages.success(request, _("Service type updated."))
            return redirect("admin_app:admin_service_type_list")
    else:
        form = ServiceTypeForm(instance=st)
    return render(request, "admin_app/facility/service_type_form.html", {"form": form, "service_type": st})


# ----- Service Visits (planned visits / calendar) -----
@staff_required
def facility_service_visit_list(request, facility_slug):
    """List planned service visits for a facility."""
    facility = get_object_or_404(Facility, slug=facility_slug)
    visits = facility.service_visits.all().order_by("scheduled_start")
    return render(request, "admin_app/facility/facility_service_visit_list.html", {
        "facility": facility,
        "visits": visits,
    })


@staff_required
def facility_service_visit_add(request, facility_slug):
    from .forms import ServiceVisitForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
    if request.method == "POST":
        form = ServiceVisitForm(request.POST, facility=facility)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.facility = facility
            visit.created_by = request.user
            visit.save()
            messages.success(request, _("Service visit added."))
            if in_modal or request.POST.get("modal") == "1":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_facility_service_visit_list", facility_slug=facility.slug)
    else:
        form = ServiceVisitForm(facility=facility)
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/facility_service_visit_form_fragment.html", {
            "form": form,
            "facility": facility,
            "cancel_url": cancel_url,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/facility_service_visit_form.html", {
        "form": form,
        "facility": facility,
        "cancel_url": cancel_url,
    })


@staff_required
def facility_service_visit_edit(request, facility_slug, visit_id):
    from .forms import ServiceVisitForm
    facility = get_object_or_404(Facility, slug=facility_slug)
    visit = get_object_or_404(ServiceVisit, pk=visit_id, facility=facility)
    in_modal = request.GET.get("modal") == "1" or request.GET.get("fragment") == "1"
    if request.method == "POST":
        form = ServiceVisitForm(request.POST, instance=visit, facility=facility)
        if form.is_valid():
            form.save()
            messages.success(request, _("Service visit updated."))
            if in_modal or request.POST.get("modal") == "1":
                return redirect("admin_app:admin_facility_modal_close", facility_slug=facility.slug)
            return redirect("admin_app:admin_facility_service_visit_list", facility_slug=facility.slug)
    else:
        form = ServiceVisitForm(instance=visit, facility=facility)
    cancel_url = reverse("admin_app:admin_facility_modal_close", kwargs={"facility_slug": facility.slug}) if in_modal else reverse("admin_app:admin_facility_detail", kwargs={"slug": facility.slug})
    if request.GET.get("fragment") == "1":
        return render(request, "admin_app/facility/facility_service_visit_form_fragment.html", {
            "form": form,
            "facility": facility,
            "visit": visit,
            "cancel_url": cancel_url,
            "form_action": request.build_absolute_uri(request.path),
        })
    return render(request, "admin_app/facility/facility_service_visit_form.html", {
        "form": form,
        "facility": facility,
        "visit": visit,
        "cancel_url": cancel_url,
    })


@staff_required
@require_POST
def facility_service_visit_delete(request, facility_slug, visit_id):
    facility = get_object_or_404(Facility, slug=facility_slug)
    visit = get_object_or_404(ServiceVisit, pk=visit_id, facility=facility)
    visit.delete()
    messages.success(request, _("Service visit deleted."))
    return redirect("admin_app:admin_facility_detail", slug=facility.slug)


# ----- Service log export (PDF / Excel) -----
@staff_required
def facility_service_log_export(request, facility_slug):
    """Export service logs for a facility as Excel or PDF (date range optional)."""
    from io import BytesIO
    from django.utils.dateparse import parse_date

    facility = get_object_or_404(Facility, slug=facility_slug)
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()
    fmt = request.GET.get("format", "xlsx").strip().lower()
    if fmt not in ("xlsx", "pdf"):
        fmt = "xlsx"

    qs = facility.service_logs.all().order_by("-performed_at")
    if date_from:
        d = parse_date(date_from)
        if d:
            from django.utils import timezone
            qs = qs.filter(performed_at__date__gte=d)
    if date_to:
        d = parse_date(date_to)
        if d:
            from django.utils import timezone
            qs = qs.filter(performed_at__date__lte=d)

    if fmt == "xlsx":
        try:
            import openpyxl
        except ImportError:
            messages.error(request, _("Excel export requires openpyxl."))
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Servicelogg"
        headers = [
            _("Date"), _("Service ID"), _("Type"), _("Technician (employee no.)"),
            _("Description"), _("SLA deadline"), _("SLA met"), _("Approved"), _("External ID"),
        ]
        ws.append(headers)
        for log in qs:
            ws.append([
                log.performed_at.strftime("%Y-%m-%d %H:%M") if log.performed_at else "",
                log.service_id,
                log.service_type.name if log.service_type else "",
                log.technician_employee_no or "",
                (log.description or "")[:500],
                log.sla_deadline.strftime("%Y-%m-%d %H:%M") if log.sla_deadline else "",
                _("Yes") if log.sla_met is True else (_("No") if log.sla_met is False else ""),
                log.approved_at.strftime("%Y-%m-%d %H:%M") if log.approved_at else "",
                log.external_id or "",
            ])
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        filename = f"servicelogg-{facility.slug}-{timezone.now().strftime('%Y%m%d')}.xlsx"
        response = HttpResponse(buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    else:
        # PDF: simple table
        from xhtml2pdf import pisa
        from django.template.loader import render_to_string
        from django.utils import timezone
        html = render_to_string("admin_app/facility/facility_service_log_export_pdf.html", {
            "facility": facility,
            "logs": qs,
            "date_from": date_from,
            "date_to": date_to,
        })
        buf = BytesIO()
        pisa_status = pisa.CreatePDF(html.encode("utf-8"), dest=buf, encoding="utf-8")
        if pisa_status.err:
            messages.error(request, _("PDF generation failed."))
            return redirect("admin_app:admin_facility_detail", slug=facility.slug)
        buf.seek(0)
        filename = f"servicelogg-{facility.slug}-{timezone.now().strftime('%Y%m%d')}.pdf"
        response = HttpResponse(buf.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


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

    return render(request, "admin_app/backup/backup_restore.html")
