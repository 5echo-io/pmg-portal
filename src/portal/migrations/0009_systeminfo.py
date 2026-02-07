# Migration: SystemInfo for storing app version (backwards compatibility)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0008_devices_manufacturer_category_datasheet_sla"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemInfo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(db_index=True, max_length=128, unique=True)),
                ("value", models.TextField(blank=True, default="")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "System info",
                "verbose_name_plural": "System info",
                "ordering": ["key"],
            },
        ),
    ]
