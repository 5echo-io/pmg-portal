"""
Accounts views (login, logout, register).
"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm, CustomPasswordChangeForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/portal/")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("/portal/")

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("/account/login/")


def register_view(request):
    if not settings.ENABLE_REGISTRATION:
        messages.info(request, "Registration is currently disabled.")
        return redirect("/account/login/")

    if request.user.is_authenticated:
        return redirect("/portal/")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("/portal/")

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    """User profile settings page."""
    return render(request, "accounts/profile.html", {
        "user": request.user,
    })


@login_required
def password_change_view(request):
    """Password change view."""
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect("/account/profile/")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, "accounts/password_change.html", {"form": form})
