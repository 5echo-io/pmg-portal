# Facility.status_label_year for year in labels 08/09 (Kontrollert/Godkjent)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0023_sync_is_staff_from_roles"),
    ]

    operations = [
        migrations.AddField(
            model_name="facility",
            name="status_label_year",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Årstall for statusetiketter som viser år (f.eks. Kontrollert/Godkjent). Brukes når status label er 08 eller 09.",
                null=True,
            ),
        ),
    ]
