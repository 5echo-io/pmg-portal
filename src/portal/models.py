"""
Customer portal foundation models.
"""
from django.conf import settings
from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    org_number = models.CharField(max_length=32, blank=True, default="")
    contact_info = models.TextField(blank=True, default="")
    logo = models.ImageField(upload_to="customer_logos/", blank=True, null=True, help_text="Customer logo displayed on dashboard")
    primary_contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_contact_for_customers",
    )

    def __str__(self) -> str:
        return self.name
    
    def logo_url(self):
        """Return logo URL if logo exists. Always returns URL if logo.name exists, even if file check fails."""
        if not self.logo or not self.logo.name:
            return None
        try:
            # Try to get URL from Django's storage system
            url = self.logo.url
            # Verify file exists if possible
            try:
                if hasattr(self.logo, 'storage') and hasattr(self.logo.storage, 'exists'):
                    if self.logo.storage.exists(self.logo.name):
                        return url
                # Fallback: check path directly
                if hasattr(self.logo, 'path'):
                    import os
                    if os.path.exists(self.logo.path):
                        return url
            except Exception:
                # If file check fails, still return URL (file might exist but check failed)
                pass
            # Return URL even if file existence check failed
            return url
        except Exception:
            # If URL generation fails, try manual construction
            try:
                from django.conf import settings
                return settings.MEDIA_URL + self.logo.name
            except Exception:
                return None
    
    def delete(self, *args, **kwargs):
        """Override delete to remove logo file and all related files when customer is deleted."""
        # Store logo path before deletion
        logo_path = None
        if self.logo:
            try:
                logo_path = self.logo.path
            except Exception:
                pass
        
        # Delete the customer (this will cascade delete CustomerMembership and PortalLink)
        super().delete(*args, **kwargs)
        
        # Delete logo file after model deletion
        if logo_path:
            try:
                import os
                if os.path.exists(logo_path):
                    os.remove(logo_path)
            except Exception:
                pass  # Silently fail if file deletion fails


class CustomerMembership(models.Model):
    ROLE_MEMBER = "member"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_MEMBER, "Member"),
        (ROLE_ADMIN, "Customer Admin"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_index=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER, db_index=True)

    class Meta:
        unique_together = ("user", "customer")
        indexes = [
            models.Index(fields=["user", "customer"]),  # Composite index for common query pattern
            models.Index(fields=["customer", "role"]),  # For filtering by customer and role
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.customer} ({self.role})"


class PortalLink(models.Model):
    """
    Simple links shown inside a customer's portal.
    Later you can extend this to sections/widgets/FDV status blocks, etc.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="links", db_index=True)
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.CharField(max_length=300, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=100, db_index=True)

    class Meta:
        ordering = ["sort_order", "title"]
        indexes = [
            models.Index(fields=["customer", "sort_order"]),  # Composite index for customer links ordering
        ]

    def __str__(self) -> str:
        return f"{self.customer}: {self.title}"


class Announcement(models.Model):
    """
    Announcements posted by admins, visible to all members of a customer.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="announcements", db_index=True)
    title = models.CharField(max_length=200)
    body = models.TextField(help_text="Plain text or HTML content")
    is_pinned = models.BooleanField(default=False, help_text="Pinned announcements appear first")
    valid_from = models.DateTimeField(null=True, blank=True, help_text="Optional: show only after this time")
    valid_until = models.DateTimeField(null=True, blank=True, help_text="Optional: hide after this time")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_announcements",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["customer", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.customer}: {self.title}"


class PortalUserPreference(models.Model):
    """
    Per-user (and optionally per-customer) preferences: theme, dashboard widgets.
    """
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    THEME_SYSTEM = "system"
    THEME_CHOICES = [
        (THEME_LIGHT, "Light"),
        (THEME_DARK, "Dark"),
        (THEME_SYSTEM, "System"),
    ]
    WIDGET_ANNOUNCEMENTS = "announcements"
    WIDGET_QUICK_STATS = "quick_stats"
    WIDGET_RECENT_LINKS = "recent_links"
    WIDGET_QUICK_LINKS = "quick_links"
    DEFAULT_WIDGETS = [WIDGET_ANNOUNCEMENTS, WIDGET_QUICK_STATS, WIDGET_RECENT_LINKS, WIDGET_QUICK_LINKS]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portal_preferences",
        db_index=True,
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="portal_preferences",
        help_text="If set, preferences apply when this customer is active; otherwise default for all.",
    )
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default=THEME_SYSTEM)
    dashboard_widgets = models.JSONField(
        default=list,
        blank=True,
        help_text="List of widget ids to show, e.g. ['announcements', 'quick_stats', 'recent_links', 'quick_links']. Empty = use defaults.",
    )

    class Meta:
        unique_together = [("user", "customer")]
        indexes = [
            models.Index(fields=["user", "customer"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} / {self.customer or 'default'}"


class Facility(models.Model):
    """
    Facility (Anlegg) - Physical locations/sites that customers can have access to.
    Facilities contain installations, management info, operations, maintenance, documentation, network, racks, IP addresses, etc.
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True, default="", help_text="Description of the facility")
    address = models.CharField(max_length=500, blank=True, default="", help_text="Physical address")
    city = models.CharField(max_length=100, blank=True, default="")
    postal_code = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, blank=True, default="Norway")
    contact_person = models.CharField(max_length=200, blank=True, default="", help_text="Primary contact person")
    contact_email = models.EmailField(blank=True, default="")
    contact_phone = models.CharField(max_length=50, blank=True, default="")
    is_active = models.BooleanField(default=True, help_text="Whether this facility is currently active")
    customers = models.ManyToManyField(Customer, related_name="facilities", blank=True, help_text="Customers that have access to this facility")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Facilities"

    def __str__(self) -> str:
        return self.name
    
    def get_customer_count(self):
        """Return the number of customers with access to this facility."""
        return self.customers.count()


class ServiceLog(models.Model):
    """
    Service log entry for a facility. Records when service was performed,
    by whom (technician employee number), and a documented description.
    """
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="service_logs")
    service_id = models.CharField(max_length=100, help_text="Service ID / reference number")
    performed_at = models.DateTimeField(help_text="When the service was performed")
    technician_employee_no = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Technician's employee number (ansattnummer)",
    )
    description = models.TextField(
        blank=True,
        default="",
        help_text="Documented description of what was performed",
    )
    notes = models.TextField(blank=True, default="", help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_service_logs",
    )

    class Meta:
        ordering = ["-performed_at"]
        verbose_name = "Service log"
        verbose_name_plural = "Service logs"
        indexes = [
            models.Index(fields=["facility", "-performed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.facility.name}: {self.service_id} ({self.performed_at.date()})"


class FacilityDocument(models.Model):
    """
    Documents uploaded to a facility (manuals, diagrams, certificates, etc.)
    """
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    file = models.FileField(upload_to="facility_documents/", help_text="Upload document file")
    category = models.CharField(
        max_length=50,
        choices=[
            ("manual", "Manual"),
            ("diagram", "Diagram"),
            ("certificate", "Certificate"),
            ("report", "Report"),
            ("other", "Other"),
        ],
        default="other",
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return f"{self.facility.name}: {self.title}"


class Rack(models.Model):
    """
    Rack within a facility for organizing equipment.
    """
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="racks")
    name = models.CharField(max_length=100, help_text="Rack name/number (e.g., 'Rack 01', 'A1')")
    location = models.CharField(max_length=200, blank=True, default="", help_text="Physical location within facility")
    description = models.TextField(blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True, default="", help_text="Rack serial number")
    height_units = models.PositiveIntegerField(default=42, help_text="Height in rack units (U)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["facility", "name"]
        unique_together = ("facility", "name")

    def __str__(self) -> str:
        return f"{self.facility.name} - {self.name}"
    
    def get_active_seals(self):
        """Return all active (not removed) seals for this rack."""
        return self.seals.filter(removed_at__isnull=True)
    
    def get_devices_by_position(self):
        """Return devices ordered by rack position."""
        return self.devices.filter(is_active=True).order_by("rack_position")


class Manufacturer(models.Model):
    """Manufacturer/brand for devices (selectable, not free text)."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class DeviceCategory(models.Model):
    """Category or subcategory for device types. parent=None = top-level category."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=80, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        ordering = ["parent__name", "name"]
        verbose_name_plural = "Device categories"

    def __str__(self) -> str:
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name


class DeviceType(models.Model):
    """
    Device product/template (e.g. a PC model, a gateway model). Defines the "product";
    actual physical units are NetworkDevice instances linked via product FK.
    """
    CATEGORY_NETWORK = "network"
    CATEGORY_SERVER_PC = "server_pc"
    CATEGORY_OTHER = "other"
    CATEGORY_CHOICES = [
        (CATEGORY_NETWORK, "Network"),
        (CATEGORY_SERVER_PC, "Server / PC"),
        (CATEGORY_OTHER, "Other"),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=120, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    subcategory = models.CharField(max_length=100, blank=True, default="")
    category_fk = models.ForeignKey(
        DeviceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_types",
        help_text="Category (optional; overrides legacy category if set).",
    )
    subcategory_fk = models.ForeignKey(
        DeviceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_types_sub",
        help_text="Subcategory (optional; must be child of category).",
    )
    manufacturer_fk = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="device_types",
        help_text="Manufacturer (optional; overrides legacy manufacturer if set).",
    )
    manufacturer = models.CharField(max_length=100, blank=True, default="")
    model = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    spec = models.JSONField(default=dict, blank=True, help_text="Type-specific specs: ports, PoE, components, etc.")
    product_image = models.ImageField(upload_to="device_type_images/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name

    def instance_count(self):
        return self.instances.filter(is_active=True).count()

    def get_manufacturer_display(self):
        if self.manufacturer_fk:
            return self.manufacturer_fk.name
        return self.manufacturer or ""

    def get_category_display_full(self):
        if self.category_fk:
            if self.subcategory_fk:
                return f"{self.category_fk.name} / {self.subcategory_fk.name}"
            return self.category_fk.name
        return self.get_category_display()


class ProductDatasheet(models.Model):
    """Product datasheet – Markdown content and/or manufacturer PDF, linked to a device type for /datasheet/<slug>/."""
    title = models.CharField(max_length=200, help_text="Product name for this datasheet")
    file = models.FileField(
        upload_to="product_datasheets/",
        help_text="Optional: PDF from manufacturer",
        blank=True,
        null=True,
    )
    content_md = models.TextField(
        blank=True,
        default="",
        help_text="Optional: Build the datasheet in Markdown (tables, headings, etc.). Shown at /datasheet/<product-slug>/.",
    )
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="datasheets",
        help_text="Link to device type. When set, datasheet is available at /datasheet/<device-type-slug>/.",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_datasheets",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title


class NetworkDevice(models.Model):
    """
    A physical device instance (serial number, placement). Can be linked to a DeviceType (product).
    Facility is optional (instance may not be assigned to an facility yet).
    """
    product = models.ForeignKey(
        DeviceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="instances",
        help_text="Device type/product this instance is of (optional).",
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="network_devices",
        null=True,
        blank=True,
        help_text="Facility this instance is installed at (optional if not yet deployed).",
    )
    rack = models.ForeignKey(Rack, on_delete=models.SET_NULL, null=True, blank=True, related_name="devices")
    is_sla = models.BooleanField(
        default=False,
        help_text="Part of Service Level Agreement / FDV (included in SLA reports).",
    )
    name = models.CharField(max_length=200)
    device_type = models.CharField(
        max_length=50,
        choices=[
            ("switch", "Switch"),
            ("router", "Router"),
            ("firewall", "Firewall"),
            ("access_point", "Access Point"),
            ("server", "Server"),
            ("other", "Other"),
        ],
        default="other",
    )
    manufacturer = models.CharField(max_length=100, blank=True, default="")
    model = models.CharField(max_length=100, blank=True, default="")
    serial_number = models.CharField(max_length=100, blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Primary IP address")
    mac_address = models.CharField(max_length=17, blank=True, default="", help_text="MAC address (format: XX:XX:XX:XX:XX:XX)")
    rack_position = models.PositiveIntegerField(null=True, blank=True, help_text="Position in rack (U)")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["facility", "rack", "rack_position", "name"]

    def __str__(self) -> str:
        if self.facility:
            return f"{self.facility.name} - {self.name}"
        return self.name


class IPAddress(models.Model):
    """
    Reserved IP addresses for a facility.
    """
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="ip_addresses")
    ip_address = models.GenericIPAddressField(unique=True)
    subnet = models.CharField(max_length=18, blank=True, default="", help_text="Subnet mask (e.g., /24)")
    description = models.CharField(max_length=200, blank=True, default="")
    reserved_for = models.CharField(max_length=200, blank=True, default="", help_text="What this IP is reserved for")
    device = models.ForeignKey(NetworkDevice, on_delete=models.SET_NULL, null=True, blank=True, related_name="ip_addresses")
    is_in_use = models.BooleanField(default=False)
    reserved_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["facility", "ip_address"]

    def __str__(self) -> str:
        return f"{self.facility.name} - {self.ip_address}"


class RackSeal(models.Model):
    """
    Security seals on racks to track access and tampering.
    """
    REMOVAL_REASONS = [
        ("service", "Service/Maintenance"),
        ("replace", "Replace seal"),
        ("broken", "Already broken"),
        ("upgrade", "Upgrade/Modification"),
        ("other", "Other"),
    ]
    
    rack = models.ForeignKey(Rack, on_delete=models.CASCADE, related_name="seals")
    seal_id = models.CharField(max_length=100, help_text="Unique seal identifier/ID")
    location_description = models.TextField(blank=True, default="", help_text="Description of where the seal is placed on the rack")
    installed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="installed_seals",
        help_text="User who installed the seal"
    )
    installed_at = models.DateTimeField(auto_now_add=True, help_text="When the seal was installed")
    removed_at = models.DateTimeField(null=True, blank=True, help_text="When the seal was removed")
    removed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="removed_seals",
        help_text="User who removed the seal"
    )
    removal_reason = models.CharField(
        max_length=50,
        choices=REMOVAL_REASONS,
        blank=True,
        default="",
        help_text="Reason for removing the seal"
    )
    removal_notes = models.TextField(blank=True, default="", help_text="Additional notes about the removal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-installed_at"]

    def __str__(self) -> str:
        return f"{self.rack} - Seal {self.seal_id}"
    
    @property
    def is_active(self):
        """Check if seal is currently active (not removed)."""
        return self.removed_at is None


class SystemInfo(models.Model):
    """
    Key-value store for app-wide system data (e.g. installed app version).
    Used for backwards-compatibility checks across upgrades/downgrades.
    """
    key = models.CharField(max_length=128, unique=True, db_index=True)
    value = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System info"
        verbose_name_plural = "System info"
        ordering = ["key"]

    def __str__(self) -> str:
        return f"{self.key}={self.value}"
