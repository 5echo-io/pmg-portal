# Announcement.customer optional when facility is set

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0024_facility_status_label_year"),
    ]

    operations = [
        migrations.AlterField(
            model_name="announcement",
            name="customer",
            field=models.ForeignKey(
                blank=True,
                help_text="Required when facility is empty (dashboard announcement). Optional when facility is set (shown on facility for all with access).",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="announcements",
                to="portal.customer",
                db_index=True,
            ),
        ),
    ]
