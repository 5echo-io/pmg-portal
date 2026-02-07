# Facility status labels and Facility.status_label

from django.db import migrations, models
import django.db.models.deletion


def create_default_status_labels(apps, schema_editor):
    FacilityStatusLabel = apps.get_model("portal", "FacilityStatusLabel")
    defaults = [
        ("01", "Under utbygging", "#94a3b8", 10),
        ("02", "Kontroll nødvendig", "#eab308", 20),
        ("03", "Periodisk kontroll utløpt", "#f97316", 30),
        ("04", "Kontroll ikke gyldig", "#dc2626", 40),
        ("05", "Anbefalt ikke bruk", "#b91c1c", 50),
        ("06", "Ute av drift", "#78716c", 60),
        ("07", "Service nødvendig", "#eab308", 70),
        ("08", "Kontrollert (årstall)", "#16a34a", 80),
        ("09", "Godkjent (årstall)", "#15803d", 90),
        ("10", "Ikke kontrollpliktig", "#0ea5e9", 100),
        ("11", "Demontert", "#64748b", 110),
    ]
    for code, name, color, order in defaults:
        FacilityStatusLabel.objects.get_or_create(code=code, defaults={"name": name, "color": color, "sort_order": order})


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0019_announcement_facility"),
    ]

    operations = [
        migrations.CreateModel(
            name="FacilityStatusLabel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(help_text="E.g. 01, 02", max_length=20, unique=True)),
                ("name", models.CharField(help_text="E.g. Under utbygging, Kontrollert (årstall)", max_length=120)),
                ("color", models.CharField(default="#16a34a", help_text="Hex color for status indicator, e.g. #16a34a", max_length=20)),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=100)),
            ],
            options={
                "ordering": ["sort_order", "code"],
                "verbose_name": "Facility status label",
                "verbose_name_plural": "Facility status labels",
            },
        ),
        migrations.AddField(
            model_name="facility",
            name="status_label",
            field=models.ForeignKey(
                blank=True,
                help_text="Status label (e.g. Kontrollert, Ute av drift). Overstyrer statusfarge i anleggsoversikten.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="facilities",
                to="portal.facilitystatuslabel",
            ),
        ),
        migrations.RunPython(create_default_status_labels, migrations.RunPython.noop),
    ]
