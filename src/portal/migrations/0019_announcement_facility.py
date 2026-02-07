# Migration: Announcement – optional facility for facility-scoped announcements

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0018_customer_logo_dark"),
    ]

    operations = [
        migrations.AddField(
            model_name="announcement",
            name="facility",
            field=models.ForeignKey(
                blank=True,
                help_text="Optional: when set, announcement is only shown on this facility's page; when empty, shown on dashboard (general).",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="announcements",
                to="portal.facility",
            ),
        ),
    ]
