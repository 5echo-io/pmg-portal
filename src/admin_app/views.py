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

from portal.models import Customer, CustomerMembership, PortalLink

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
def user_edit(request, pk):
    from .forms import UserEditForm
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated.")
            return redirect("admin_app:admin_user_list")
    else:
        form = UserEditForm(instance=user_obj)
    return render(request, "admin_app/user_form.html", {"form": form, "user_obj": user_obj})


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
    from django.contrib.auth.forms import GroupForm
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Role created.")
            return redirect("admin_app:admin_role_list")
    else:
        form = GroupForm()
    return render(request, "admin_app/role_form.html", {"form": form, "role": None})


@superuser_required
def role_edit(request, pk):
    from django.contrib.auth.forms import GroupForm
    role = get_object_or_404(Group, pk=pk)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Role updated.")
            return redirect("admin_app:admin_role_list")
    else:
        form = GroupForm(instance=role)
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
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer created.")
            return redirect("admin_app:admin_customer_list")
    else:
        form = CustomerForm()
    return render(request, "admin_app/customer_form.html", {"form": form, "customer": None})


@staff_required
def customer_edit(request, pk):
    from .forms import CustomerForm
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated.")
            return redirect("admin_app:admin_customer_list")
    else:
        form = CustomerForm(instance=customer)
    return render(request, "admin_app/customer_form.html", {"form": form, "customer": customer})


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
    if request.method == "POST":
        form = CustomerMembershipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Access added.")
            return redirect("admin_app:admin_customer_access_list")
    else:
        form = CustomerMembershipForm()
    return render(request, "admin_app/customer_access_form.html", {"form": form, "membership": None})


@staff_required
def customer_access_edit(request, pk):
    from .forms import CustomerMembershipForm
    membership = get_object_or_404(CustomerMembership, pk=pk)
    if request.method == "POST":
        form = CustomerMembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, "Access updated.")
            return redirect("admin_app:admin_customer_access_list")
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
    if request.method == "POST":
        form = PortalLinkForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Portal link created.")
            return redirect("admin_app:admin_portal_link_list")
    else:
        form = PortalLinkForm()
    return render(request, "admin_app/portal_link_form.html", {"form": form, "link": None})


@staff_required
def portal_link_edit(request, pk):
    from .forms import PortalLinkForm
    link = get_object_or_404(PortalLink, pk=pk)
    if request.method == "POST":
        form = PortalLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, "Portal link updated.")
            return redirect("admin_app:admin_portal_link_list")
    else:
        form = PortalLinkForm(instance=link)
    return render(request, "admin_app/portal_link_form.html", {"form": form, "link": link})
