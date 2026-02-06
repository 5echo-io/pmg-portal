"""
Forms for custom admin (admin_app).
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group
from portal.models import Customer, CustomerMembership, PortalLink, Facility, Rack, RackSeal

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
    
    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if slug:
            # Check if slug is already in use by another facility
            queryset = Facility.objects.filter(slug=slug)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("This slug is already in use. Please choose a different one.")
        return slug


class RackForm(forms.ModelForm):
    class Meta:
        model = Rack
        fields = ("name", "location", "description", "serial_number", "height_units", "is_active")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.facility = kwargs.pop("facility", None)
        super().__init__(*args, **kwargs)
        if self.facility:
            self.instance.facility = self.facility
    
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and self.facility:
            # Check if name is already in use by another rack in the same facility
            queryset = Rack.objects.filter(facility=self.facility, name=name)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("A rack with this name already exists in this facility.")
        return name


class RackSealForm(forms.ModelForm):
    class Meta:
        model = RackSeal
        fields = ("seal_id", "location_description")
        widgets = {
            "location_description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.rack = kwargs.pop("rack", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.rack:
            self.instance.rack = self.rack
        if self.user:
            self.instance.installed_by = self.user
    
    def clean_seal_id(self):
        seal_id = self.cleaned_data.get("seal_id")
        if seal_id and self.rack:
            # Check if an active (not removed) seal with this ID already exists on this rack
            queryset = RackSeal.objects.filter(rack=self.rack, seal_id=seal_id, removed_at__isnull=True)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("An active seal with this ID already exists on this rack.")
        return seal_id


class RackSealRemovalForm(forms.ModelForm):
    class Meta:
        model = RackSeal
        fields = ("removal_reason", "removal_notes")
        widgets = {
            "removal_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.instance.removed_by = self.user


