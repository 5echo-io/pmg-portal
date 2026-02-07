"""
Forms for custom admin (admin_app).
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group
from portal import roles as role_helpers
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
    FacilityContact,
    ServiceLog,
    ServiceLogAttachment,
    ServiceLogDevice,
    ServiceType,
    ServiceVisit,
)

User = get_user_model()


class RoleForm(forms.ModelForm):
    """Simple role (Group) form with name only to avoid 500 from Django's GroupForm (permissions M2M)."""
    class Meta:
        model = Group
        fields = ("name",)


class UserCreationForm(BaseUserCreationForm):
    """is_staff is derived from role (Administrator or higher); not shown."""
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "is_active")

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            role_helpers.sync_user_is_staff(instance)
        return instance


class UserEditForm(forms.ModelForm):
    """is_staff is derived from role (Administrator or higher); not shown."""
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "is_active", "is_superuser")

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._request = request
        # Only platform admin can change is_superuser (cannot grant platform admin as super admin)
        if request and not request.user.is_superuser:
            if "is_superuser" in self.fields:
                self.fields["is_superuser"].disabled = True
                self.fields["is_superuser"].help_text = _("Only platform administrators can change this.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Ensure non-platform-admins cannot set is_superuser
        if self._request and not self._request.user.is_superuser and hasattr(instance, "is_superuser"):
            instance.is_superuser = User.objects.filter(pk=instance.pk).values_list("is_superuser", flat=True).first() or False
        if commit:
            instance.save()
            role_helpers.sync_user_is_staff(instance)
        return instance


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "slug", "org_number", "contact_info", "logo", "logo_dark", "primary_contact")
        widgets = {
            "contact_info": forms.Textarea(attrs={"rows": 3}),
            "logo": forms.FileInput(attrs={"accept": "image/*"}),
            "logo_dark": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "slug" in self.fields:
            self.fields["slug"].label = _("Kundenummer")
        if "primary_contact" in self.fields:
            self.fields["primary_contact"].queryset = User.objects.all().order_by("username")
        for f in ("logo", "logo_dark"):
            if f in self.fields:
                self.fields[f].required = False


class CustomerMembershipForm(forms.ModelForm):
    class Meta:
        model = CustomerMembership
        fields = ("user", "customer", "role")

    def __init__(self, *args, request=None, customer=None, membership=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._request = request
        cust = customer or (membership.customer if membership else None)
        if request and "role" in self.fields:
            choices = role_helpers.get_assignable_tenant_roles(request.user, cust)
            if choices:
                self.fields["role"].choices = choices
            # If editing and current role not in assignable (e.g. owner when actor is administrator), keep current as option
            if membership and membership.role:
                current_choices = list(self.fields["role"].choices or [])
                if not any(c[0] == membership.role for c in current_choices):
                    label = getattr(membership, "get_role_display", lambda: membership.role)() if hasattr(membership, "get_role_display") else membership.role
                    self.fields["role"].choices = current_choices + [(membership.role, label)]


class PortalLinkForm(forms.ModelForm):
    class Meta:
        model = PortalLink
        fields = ("customer", "title", "url", "description", "sort_order")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ("customer", "facility", "title", "body", "is_pinned", "valid_from", "valid_until")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 6}),
            "valid_from": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "valid_until": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "customer" in self.fields:
            self.fields["customer"].queryset = Customer.objects.all().order_by("name")
            self.fields["customer"].required = False
            self.fields["customer"].help_text = _(
                "Påkrevd når anlegg er tom (dashboard). Valgfri når anlegg er valgt – meldingen vises da på anlegget for alle med tilgang."
            )
        if "facility" in self.fields:
            self.fields["facility"].queryset = Facility.objects.all().order_by("name")
            self.fields["facility"].required = False
            self.fields["facility"].help_text = _(
                "Velg anlegg: kunngjøringen vises på anleggssiden for alle med tilgang (kunde trengs ikke). La stå tom: kunngjøringen vises på dashboard for valgt kunde."
            )

    def clean(self):
        data = super().clean()
        facility = data.get("facility")
        customer = data.get("customer")
        if not facility and not customer:
            self.add_error(
                "customer",
                forms.ValidationError(_("Velg enten kunde (for dashboard) eller anlegg (for anleggssiden).")),
            )
        if facility and customer and not facility.customers.filter(pk=customer.pk).exists():
            self.add_error(
                "facility",
                forms.ValidationError(_("The selected facility does not have access for this customer.")),
            )
        return data


class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = (
            "name", "slug", "description", "address", "city", "postal_code", "country",
            "contact_person", "contact_email", "contact_phone",
            "important_info",
            "is_active", "status_label", "status_label_year", "customers"
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "important_info": forms.Textarea(attrs={"rows": 5, "placeholder": "F.eks. åpningstider, adkomst, nedetid eller andre kunngjøringer som vises på anleggssiden i portalen."}),
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


class DeviceTypeForm(forms.ModelForm):
    """Form for creating/editing a device type (product)."""
    class Meta:
        model = DeviceType
        fields = (
            "name", "slug", "category_fk", "subcategory_fk", "manufacturer_fk",
            "manufacturer", "model", "description", "product_image", "is_active"
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "product_image": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category_fk"].required = False
        self.fields["subcategory_fk"].required = False
        self.fields["manufacturer_fk"].required = False
        self.fields["manufacturer"].required = False
        if "subcategory_fk" in self.fields:
            self.fields["subcategory_fk"].queryset = DeviceCategory.objects.filter(parent__isnull=False).select_related("parent")


class DeviceCategoryForm(forms.ModelForm):
    class Meta:
        model = DeviceCategory
        fields = ("name", "slug", "parent")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].queryset = DeviceCategory.objects.filter(parent__isnull=True).order_by("name")
        self.fields["parent"].required = False


class ManufacturerForm(forms.ModelForm):
    class Meta:
        model = Manufacturer
        fields = ("name", "slug")


class ProductDatasheetForm(forms.ModelForm):
    class Meta:
        model = ProductDatasheet
        fields = ("title", "device_type", "file", "content_md")
        widgets = {
            "file": forms.FileInput(attrs={"accept": ".pdf,application/pdf"}),
            "content_md": forms.Textarea(attrs={"rows": 16, "class": "monospace", "placeholder": "## Specs\n| Parameter | Value |\n|----------|-------|\n| ... | ... |"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["device_type"].queryset = DeviceType.objects.filter(is_active=True).order_by("name")
        self.fields["device_type"].required = False
        self.fields["file"].required = False
        self.fields["content_md"].required = False

    def clean(self):
        data = super().clean()
        if not data.get("file") and not data.get("content_md") and not (self.instance and self.instance.pk and self.instance.file):
            raise forms.ValidationError(
                "Provide at least one: manufacturer PDF (file) or Markdown content."
            )
        return data


class NetworkDeviceForm(forms.ModelForm):
    class Meta:
        model = NetworkDevice
        fields = (
            "name", "device_type", "manufacturer", "model", "serial_number",
            "ip_address", "mac_address", "rack", "rack_position", "description", "is_active", "is_sla"
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.facility = kwargs.pop("facility", None)
        self.rack = kwargs.pop("rack", None)
        self.rack_position = kwargs.pop("rack_position", None)
        super().__init__(*args, **kwargs)
        
        if self.facility:
            self.instance.facility = self.facility
            if "rack" in self.fields:
                self.fields["rack"].queryset = Rack.objects.filter(facility=self.facility, is_active=True).order_by("name")
                self.fields["rack"].required = False
        else:
            if "rack" in self.fields:
                self.fields["rack"].queryset = Rack.objects.none()
                self.fields["rack"].widget = forms.HiddenInput()
        
        # Pre-select rack and position if provided
        if self.rack:
            self.instance.rack = self.rack
            if "rack" in self.fields:
                self.fields["rack"].initial = self.rack
        
        if self.rack_position:
            self.instance.rack_position = self.rack_position
            if "rack_position" in self.fields:
                self.fields["rack_position"].initial = self.rack_position


class FacilityCustomerAddForm(forms.Form):
    """Form to add a customer to a facility's access list."""
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.none(),
        label="Customer",
        required=True,
        empty_label="-- Select customer --",
    )

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility is not None:
            existing_ids = facility.customers.values_list("id", flat=True)
            self.fields["customer"].queryset = Customer.objects.exclude(id__in=existing_ids).order_by("name")


class FacilityCustomersEditForm(forms.Form):
    """Form to set which customers have access to a facility (checkboxes)."""
    customers = forms.ModelMultipleChoiceField(
        queryset=Customer.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility is not None:
            self.fields["customers"].queryset = Customer.objects.all().order_by("name")
            self.fields["customers"].initial = facility.customers.values_list("id", flat=True)

    def save(self, facility):
        facility.customers.set(self.cleaned_data["customers"])


class IPAddressForm(forms.ModelForm):
    class Meta:
        model = IPAddress
        fields = ("ip_address", "subnet", "reserved_for", "description", "device")
        widgets = {
            "description": forms.TextInput(attrs={"placeholder": "Optional"}),
            "reserved_for": forms.TextInput(attrs={"placeholder": "What this IP is reserved for"}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility:
            self.instance.facility = facility
            if "device" in self.fields:
                self.fields["device"].queryset = NetworkDevice.objects.filter(facility=facility).order_by("name")
                self.fields["device"].required = False


class FacilityDocumentForm(forms.ModelForm):
    class Meta:
        model = FacilityDocument
        fields = ("title", "description", "file", "category")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility:
            self.instance.facility = facility


class FacilityContactForm(forms.ModelForm):
    class Meta:
        model = FacilityContact
        fields = ("name", "role", "email", "phone", "is_primary", "sort_order")
        widgets = {
            "role": forms.TextInput(attrs={"placeholder": "e.g. Facility manager, IT contact"}),
            "sort_order": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility:
            self.instance.facility = facility


class ServiceLogForm(forms.ModelForm):
    """Full servicerapport form – all sections from the PDF template."""
    class Meta:
        model = ServiceLog
        fields = (
            # Identifikasjon
            "service_id",
            "service_type",
            "performed_at",
            "technician_employee_no",
            "external_id",
            # Header / omslag
            "asset_name",
            "asset_id",
            "contract_number",
            "customer_name",
            "customer_org_numbers",
            "customer_address",
            "supplier_name",
            "supplier_org_number",
            # Sammendrag
            "background",
            "summary",
            # Rapport
            "description",
            # Funn og observasjoner
            "findings_observations",
            # Konklusjon
            "conclusion",
            # Anbefalinger
            "recommendations_immediate",
            "recommendations_long_term",
            "notes",
            # SLA / signatur
            "sla_deadline",
            "sla_met",
            "approved_at",
            "approved_by",
            "signature_notes",
        )
        widgets = {
            "performed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "sla_deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "approved_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 8}),
            "background": forms.Textarea(attrs={"rows": 4}),
            "summary": forms.Textarea(attrs={"rows": 4}),
            "findings_observations": forms.Textarea(attrs={"rows": 5}),
            "conclusion": forms.Textarea(attrs={"rows": 4}),
            "recommendations_immediate": forms.Textarea(attrs={"rows": 3}),
            "recommendations_long_term": forms.Textarea(attrs={"rows": 3}),
            "customer_address": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility:
            self.instance.facility = facility
        self.fields["service_type"].queryset = ServiceType.objects.filter(is_active=True)
        self.fields["service_type"].required = False
        for name in ("performed_at", "sla_deadline", "approved_at"):
            if name in self.fields:
                self.fields[name].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
                self.fields[name].required = name == "performed_at"
        for name in ("sla_deadline", "approved_at", "approved_by"):
            if name in self.fields:
                self.fields[name].required = False
        if self.instance and self.instance.pk:
            from django.utils import timezone
            for field_name, attr in (
                ("performed_at", "performed_at"),
                ("sla_deadline", "sla_deadline"),
                ("approved_at", "approved_at"),
            ):
                val = getattr(self.instance, attr, None)
                if val:
                    if timezone.is_naive(val):
                        val = timezone.make_aware(val)
                    self.initial.setdefault(field_name, val.strftime("%Y-%m-%dT%H:%M"))


class ServiceLogDeviceForm(forms.ModelForm):
    class Meta:
        model = ServiceLogDevice
        fields = ("device", "serviced_at", "notes")
        widgets = {
            "serviced_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 1}),
        }

    def __init__(self, *args, service_log=None, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility:
            self.fields["device"].queryset = NetworkDevice.objects.filter(facility=facility, is_active=True).order_by("name")
        self.fields["serviced_at"].required = False
        self.fields["serviced_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]
        self.fields["notes"].required = False


class ServiceLogAttachmentForm(forms.ModelForm):
    class Meta:
        model = ServiceLogAttachment
        fields = ("title", "file")
        widgets = {"title": forms.TextInput(attrs={"placeholder": "Valgfri tittel"})}


class ServiceTypeForm(forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = ("name", "slug", "sort_order", "is_active")


class ServiceVisitForm(forms.ModelForm):
    class Meta:
        model = ServiceVisit
        fields = ("title", "scheduled_start", "scheduled_end", "description", "facility", "service_log")
        widgets = {
            "scheduled_start": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "scheduled_end": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, facility=None, **kwargs):
        super().__init__(*args, **kwargs)
        if facility:
            self.instance.facility = facility
            if "facility" in self.fields:
                self.fields["facility"].initial = facility
                self.fields["facility"].widget = forms.HiddenInput()
            self.fields["service_log"].queryset = ServiceLog.objects.filter(facility=facility).order_by("-performed_at")
        self.fields["scheduled_start"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]
        self.fields["scheduled_end"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"]
        self.fields["service_log"].required = False

