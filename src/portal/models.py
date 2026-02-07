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
    logo = models.ImageField(upload_to="customer_logos/", blank=True, null=True, verbose_name="Logo (light mode)", help_text="Customer logo for light mode (and fallback)")
    logo_dark = models.ImageField(upload_to="customer_logos/", blank=True, null=True, verbose_name="Logo (dark mode)", help_text="Customer logo for dark mode (optional)")
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

    def logo_url_dark(self):
        """Return dark-mode logo URL if logo_dark exists. Same logic as logo_url."""
        if not self.logo_dark or not self.logo_dark.name:
            return None
        try:
            url = self.logo_dark.url
            try:
                if hasattr(self.logo_dark, "storage") and hasattr(self.logo_dark.storage, "exists"):
                    if self.logo_dark.storage.exists(self.logo_dark.name):
                        return url
                if hasattr(self.logo_dark, "path"):
                    import os
                    if os.path.exists(self.logo_dark.path):
                        return url
            except Exception:
                pass
            return url
        except Exception:
            try:
                return settings.MEDIA_URL + self.logo_dark.name
            except Exception:
                return None

    def delete(self, *args, **kwargs):
        """Override delete to remove logo files when customer is deleted."""
        logo_path = None
        logo_dark_path = None
        if self.logo:
            try:
                logo_path = self.logo.path
            except Exception:
                pass
        if self.logo_dark:
            try:
                logo_dark_path = self.logo_dark.path
            except Exception:
                pass

        super().delete(*args, **kwargs)

        for path in (logo_path, logo_dark_path):
            if path:
                try:
                    import os
                    if os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass


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
    Announcements posted by admins, visible to customer members.
    - facility is None: general announcement (shown on portal dashboard).
    - facility is set: announcement only shown when viewing that facility.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="announcements", db_index=True)
    facility = models.ForeignKey(
        "Facility",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="announcements",
        help_text="Optional: when set, announcement is only shown on this facility's page; when empty, shown on dashboard (general).",
    )
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
    important_info = models.TextField(
        blank=True,
        default="",
        help_text="Viktig informasjon eller kunngjøring som vises på anleggskortet i portalen (f.eks. åpningstider, adkomst, nedetid).",
    )
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


class ServiceType(models.Model):
    """
    Category for service log entries (e.g. planned service, troubleshooting, upgrade).
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=80, unique=True)
    sort_order = models.PositiveIntegerField(default=100, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Service type"
        verbose_name_plural = "Service types"

    def __str__(self) -> str:
        return self.name


class ServiceLog(models.Model):
    """
    Servicerapport: full service report document for a facility.
    Servicelogg is the overview list; each entry is a servicerapport (this model).
    Structure follows the standard servicerapport: Sammendrag (Bakgrunn, Oppsummering),
    Rapport, Funn og observasjoner, Konklusjon, Anbefalinger, Vedlegg, signaturer.
    """
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="service_logs")
    service_id = models.CharField(max_length=100, help_text="Service ID / reference number (e.g. RQ-2690)")
    service_type = models.ForeignKey(
        "ServiceType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_logs",
        help_text="Category: planned service, troubleshooting, upgrade, etc.",
    )
    performed_at = models.DateTimeField(help_text="When the service was performed")
    technician_employee_no = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Technician's employee number (ansattnummer)",
    )
    # --- Servicerapport header (from PDF page 1) ---
    asset_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Asset/location name (e.g. WS06 NTK Studio)",
    )
    asset_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Asset ID (e.g. SDODMR0268)",
    )
    contract_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Avtalenummer",
    )
    customer_name = models.CharField(
        max_length=300,
        blank=True,
        default="",
        help_text="Kunden (e.g. KS-Agenda AS / KS-Møteplasser AS)",
    )
    customer_org_numbers = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Customer org numbers (MVA)",
    )
    customer_address = models.TextField(
        blank=True,
        default="",
        help_text="Customer address",
    )
    supplier_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Leverandøren (e.g. Park Media Group AS)",
    )
    supplier_org_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Leverandør org number (MVA)",
    )
    # --- Sammendrag ---
    background = models.TextField(
        blank=True,
        default="",
        help_text="Bakgrunn",
    )
    summary = models.TextField(
        blank=True,
        default="",
        help_text="Oppsummering (short summary in Sammendrag)",
    )
    # --- Rapport (main work log) ---
    description = models.TextField(
        blank=True,
        default="",
        help_text="Rapport – documented description of what was performed",
    )
    # --- Funn og observasjoner ---
    findings_observations = models.TextField(
        blank=True,
        default="",
        help_text="Funn og observasjoner",
    )
    # --- Konklusjon ---
    conclusion = models.TextField(
        blank=True,
        default="",
        help_text="Konklusjon",
    )
    # --- Anbefalinger ---
    recommendations_immediate = models.TextField(
        blank=True,
        default="",
        help_text="Anbefalinger – umiddelbare tiltak",
    )
    recommendations_long_term = models.TextField(
        blank=True,
        default="",
        help_text="Anbefalinger – langsiktige tiltak",
    )
    notes = models.TextField(blank=True, default="", help_text="Additional notes")
    # SLA tracking (can be linked to ServiceDesk Plus or internal)
    external_id = models.CharField(
        max_length=100,
        blank=True,
        default="",
        db_index=True,
        help_text="External ticket ID (e.g. ServiceDesk Plus request ID) for linking.",
    )
    sla_deadline = models.DateTimeField(null=True, blank=True, help_text="SLA deadline for this service")
    sla_met = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether SLA was met (null = not evaluated)",
    )
    # Approval / signature (optional; full sign-request flow can extend this)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_service_logs",
    )
    signature_notes = models.CharField(max_length=200, blank=True, default="")
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
            models.Index(fields=["service_type", "-performed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.facility.name}: {self.service_id} ({self.performed_at.date()})"


class ServiceLogDevice(models.Model):
    """
    Links a network device to a service report – which devices were serviced in this report.
    Optionally when each device was serviced and notes per device.
    """
    service_log = models.ForeignKey(
        ServiceLog,
        on_delete=models.CASCADE,
        related_name="serviced_devices",
    )
    device = models.ForeignKey(
        "NetworkDevice",
        on_delete=models.CASCADE,
        related_name="service_reports",
    )
    serviced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this device was serviced (optional)",
    )
    notes = models.TextField(blank=True, default="", help_text="Notes for this device in this service")

    class Meta:
        ordering = ["serviced_at", "device__name"]
        unique_together = ("service_log", "device")
        verbose_name = "Serviced device"
        verbose_name_plural = "Serviced devices"

    def __str__(self) -> str:
        return f"{self.service_log.service_id} – {self.device.name}"


class ServiceLogAttachment(models.Model):
    """Attachment (image, PDF, etc.) for a service log entry."""
    service_log = models.ForeignKey(ServiceLog, on_delete=models.CASCADE, related_name="attachments")
    title = models.CharField(max_length=200, blank=True, default="")
    file = models.FileField(upload_to="service_log_attachments/%Y/%m/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_service_log_attachments",
    )

    class Meta:
        ordering = ["uploaded_at"]

    def __str__(self) -> str:
        return self.title or self.file.name


class ServiceLogSignatureRequest(models.Model):
    """
    Tracks a request for customer signature on a service log.
    Who can sign is configured per request; audit events record opening/signing.
    """
    service_log = models.ForeignKey(ServiceLog, on_delete=models.CASCADE, related_name="signature_requests")
    requested_at = models.DateTimeField(auto_now_add=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_service_log_signatures",
    )
    # Who can sign: comma-separated email or "customer_contact" etc.; or FK to CustomerMembership
    allowed_signer_emails = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated emails of people who may sign, or leave blank for customer admins",
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="signed_service_logs",
    )
    signed_document = models.FileField(
        upload_to="service_log_signed/%Y/%m/",
        blank=True,
        null=True,
        help_text="Generated document with signature (e.g. PDF) after signing",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("signed", "Signed"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        db_index=True,
    )

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self) -> str:
        return f"Signature request for {self.service_log.service_id} ({self.status})"


class ServiceLogAuditEvent(models.Model):
    """Audit log for service log document: opened, signature requested, signed, etc."""
    service_log = models.ForeignKey(ServiceLog, on_delete=models.CASCADE, related_name="audit_events")
    event_type = models.CharField(
        max_length=50,
        choices=[
            ("viewed", "Document viewed"),
            ("signature_requested", "Signature requested"),
            ("signature_sent", "Signature request sent"),
            ("signed", "Document signed"),
            ("downloaded", "Document downloaded"),
        ],
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_log_audit_events",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["service_log", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.service_log.service_id}: {self.event_type} at {self.created_at}"


class ServiceVisit(models.Model):
    """Planned service visit to a facility (for calendar and notifications)."""
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="service_visits")
    title = models.CharField(max_length=200)
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    service_log = models.ForeignKey(
        ServiceLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_visits",
        help_text="Link to service log after visit is completed",
    )
    notified_at = models.DateTimeField(null=True, blank=True, help_text="When notification was sent")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_service_visits",
    )

    class Meta:
        ordering = ["scheduled_start"]
        indexes = [
            models.Index(fields=["facility", "scheduled_start"]),
        ]
        verbose_name = "Service visit"
        verbose_name_plural = "Service visits"

    def __str__(self) -> str:
        return f"{self.facility.name}: {self.title} ({self.scheduled_start.date()})"


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


class FacilityContact(models.Model):
    """
    Contact person for a facility. Multiple contacts per facility with name, role, email, phone.
    """
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=200, help_text="Contact name")
    role = models.CharField(max_length=200, blank=True, default="", help_text="Role or title (e.g. Facility manager, IT contact)")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    is_primary = models.BooleanField(default=False, help_text="Mark as primary contact for this facility")
    sort_order = models.PositiveIntegerField(default=100, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Facility contact"
        verbose_name_plural = "Facility contacts"

    def __str__(self) -> str:
        return f"{self.facility.name}: {self.name}"


class TechnicalSupportContact(models.Model):
    """
    Global teknisk kontakt / nøkkelperson fra leverandørens side.
    Vises på anleggskortet slik at kunden vet hvem de skal kontakte ved teknisk support.
    """
    name = models.CharField(max_length=200, help_text="Navn på teknisk kontakt (f.eks. Support, NOC)")
    role = models.CharField(max_length=200, blank=True, default="", help_text="Rolle/tittel (f.eks. Teknisk support)")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    support_info = models.TextField(
        blank=True,
        default="",
        help_text="Ekstra informasjon (f.eks. åpningstider: Man–Fre 08–16, eller hvordan man åpner sak).",
    )
    sort_order = models.PositiveIntegerField(default=100, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "Technical support contact"
        verbose_name_plural = "Technical support contacts"

    def __str__(self) -> str:
        return self.name or "Technical support"


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


class DocumentTemplate(models.Model):
    """
    Master template for PDF documents (e.g. servicerapport, nettverksdokumentasjon).
    HTML + CSS are rendered with a context (e.g. service_log, facility) and converted to PDF via WeasyPrint.
    Use Django template variables in html_content, e.g. {{ service_log.service_id }}, {{ facility.name }}.
    """
    DOCUMENT_TYPE_SERVICERAPPORT = "servicerapport"
    DOCUMENT_TYPE_NETWORK = "nettverksdokumentasjon"
    DOCUMENT_TYPE_CHOICES = [
        (DOCUMENT_TYPE_SERVICERAPPORT, "Servicerapport"),
        (DOCUMENT_TYPE_NETWORK, "Nettverksdokumentasjon"),
    ]
    name = models.CharField(max_length=200, help_text="Template name (e.g. Standard servicerapport)")
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
        db_index=True,
        help_text="Type of document this template is used for",
    )
    html_content = models.TextField(
        blank=True,
        default="",
        help_text="Full HTML document. Use Django template variables, e.g. {{ service_log.description }}, {{ facility.name }}.",
    )
    css_content = models.TextField(
        blank=True,
        default="",
        help_text="CSS for print/PDF (e.g. @page, typography, margins). Used with WeasyPrint.",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Use this template when generating this document type (only one default per type).",
    )
    variables_help = models.TextField(
        blank=True,
        default="",
        help_text="Optional: list of available variable names for this document type (for reference when editing).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["document_type", "name"]
        verbose_name = "Document template"
        verbose_name_plural = "Document templates"

    def __str__(self) -> str:
        return f"{self.get_document_type_display()}: {self.name}"
