"""
Simple auth forms.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(AuthenticationForm):
    """Login with email or username; field is labeled Email."""
    username = forms.CharField(
        label="Email",
        widget=forms.TextInput(attrs={"autocomplete": "email", "type": "email", "placeholder": "you@example.com"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean(self):
        login_value = (self.cleaned_data.get("username") or "").strip().lower()
        password = self.cleaned_data.get("password")
        if not login_value or not password:
            return self.cleaned_data
        user = User.objects.filter(email__iexact=login_value).first() or User.objects.filter(username__iexact=login_value).first()
        if user is None:
            raise forms.ValidationError("Please enter a correct email and password.")
        if not user.check_password(password):
            raise forms.ValidationError("Please enter a correct email and password.")
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.")
        self.cleaned_data["username"] = user.username
        self.user_cache = user
        return super().clean()

    def get_user(self):
        return getattr(self, "user_cache", None)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").strip()
        if email:
            cleaned["username"] = email[:150]
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.email:
            user.username = user.email[:150]
        if commit:
            user.save()
            self.save_m2m()
        return user

class AccountEditForm(forms.ModelForm):
    """Edit email, first_name, last_name only."""
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-input", "autocomplete": "email"}),
            "first_name": forms.TextInput(attrs={"class": "form-input", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "autocomplete": "family-name"}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "class": "form-input"}),
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-input"}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-input"}),
        label="Confirm New Password"
    )
