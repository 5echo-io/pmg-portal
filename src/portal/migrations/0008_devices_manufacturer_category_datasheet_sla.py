# Migration: Manufacturer, DeviceCategory, ProductDatasheet; DeviceType FKs + image; NetworkDevice facility nullable + is_sla

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0007_add_announcement_and_preferences"),
    ]

    operations = [
        migrations.CreateModel(
            name="Manufacturer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=120, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DeviceCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="portal.devicecategory")),
            ],
            options={
                "verbose_name_plural": "Device categories",
                "ordering": ["parent__name", "name"],
            },
        ),
        migrations.CreateModel(
            name="ProductDatasheet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("file", models.FileField(help_text="PDF or document file", upload_to="product_datasheets/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("device_type", models.ForeignKey(blank=True, help_text="Link to device type (optional).", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="datasheets", to="portal.devicetype")),
                ("uploaded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="uploaded_datasheets", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-uploaded_at"],
            },
        ),
        migrations.AddField(
            model_name="devicetype",
            name="category_fk",
            field=models.ForeignKey(blank=True, help_text="Category (optional; overrides legacy category if set).", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="device_types", to="portal.devicecategory"),
        ),
        migrations.AddField(
            model_name="devicetype",
            name="subcategory_fk",
            field=models.ForeignKey(blank=True, help_text="Subcategory (optional; must be child of category).", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="device_types_sub", to="portal.devicecategory"),
        ),
        migrations.AddField(
            model_name="devicetype",
            name="manufacturer_fk",
            field=models.ForeignKey(blank=True, help_text="Manufacturer (optional; overrides legacy manufacturer if set).", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="device_types", to="portal.manufacturer"),
        ),
        migrations.AddField(
            model_name="devicetype",
            name="product_image",
            field=models.ImageField(blank=True, null=True, upload_to="device_type_images/"),
        ),
        migrations.AddField(
            model_name="networkdevice",
            name="is_sla",
            field=models.BooleanField(default=False, help_text="Part of Service Level Agreement / FDV (included in SLA reports)."),
        ),
        migrations.AlterField(
            model_name="networkdevice",
            name="facility",
            field=models.ForeignKey(blank=True, help_text="Facility this instance is installed at (optional if not yet deployed).", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="network_devices", to="portal.facility"),
        ),
    ]
