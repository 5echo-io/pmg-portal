"""
Forms for custom admin (admin_app).
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group
from portal.models import Customer, CustomerMembership, PortalLink, Facility

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
        fields = ("name", "slug", "org_number", "contact_info", "logo", "primary_contact")
        widgets = {
            "contact_info": forms.Textarea(attrs={"rows": 3}),
            "logo": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "primary_contact" in self.fields:
            self.fields["primary_contact"].queryset = User.objects.all().order_by("username")
        # Make logo field not required (allow clearing it)
        if "logo" in self.fields:
            self.fields["logo"].required = False


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


class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = (
            "name", "slug", "description", "address", "city", "postal_code", "country",
            "contact_person", "contact_email", "contact_phone", "is_active", "customers"
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "customers": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "customers" in self.fields:
            self.fields["customers"].queryset = Customer.objects.all().order_by("name")
            self.fields["customers"].required = False


