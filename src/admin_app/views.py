"""
Custom admin views. Staff required; some actions require superuser.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import os

from portal.models import Customer, CustomerMembership, PortalLink, Facility

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
            messages.success(request, "Facility created.")
            return redirect("admin_app:admin_facility_detail", pk=facility.pk)
    else:
        form = FacilityForm()
    return render(request, "admin_app/facility_form.html", {"form": form, "facility": None})


@staff_required
def facility_detail(request, pk):
    """Modern facility card view showing all facility information."""
    facility = get_object_or_404(Facility, pk=pk)
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
def facility_edit(request, pk):
    from .forms import FacilityForm
    facility = get_object_or_404(Facility, pk=pk)
    if request.method == "POST":
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, "Facility updated.")
            return redirect("admin_app:admin_facility_detail", pk=facility.pk)
    else:
        form = FacilityForm(instance=facility)
    return render(request, "admin_app/facility_form.html", {"form": form, "facility": facility})


@staff_required
@require_POST
def facility_delete(request, pk):
    """Delete a facility and all related data."""
    facility = get_object_or_404(Facility, pk=pk)
    facility_name = facility.name
    
    # Delete facility (this will cascade delete related models)
    facility.delete()
    
    messages.success(request, f"Facility '{facility_name}' has been deleted.")
    return redirect("admin_app:admin_facility_list")
