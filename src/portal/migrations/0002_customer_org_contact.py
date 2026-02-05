# Generated manually for Customer: org_number, contact_info, primary_contact

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="org_number",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
        migrations.AddField(
            model_name="customer",
            name="contact_info",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="customer",
            name="primary_contact",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="primary_contact_for_customers",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
