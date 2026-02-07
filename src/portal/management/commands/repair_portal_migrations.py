"""
Repair out-of-sync migration state for portal app (e.g. 0021 marked applied but
portal_userprofile table missing, or 0021 fails with duplicate index).
Creates portal_userprofile if missing and marks 0021 applied so migrate can
continue with 0022–0026. Run before migrate in install/update scripts.
"""
from django.core.management.base import BaseCommand
from django.db import connection


# Schema matches portal/migrations/0021_userprofile_and_tenant_roles (CreateModel UserProfile)
USERPROFILE_TABLE = "portal_userprofile"
USERPROFILE_CREATE_SQL = f"""
CREATE TABLE IF NOT EXISTS {USERPROFILE_TABLE} (
    user_id integer NOT NULL PRIMARY KEY REFERENCES auth_user(id) ON DELETE CASCADE,
    system_role varchar(20) NOT NULL DEFAULT ''
);
"""
USERPROFILE_INDEX_SQL = f"""
CREATE INDEX IF NOT EXISTS portal_userprofile_system_role_idx ON {USERPROFILE_TABLE} (system_role);
"""
MIGRATION_0021_NAME = "0021_userprofile_and_tenant_roles"


class Command(BaseCommand):
    help = (
        "Repair portal migration state: create portal_userprofile if missing and mark 0021 applied. "
        "Run before migrate in install/update scripts."
    )

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if portal_userprofile exists
            cursor.execute(
                """
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = %s
                """,
                [USERPROFILE_TABLE],
            )
            if cursor.fetchone():
                if options.get("verbosity", 1) >= 2:
                    self.stdout.write(f"Table {USERPROFILE_TABLE} already exists, nothing to repair.")
                return

            self.stdout.write(
                self.style.WARNING(
                    f"Table {USERPROFILE_TABLE} missing (migration state out of sync). Creating table and marking 0021 applied."
                )
            )
            cursor.execute(USERPROFILE_CREATE_SQL)
            cursor.execute(USERPROFILE_INDEX_SQL)

            # Mark 0021 as applied so migrate skips it and runs 0022–0026
            cursor.execute(
                """
                INSERT INTO django_migrations (app, name, applied)
                SELECT 'portal', %s, NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM django_migrations WHERE app = 'portal' AND name = %s
                )
                """,
                [MIGRATION_0021_NAME, MIGRATION_0021_NAME],
            )
            if cursor.rowcount:
                self.stdout.write(self.style.SUCCESS(f"Marked portal.{MIGRATION_0021_NAME} as applied."))
        self.stdout.write(self.style.SUCCESS("Repair complete. Run migrate to apply remaining migrations."))
