# Migration: Rack serial_number and RackSeal model

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0004_facility_and_racks"),
    ]

    operations = [
        migrations.AddField(
            model_name="rack",
            name="serial_number",
            field=models.CharField(blank=True, default="", help_text="Rack serial number", max_length=100),
        ),
        migrations.CreateModel(
            name="RackSeal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("seal_id", models.CharField(help_text="Unique seal identifier/ID", max_length=100)),
                ("location_description", models.TextField(blank=True, default="", help_text="Description of where the seal is placed on the rack")),
                ("installed_at", models.DateTimeField(auto_now_add=True, help_text="When the seal was installed")),
                ("removed_at", models.DateTimeField(blank=True, help_text="When the seal was removed", null=True)),
                ("removal_reason", models.CharField(blank=True, choices=[("service", "Service/Maintenance"), ("replace", "Replace seal"), ("broken", "Already broken"), ("upgrade", "Upgrade/Modification"), ("other", "Other")], default="", help_text="Reason for removing the seal", max_length=50)),
                ("removal_notes", models.TextField(blank=True, default="", help_text="Additional notes about the removal")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("installed_by", models.ForeignKey(help_text="User who installed the seal", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="installed_seals", to=settings.AUTH_USER_MODEL)),
                ("rack", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seals", to="portal.rack")),
                ("removed_by", models.ForeignKey(blank=True, help_text="User who removed the seal", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="removed_seals", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-installed_at"],
            },
        ),
    ]
