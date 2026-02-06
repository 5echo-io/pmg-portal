# Migration: Facility, Rack, NetworkDevice, IPAddress, FacilityDocument models

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0003_customer_logo"),
    ]

    operations = [
        migrations.CreateModel(
            name="Facility",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True)),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("description", models.TextField(blank=True, default="", help_text="Description of the facility")),
                ("address", models.CharField(blank=True, default="", help_text="Physical address", max_length=500)),
                ("city", models.CharField(blank=True, default="", max_length=100)),
                ("postal_code", models.CharField(blank=True, default="", max_length=20)),
                ("country", models.CharField(blank=True, default="Norway", max_length=100)),
                ("contact_person", models.CharField(blank=True, default="", help_text="Primary contact person", max_length=200)),
                ("contact_email", models.EmailField(blank=True, default="")),
                ("contact_phone", models.CharField(blank=True, default="", max_length=50)),
                ("is_active", models.BooleanField(default=True, help_text="Whether this facility is currently active")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customers", models.ManyToManyField(blank=True, help_text="Customers that have access to this facility", related_name="facilities", to="portal.customer")),
            ],
            options={
                "ordering": ["name"],
                "verbose_name_plural": "Facilities",
            },
        ),
        migrations.CreateModel(
            name="Rack",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Rack name/number (e.g., 'Rack 01', 'A1')", max_length=100)),
                ("location", models.CharField(blank=True, default="", help_text="Physical location within facility", max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("height_units", models.PositiveIntegerField(default=42, help_text="Height in rack units (U)")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="racks", to="portal.facility")),
            ],
            options={
                "ordering": ["facility", "name"],
                "unique_together": {("facility", "name")},
            },
        ),
        migrations.CreateModel(
            name="NetworkDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("device_type", models.CharField(choices=[("switch", "Switch"), ("router", "Router"), ("firewall", "Firewall"), ("access_point", "Access Point"), ("server", "Server"), ("other", "Other")], default="other", max_length=50)),
                ("manufacturer", models.CharField(blank=True, default="", max_length=100)),
                ("model", models.CharField(blank=True, default="", max_length=100)),
                ("serial_number", models.CharField(blank=True, default="", max_length=100)),
                ("ip_address", models.GenericIPAddressField(blank=True, help_text="Primary IP address", null=True)),
                ("mac_address", models.CharField(blank=True, default="", help_text="MAC address (format: XX:XX:XX:XX:XX:XX)", max_length=17)),
                ("rack_position", models.PositiveIntegerField(blank=True, help_text="Position in rack (U)", null=True)),
                ("description", models.TextField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="network_devices", to="portal.facility")),
                ("rack", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="devices", to="portal.rack")),
            ],
            options={
                "ordering": ["facility", "rack", "rack_position", "name"],
            },
        ),
        migrations.CreateModel(
            name="IPAddress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ip_address", models.GenericIPAddressField(unique=True)),
                ("subnet", models.CharField(blank=True, default="", help_text="Subnet mask (e.g., /24)", max_length=18)),
                ("description", models.CharField(blank=True, default="", max_length=200)),
                ("reserved_for", models.CharField(blank=True, default="", help_text="What this IP is reserved for", max_length=200)),
                ("is_in_use", models.BooleanField(default=False)),
                ("reserved_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("device", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ip_addresses", to="portal.networkdevice")),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ip_addresses", to="portal.facility")),
            ],
            options={
                "ordering": ["facility", "ip_address"],
            },
        ),
        migrations.CreateModel(
            name="FacilityDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("file", models.FileField(help_text="Upload document file", upload_to="facility_documents/")),
                ("category", models.CharField(choices=[("manual", "Manual"), ("diagram", "Diagram"), ("certificate", "Certificate"), ("report", "Report"), ("other", "Other")], default="other", max_length=50)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="portal.facility")),
                ("uploaded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
    ]
