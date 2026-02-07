"""
Admin app models: admin-to-admin notifications.
"""
from django.conf import settings
from django.db import models


class AdminNotification(models.Model):
    """
    Notifications from one admin to another (or to all staff).
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_notifications",
        null=True,
        blank=True,
        help_text="Leave empty to notify all staff.",
    )
    title = models.CharField(max_length=200)
    message = models.TextField(blank=True, default="")
    link = models.URLField(blank=True, default="", help_text="Optional link for the notification")
    link_label = models.CharField(max_length=100, blank=True, default="")
    read_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_admin_notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "read_at"]),
        ]

    def __str__(self) -> str:
        to_whom = self.recipient.username if self.recipient else "All staff"
        return f"{self.title} → {to_whom}"
