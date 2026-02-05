#!/usr/bin/env python3
"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Django management entrypoint
Path: src/manage.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmg_portal.settings")
    from django.core.management import execute_from_command_line  # noqa: WPS433

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
