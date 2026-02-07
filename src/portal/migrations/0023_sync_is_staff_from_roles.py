# Data migration: set is_staff from roles (Administrator or higher = staff)
# Run after 0022 so tenant roles are owner/administrator/user.

from django.db import migrations
from django.conf import settings


def sync_is_staff(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.rsplit(".", 1)
    User = apps.get_model(app_label, model_name)
    CustomerMembership = apps.get_model("portal", "CustomerMembership")
    UserProfile = apps.get_model("portal", "UserProfile")

    for user in User.objects.all():
        should_staff = user.is_superuser
        if not should_staff:
            if UserProfile.objects.filter(user=user, system_role="super_admin").exists():
                should_staff = True
        if not should_staff:
            if CustomerMembership.objects.filter(user=user, role__in=["owner", "administrator"]).exists():
                should_staff = True
        if user.is_staff != should_staff:
            user.is_staff = should_staff
            user.save(update_fields=["is_staff"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0022_migrate_member_admin_to_user_administrator"),
    ]

    operations = [
        migrations.RunPython(sync_is_staff, noop_reverse),
    ]
