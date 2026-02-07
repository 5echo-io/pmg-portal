# Migration: DocumentTemplate for master PDF templates (HTML + CSS, WeasyPrint)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0013_servicerapport_fields_and_serviced_devices"),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Template name (e.g. Standard servicerapport)", max_length=200)),
                (
                    "document_type",
                    models.CharField(
                        choices=[("servicerapport", "Servicerapport"), ("nettverksdokumentasjon", "Nettverksdokumentasjon")],
                        db_index=True,
                        help_text="Type of document this template is used for",
                        max_length=50,
                    ),
                ),
                (
                    "html_content",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Full HTML document. Use Django template variables, e.g. {{ service_log.description }}, {{ facility.name }}.",
                    ),
                ),
                (
                    "css_content",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="CSS for print/PDF (e.g. @page, typography, margins). Used with WeasyPrint.",
                    ),
                ),
                (
                    "is_default",
                    models.BooleanField(
                        default=False,
                        help_text="Use this template when generating this document type (only one default per type).",
                    ),
                ),
                (
                    "variables_help",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Optional: list of available variable names for this document type (for reference when editing).",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["document_type", "name"],
                "verbose_name": "Document template",
                "verbose_name_plural": "Document templates",
            },
        ),
    ]
