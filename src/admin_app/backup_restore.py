"""
Full backup and restore for PMG Portal: database (PostgreSQL) + media files.
Produces a single .tar.gz that can be restored on a fresh server.
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

BACKUP_VERSION = "1"
MANIFEST_FILENAME = "manifest.json"
DATABASE_FILENAME = "database.sql"
MEDIA_ARCHIVE_DIR = "media"


def _get_db_config():
    db = settings.DATABASES["default"]
    if db.get("ENGINE") != "django.db.backends.postgresql":
        raise ValueError("Backup/Restore only supports PostgreSQL.")
    return {
        "host": db.get("HOST", "127.0.0.1"),
        "port": str(db.get("PORT", "5432")),
        "user": db.get("USER", ""),
        "password": db.get("PASSWORD", ""),
        "name": db.get("NAME", ""),
    }


def _run_pg_dump(sql_path: Path, db: dict) -> None:
    env = os.environ.copy()
    env["PGPASSWORD"] = db["password"]
    cmd = [
        "pg_dump",
        "--no-password",
        "-h", db["host"],
        "-p", db["port"],
        "-U", db["user"],
        "-d", db["name"],
        "--clean",
        "--if-exists",
        "-f", str(sql_path),
    ]
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        raise RuntimeError(
            "pg_dump not found. Install PostgreSQL client tools (e.g. postgresql-client) and ensure pg_dump is on PATH."
        )
    except subprocess.CalledProcessError as e:
        logger.exception("pg_dump failed: %s %s", e.stderr, e.stdout)
        raise RuntimeError(f"Database dump failed: {e.stderr or str(e)}")


def _run_psql(sql_path: Path, db: dict) -> None:
    env = os.environ.copy()
    env["PGPASSWORD"] = db["password"]
    cmd = [
        "psql",
        "--no-password",
        "-h", db["host"],
        "-p", db["port"],
        "-U", db["user"],
        "-d", db["name"],
        "-f", str(sql_path),
        "-v", "ON_ERROR_STOP=1",
    ]
    try:
        subprocess.run(cmd, env=env, check=True, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        raise RuntimeError(
            "psql not found. Install PostgreSQL client tools and ensure psql is on PATH."
        )
    except subprocess.CalledProcessError as e:
        logger.exception("psql restore failed: %s %s", e.stderr, e.stdout)
        raise RuntimeError(f"Database restore failed: {e.stderr or str(e)}")


def create_backup_archive() -> bytes:
    """Create full backup (database + media) as .tar.gz bytes. Uses temp file for large archives."""
    db = _get_db_config()
    media_root = Path(settings.MEDIA_ROOT)

    with tempfile.TemporaryDirectory(prefix="pmg_backup_") as tmpdir:
        root = Path(tmpdir)
        manifest = {
            "version": BACKUP_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "db_engine": "postgresql",
        }
        (root / MANIFEST_FILENAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        sql_path = root / DATABASE_FILENAME
        _run_pg_dump(sql_path, db)

        if media_root.exists():
            media_dest = root / MEDIA_ARCHIVE_DIR
            media_dest.mkdir(parents=True, exist_ok=True)
            for item in media_root.iterdir():
                dest = media_dest / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, symlinks=False)
                else:
                    shutil.copy2(item, dest)
        else:
            (root / MEDIA_ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as out:
            tmp_path = out.name
        try:
            with tarfile.open(tmp_path, mode="w:gz") as tar:
                for name in [MANIFEST_FILENAME, DATABASE_FILENAME, MEDIA_ARCHIVE_DIR]:
                    p = root / name
                    if p.exists():
                        tar.add(p, arcname=name)
            with open(tmp_path, "rb") as f:
                return f.read()
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def restore_from_archive(archive_path: Path) -> None:
    """
    Restore from a PMG backup .tar.gz: restore database then overwrite media with archive contents.
    """
    db = _get_db_config()
    media_root = Path(settings.MEDIA_ROOT)

    with tempfile.TemporaryDirectory(prefix="pmg_restore_") as tmpdir:
        root = Path(tmpdir)
        with tarfile.open(archive_path, mode="r:gz") as tar:
            tar.extractall(root)

        manifest_path = root / MANIFEST_FILENAME
        if not manifest_path.exists():
            raise ValueError("Invalid backup: missing manifest.json")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("version") != BACKUP_VERSION:
            raise ValueError(f"Unsupported backup version: {manifest.get('version')}. Expected {BACKUP_VERSION}.")
        if manifest.get("db_engine") != "postgresql":
            raise ValueError("This backup is for a different database engine.")

        sql_path = root / DATABASE_FILENAME
        if not sql_path.exists():
            raise ValueError("Invalid backup: missing database.sql")
        _run_psql(sql_path, db)

        media_src = root / MEDIA_ARCHIVE_DIR
        if media_src.exists():
            if media_root.exists():
                shutil.rmtree(media_root)
            media_root.mkdir(parents=True, exist_ok=True)
            for item in media_src.iterdir():
                dest = media_root / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, symlinks=False)
                else:
                    shutil.copy2(item, dest)
