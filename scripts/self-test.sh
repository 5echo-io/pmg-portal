#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/pmg-portal"
SRC_DIR="$APP_DIR/src"

echo "=== Self-test: pmg-portal ==="

set -a
source "$APP_DIR/.env"
set +a

sudo -E "$SRC_DIR/.venv/bin/python" - <<'PY'
import os, socket
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pmg_portal.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from portal.models import Customer  # noqa: E402

print("OK: Django loaded")
print("Users:", User.objects.count())
print("Customers:", Customer.objects.count())

host, port = os.getenv("APP_BIND","127.0.0.1:8000").split(":")
s = socket.socket()
try:
    s.settimeout(1.0)
    s.connect((host, int(port)))
    print(f"OK: App port reachable on {host}:{port}")
except Exception as e:
    print(f"WARNING: Could not reach {host}:{port} -> {e}")
finally:
    s.close()
PY

echo "Done."
