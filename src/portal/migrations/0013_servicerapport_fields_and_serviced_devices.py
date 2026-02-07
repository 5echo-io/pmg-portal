# Migration: Servicerapport fields (asset, customer, supplier, bakgrunn, rapport, funn, konklusjon, anbefalinger) + ServiceLogDevice

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0012_servicelog_extensions"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicelog",
            name="asset_name",
            field=models.CharField(blank=True, default="", help_text="Asset/location name (e.g. WS06 NTK Studio)", max_length=200),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="asset_id",
            field=models.CharField(blank=True, default="", help_text="Asset ID (e.g. SDODMR0268)", max_length=100),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="contract_number",
            field=models.CharField(blank=True, default="", help_text="Avtalenummer", max_length=100),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="customer_name",
            field=models.CharField(blank=True, default="", help_text="Kunden (e.g. KS-Agenda AS / KS-Møteplasser AS)", max_length=300),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="customer_org_numbers",
            field=models.CharField(blank=True, default="", help_text="Customer org numbers (MVA)", max_length=200),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="customer_address",
            field=models.TextField(blank=True, default="", help_text="Customer address"),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="supplier_name",
            field=models.CharField(blank=True, default="", help_text="Leverandøren (e.g. Park Media Group AS)", max_length=200),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="supplier_org_number",
            field=models.CharField(blank=True, default="", help_text="Leverandør org number (MVA)", max_length=100),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="background",
            field=models.TextField(blank=True, default="", help_text="Bakgrunn"),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="summary",
            field=models.TextField(blank=True, default="", help_text="Oppsummering (short summary in Sammendrag)"),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="findings_observations",
            field=models.TextField(blank=True, default="", help_text="Funn og observasjoner"),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="conclusion",
            field=models.TextField(blank=True, default="", help_text="Konklusjon"),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="recommendations_immediate",
            field=models.TextField(blank=True, default="", help_text="Anbefalinger – umiddelbare tiltak"),
        ),
        migrations.AddField(
            model_name="servicelog",
            name="recommendations_long_term",
            field=models.TextField(blank=True, default="", help_text="Anbefalinger – langsiktige tiltak"),
        ),
        migrations.CreateModel(
            name="ServiceLogDevice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "serviced_at",
                    models.DateTimeField(blank=True, help_text="When this device was serviced (optional)", null=True),
                ),
                ("notes", models.TextField(blank=True, default="", help_text="Notes for this device in this service")),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="service_reports",
                        to="portal.networkdevice",
                    ),
                ),
                (
                    "service_log",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="serviced_devices",
                        to="portal.servicelog",
                    ),
                ),
            ],
            options={
                "ordering": ["serviced_at", "device__name"],
                "verbose_name": "Serviced device",
                "verbose_name_plural": "Serviced devices",
            },
        ),
        migrations.AddConstraint(
            model_name="servicelogdevice",
            constraint=models.UniqueConstraint(fields=("service_log", "device"), name="portal_servicelogdevice_unique_report_device"),
        ),
    ]
