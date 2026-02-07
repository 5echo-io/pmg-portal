# Migration: Announcement and PortalUserPreference models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0006_device_type_and_product_fk"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Announcement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("body", models.TextField(help_text="Plain text or HTML content")),
                ("is_pinned", models.BooleanField(default=False, help_text="Pinned announcements appear first")),
                ("valid_from", models.DateTimeField(blank=True, null=True, help_text="Optional: show only after this time")),
                ("valid_until", models.DateTimeField(blank=True, null=True, help_text="Optional: hide after this time")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_announcements", to=settings.AUTH_USER_MODEL)),
                ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="announcements", to="portal.customer", db_index=True)),
            ],
            options={
                "ordering": ["-is_pinned", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="announcement",
            index=models.Index(fields=["customer", "-created_at"], name="portal_ann_cust_created_idx"),
        ),
        migrations.CreateModel(
            name="PortalUserPreference",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("theme", models.CharField(choices=[("light", "Light"), ("dark", "Dark"), ("system", "System")], default="system", max_length=20)),
                ("dashboard_widgets", models.JSONField(blank=True, default=list, help_text="List of widget ids to show. Empty = use defaults.")),
                ("customer", models.ForeignKey(blank=True, help_text="If set, preferences apply when this customer is active.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="portal_preferences", to="portal.customer")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="portal_preferences", to=settings.AUTH_USER_MODEL, db_index=True)),
            ],
            options={
                "unique_together": {("user", "customer")},
            },
        ),
        migrations.AddIndex(
            model_name="portaluserpreference",
            index=models.Index(fields=["user", "customer"], name="portal_pup_user_cust_idx"),
        ),
    ]
