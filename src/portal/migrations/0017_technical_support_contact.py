# Migration: TechnicalSupportContact for global technical support / nøkkelperson

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0016_facility_important_info"),
    ]

    operations = [
        migrations.CreateModel(
            name="TechnicalSupportContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Navn på teknisk kontakt (f.eks. Support, NOC)", max_length=200)),
                ("role", models.CharField(blank=True, default="", help_text="Rolle/tittel (f.eks. Teknisk support)", max_length=200)),
                ("email", models.EmailField(blank=True, default="", max_length=254)),
                ("phone", models.CharField(blank=True, default="", max_length=50)),
                (
                    "support_info",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Ekstra informasjon (f.eks. åpningstider: Man–Fre 08–16, eller hvordan man åpner sak).",
                    ),
                ),
                ("sort_order", models.PositiveIntegerField(db_index=True, default=100)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["sort_order", "name"],
                "verbose_name": "Technical support contact",
                "verbose_name_plural": "Technical support contacts",
            },
        ),
    ]
