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
