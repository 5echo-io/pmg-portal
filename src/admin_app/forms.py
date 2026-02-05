"""
Forms for custom admin (admin_app).
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group
from portal.models import Customer, CustomerMembership, PortalLink

User = get_user_model()


class RoleForm(forms.ModelForm):
    """Simple role (Group) form with name only to avoid 500 from Django's GroupForm (permissions M2M)."""
    class Meta:
        model = Group
        fields = ("name",)


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "is_staff", "is_active")


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "is_staff", "is_active", "is_superuser")


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "slug", "org_number", "contact_info", "primary_contact")
        widgets = {
            "contact_info": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "primary_contact" in self.fields:
            self.fields["primary_contact"].queryset = User.objects.all().order_by("username")


class CustomerMembershipForm(forms.ModelForm):
    class Meta:
        model = CustomerMembership
        fields = ("user", "customer", "role")


class PortalLinkForm(forms.ModelForm):
    class Meta:
        model = PortalLink
        fields = ("customer", "title", "url", "description", "sort_order")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }
