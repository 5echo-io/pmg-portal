"""
Set the stored app version in the database to the current VERSION file.
Run after successful migrate (e.g. in update.sh / install.sh) so that
version compatibility checks know which version last ran.
"""
from django.core.management.base import BaseCommand

from pmg_portal.versioning import get_current_version, set_stored_version


class Command(BaseCommand):
    help = "Set stored app version from VERSION file (run after migrate for compatibility checks)."

    def handle(self, *args, **options):
        version = get_current_version()
        if not version:
            self.stderr.write(self.style.WARNING("VERSION file not found; storing empty version."))
        set_stored_version(version or "")
        self.stdout.write(self.style.SUCCESS(f"Stored app version: {version or '(empty)'}"))
