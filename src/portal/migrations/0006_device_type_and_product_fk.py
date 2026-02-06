# Migration: DeviceType model and NetworkDevice.product FK

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0005_rack_serial_and_seals"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeviceType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("category", models.CharField(
                    choices=[
                        ("network", "Network"),
                        ("server_pc", "Server / PC"),
                        ("other", "Other"),
                    ],
                    default="other",
                    max_length=30,
                )),
                ("subcategory", models.CharField(blank=True, default="", max_length=100)),
                ("manufacturer", models.CharField(blank=True, default="", max_length=100)),
                ("model", models.CharField(blank=True, default="", max_length=100)),
                ("description", models.TextField(blank=True, default="")),
                ("spec", models.JSONField(blank=True, default=dict, help_text="Type-specific specs: ports, PoE, components, etc.")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["category", "name"],
            },
        ),
        migrations.AddField(
            model_name="networkdevice",
            name="product",
            field=models.ForeignKey(
                blank=True,
                help_text="Device type/product this instance is of (optional).",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="instances",
                to="portal.devicetype",
            ),
        ),
    ]
