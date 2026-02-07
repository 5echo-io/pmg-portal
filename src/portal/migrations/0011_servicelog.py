# Migration: ServiceLog model for facility service log entries

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0010_product_datasheet_content_updated"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("service_id", models.CharField(help_text="Service ID / reference number", max_length=100)),
                ("performed_at", models.DateTimeField(help_text="When the service was performed")),
                (
                    "technician_employee_no",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Technician's employee number (ansattnummer)",
                        max_length=50,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Documented description of what was performed",
                    ),
                ),
                ("notes", models.TextField(blank=True, default="", help_text="Additional notes")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_service_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_logs",
                        to="portal.facility",
                    ),
                ),
            ],
            options={
                "ordering": ["-performed_at"],
                "verbose_name": "Service log",
                "verbose_name_plural": "Service logs",
            },
        ),
        migrations.AddIndex(
            model_name="servicelog",
            index=models.Index(fields=["facility", "-performed_at"], name="portal_servi_facilit_6a0b0d_idx"),
        ),
    ]
