# Data migration: highest role -> owner, rest -> user (member->user, admin->owner)
# MAJOR: On update, users with highest previous role become Owner; others get User.

from django.db import migrations


def migrate_roles(apps, schema_editor):
    CustomerMembership = apps.get_model("portal", "CustomerMembership")
    CustomerMembership.objects.filter(role="member").update(role="user")
    CustomerMembership.objects.filter(role="admin").update(role="owner")


def reverse_migrate(apps, schema_editor):
    CustomerMembership = apps.get_model("portal", "CustomerMembership")
    CustomerMembership.objects.filter(role="user").update(role="member")
    CustomerMembership.objects.filter(role="owner").update(role="admin")


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0021_userprofile_and_tenant_roles"),
    ]

    operations = [
        migrations.RunPython(migrate_roles, reverse_migrate),
    ]
