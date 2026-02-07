# Generated migration: UserProfile and extended CustomerMembership roles

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("portal", "0020_facility_status_label"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name="portal_profile", serialize=False, to=settings.AUTH_USER_MODEL)),
                ("system_role", models.CharField(blank=True, choices=[("", "—"), ("super_admin", "Super Admin")], db_index=True, default="", max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name="customermembership",
            name="role",
            field=models.CharField(
                choices=[
                    ("owner", "Owner"),
                    ("administrator", "Administrator"),
                    ("user", "User"),
                    ("member", "Member (legacy)"),
                    ("admin", "Customer Admin (legacy)"),
                ],
                db_index=True,
                default="user",
                max_length=20,
            ),
        ),
    ]
