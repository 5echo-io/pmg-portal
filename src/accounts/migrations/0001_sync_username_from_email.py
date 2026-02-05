# Generated migration: sync username from email so email can be used as primary login.
# Run once to set User.username = User.email for all users (where email fits in username field).

from django.db import migrations


def sync_username_from_email(apps, schema_editor):
    User = apps.get_model("auth", "User")
    for user in User.objects.all():
        if not user.email or len(user.email) > 150:
            continue
        if user.username != user.email:
            user.username = user.email
            user.save(update_fields=["username"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ("auth", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(sync_username_from_email, noop_reverse),
    ]
