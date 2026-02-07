"""
Middleware that blocks requests if the app was downgraded (DB version > current code version).
Prevents starting with incompatible schema.
"""
from __future__ import annotations

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

# Cache result per process so we don't hit DB on every request
_compatibility_checked: bool | None = None
_compatibility_ok: bool = True
_compatibility_message: str | None = None


def _run_check() -> tuple[bool, str | None]:
    global _compatibility_checked, _compatibility_ok, _compatibility_message
    if _compatibility_checked is not None:
        return _compatibility_ok, _compatibility_message
    try:
        from pmg_portal.versioning import check_version_compatibility
        ok, msg = check_version_compatibility()
        _compatibility_checked = True
        _compatibility_ok = ok
        _compatibility_message = msg
        return ok, msg
    except Exception:
        _compatibility_checked = True
        _compatibility_ok = True
        _compatibility_message = None
        return True, None


class VersionCompatibilityMiddleware(MiddlewareMixin):
    """Block requests with 503 if database version is newer than current code (downgrade)."""

    def process_request(self, request):
        ok, message = _run_check()
        if ok:
            return None
        body = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Version mismatch</title></head><body>"
            "<h1>Version downgrade detected</h1><p>"
            + (message or "Database was used with a newer app version. See BACKWARDS_COMPATIBILITY.md.")
            + "</p><p>Run migrations backwards to match the current code version, then restart the service.</p>"
            "</body></html>"
        )
        return HttpResponse(body, status=503, content_type="text/html; charset=utf-8")
