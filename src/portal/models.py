"""
Customer portal foundation models.
"""
from django.conf import settings
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    def __str__(self) -> str:
        return self.name


class CustomerMembership(models.Model):
    ROLE_MEMBER = "member"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_MEMBER, "Member"),
        (ROLE_ADMIN, "Customer Admin"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    class Meta:
        unique_together = ("user", "customer")

    def __str__(self) -> str:
        return f"{self.user} -> {self.customer} ({self.role})"


class PortalLink(models.Model):
    """
    Simple links shown inside a customer's portal.
    Later you can extend this to sections/widgets/FDV status blocks, etc.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="links")
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.CharField(max_length=300, blank=True, default="")
    sort_order = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self) -> str:
        return f"{self.customer}: {self.title}"
