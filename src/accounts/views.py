"""
Accounts views (login, logout, register).
"""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import translation

from .forms import LoginForm, RegisterForm, CustomPasswordChangeForm, AccountEditForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        
        # Set user's preferred language from session if available
        preferred_lang = request.session.get('user_preferred_language')
        if preferred_lang and preferred_lang in dict(settings.LANGUAGES):
            translation.activate(preferred_lang)
            request.session['django_language'] = preferred_lang
        else:
            # If no preferred language, check if there's a language in session from login page
            current_lang = request.session.get('django_language')
            if current_lang and current_lang in dict(settings.LANGUAGES):
                # Save it as preferred for future logins
                request.session['user_preferred_language'] = current_lang
        
        return redirect("/")

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
        return redirect("/")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("/")

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    """User profile settings page."""
    show_password_modal = False
    account_form = AccountEditForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user)
    
    if request.method == "POST":
        if "change_password" in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            show_password_modal = True
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully.")
                return redirect("/account/profile/")
            else:
                messages.error(request, "Please correct the errors below.")
        elif "update_account" in request.POST:
            account_form = AccountEditForm(request.POST, instance=request.user)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "Account information updated.")
                return redirect("/account/profile/")
            else:
                messages.error(request, "Please correct the errors below.")
        elif "delete_account" in request.POST:
            confirm_email = (request.POST.get("confirm_email") or "").strip()
            if confirm_email == (request.user.email or ""):
                user = request.user
                logout(request)
                user.delete()
                messages.success(request, "Your account has been permanently deleted.")
                return redirect("/account/login/")
            else:
                messages.error(request, "Email confirmation does not match. Account deletion cancelled.")
    
    return render(request, "accounts/profile.html", {
        "user": request.user,
        "password_form": password_form,
        "account_form": account_form,
        "show_password_modal": show_password_modal,
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
