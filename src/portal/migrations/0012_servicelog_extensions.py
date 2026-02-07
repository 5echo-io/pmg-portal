# Migration: Service types, attachments, approval, SLA, signature request, audit, service visits

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_default_service_types(apps, schema_editor):
    ServiceType = apps.get_model("portal", "ServiceType")
    for name, slug, order in [
        ("Planlagt service", "planlagt-service", 10),
        ("Feilsøking", "feilsoking", 20),
        ("Oppgradering", "oppgradering", 30),
        ("Inspeksjon", "inspeksjon", 40),
        ("Annet", "annet", 100),
    ]:
        ServiceType.objects.get_or_create(slug=slug, defaults={"name": name, "sort_order": order})


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0011_servicelog"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=80, unique=True)),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=100)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["sort_order", "name"],
                "verbose_name": "Service type",
                "verbose_name_plural": "Service types",
            },
        ),
        migrations.AddField(
            model_name="servicelog",
            name="service_type",
            field=models.ForeignKey(
                blank=True,
                help_text="Category: planned service, troubleshooting, upgrade, etc.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="service_logs",
                to="portal.servicetype",
            ),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="external_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                default="",
                help_text="External ticket ID (e.g. ServiceDesk Plus request ID) for linking.",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="sla_deadline",
            field=models.DateTimeField(blank=True, help_text="SLA deadline for this service", null=True),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="sla_met",
            field=models.BooleanField(
                blank=True,
                help_text="Whether SLA was met (null = not evaluated)",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="approved_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="approved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="approved_service_logs",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="signature_notes",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddIndex(
            model_name="servicelog",
            index=models.Index(fields=["service_type", "-performed_at"], name="portal_servi_service_8c2e3a_idx"),
        ),
        migrations.RunPython(create_default_service_types, migrations.RunPython.noop),
        migrations.CreateModel(
            name="ServiceLogAttachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, default="", max_length=200)),
                ("file", models.FileField(upload_to="service_log_attachments/%Y/%m/")),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "service_log",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="portal.servicelog",
                    ),
                ),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_service_log_attachments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["uploaded_at"],
            },
        ),
        migrations.CreateModel(
            name="ServiceLogSignatureRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                (
                    "allowed_signer_emails",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Comma-separated emails of people who may sign, or leave blank for customer admins",
                    ),
                ),
                ("signed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "signed_document",
                    models.FileField(
                        blank=True,
                        help_text="Generated document with signature (e.g. PDF) after signing",
                        null=True,
                        upload_to="service_log_signed/%Y/%m/",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("signed", "Signed"),
                            ("expired", "Expired"),
                            ("cancelled", "Cancelled"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "requested_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="requested_service_log_signatures",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "signed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="signed_service_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "service_log",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="signature_requests",
                        to="portal.servicelog",
                    ),
                ),
            ],
            options={
                "ordering": ["-requested_at"],
            },
        ),
        migrations.CreateModel(
            name="ServiceLogAuditEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("viewed", "Document viewed"),
                            ("signature_requested", "Signature requested"),
                            ("signature_sent", "Signature request sent"),
                            ("signed", "Document signed"),
                            ("downloaded", "Document downloaded"),
                        ],
                        max_length=50,
                    ),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, default="", max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("extra", models.JSONField(blank=True, default=dict)),
                (
                    "service_log",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audit_events",
                        to="portal.servicelog",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="service_log_audit_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="servicelogauditevent",
            index=models.Index(fields=["service_log", "-created_at"], name="portal_servi_service_2d4f1b_idx"),
        ),
        migrations.CreateModel(
            name="ServiceVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("scheduled_start", models.DateTimeField()),
                ("scheduled_end", models.DateTimeField(blank=True, null=True)),
                ("description", models.TextField(blank=True, default="")),
                ("notified_at", models.DateTimeField(blank=True, null=True, help_text="When notification was sent")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_service_visits",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "facility",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_visits",
                        to="portal.facility",
                    ),
                ),
                (
                    "service_log",
                    models.ForeignKey(
                        blank=True,
                        help_text="Link to service log after visit is completed",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="scheduled_visits",
                        to="portal.servicelog",
                    ),
                ),
            ],
            options={
                "ordering": ["scheduled_start"],
                "verbose_name": "Service visit",
                "verbose_name_plural": "Service visits",
            },
        ),
        migrations.AddIndex(
            model_name="servicevisit",
            index=models.Index(fields=["facility", "scheduled_start"], name="portal_servi_facilit_9e1a2b_idx"),
        ),
    ]
