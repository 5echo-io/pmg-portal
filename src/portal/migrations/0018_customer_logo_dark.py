# Migration: Customer.logo_dark for dark-mode logo

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0017_technical_support_contact"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="logo_dark",
            field=models.ImageField(blank=True, help_text="Customer logo for dark mode (optional)", null=True, upload_to="customer_logos/"),
        ),
    ]
