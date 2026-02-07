# Migration: FacilityContact for contact persons per facility

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0014_add_document_template"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacilityContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Contact name", max_length=200)),
                ("role", models.CharField(blank=True, default="", help_text="Role or title (e.g. Facility manager, IT contact)", max_length=200)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("phone", models.CharField(blank=True, default="", max_length=50)),
                ("is_primary", models.BooleanField(default=False, help_text="Mark as primary contact for this facility")),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=100)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("facility", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contacts", to="portal.facility")),
            ],
            options={
                "ordering": ["sort_order", "name"],
                "verbose_name": "Facility contact",
                "verbose_name_plural": "Facility contacts",
            },
        ),
    ]
