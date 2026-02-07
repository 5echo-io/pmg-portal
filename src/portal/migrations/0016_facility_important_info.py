# Migration: Add important_info (viktig informasjon/kunngjøring) to Facility

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0015_facility_contact"),
    ]

    operations = [
        migrations.AddField(
            model_name="facility",
            name="important_info",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Viktig informasjon eller kunngjøring som vises på anleggskortet i portalen (f.eks. åpningstider, adkomst, nedetid).",
            ),
        ),
    ]
