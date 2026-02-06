"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Django settings
Path: src/pmg_portal/settings.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value

SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-key")
DEBUG = env("DJANGO_DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "accounts",
    "portal",
    "web",
    "admin_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "portal.middleware.LanguagePreferenceMiddleware",  # Custom language preference (after AuthenticationMiddleware)
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Only enable debug logging middleware in DEBUG mode (performance optimization)
if DEBUG:
    MIDDLEWARE.append("pmg_portal.logging_middleware.DebugLoggingMiddleware")

ROOT_URLCONF = "pmg_portal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "pmg_portal" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "portal.context_processors.user_customers",
                "portal.context_processors.footer_info",
                "portal.context_processors.language_menu",
                "portal.context_processors.about_info",
            ],
        },
    },
]

WSGI_APPLICATION = "pmg_portal.wsgi.application"
ASGI_APPLICATION = "pmg_portal.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST", "127.0.0.1"),
        "PORT": env("POSTGRES_PORT", "5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Enable database query logging for debug view (only in DEBUG mode)
if DEBUG:
    LOGGING["loggers"]["django.db.backends"] = {
        "handlers": ["console"],
        "level": "DEBUG",
        "propagate": False,
    }

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("nb", "Norsk"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Europe/Oslo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media files (user uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR.parent / "media"

# WhiteNoise configuration for serving static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Caching configuration
# Use local memory cache (fast, per-process) for development and small deployments
# For larger deployments, consider Redis: django.core.cache.backends.redis.RedisCache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "pmg-portal-cache",
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
            "CULL_FREQUENCY": 3,  # Remove 1/3 of entries when MAX_ENTRIES is reached
        },
        "TIMEOUT": 300,  # Default cache timeout: 5 minutes
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "/account/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/account/login/"

ENABLE_REGISTRATION = env("ENABLE_REGISTRATION", "true").lower() == "true"

# Development Feature Flags
# Set ENABLE_DEV_FEATURES=true to enable development features (Facility management, etc.)
# Dev features are only accessible to superusers/admins
# Set DEV_ACCESS_USERS to comma-separated list of usernames/emails who can access dev features
# Example: DEV_ACCESS_USERS=admin@example.com,developer@example.com
# Leave empty to allow all superusers only
ENABLE_DEV_FEATURES = env("ENABLE_DEV_FEATURES", "false").lower() == "true"
DEV_ACCESS_USERS = [u.strip() for u in env("DEV_ACCESS_USERS", "").split(",") if u.strip()]

# Production-friendly defaults (keep simple)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# Logging configuration for debugging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO" if DEBUG else "WARNING",
            "propagate": False,
        },
        "portal": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "pmg_portal.debug": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "admin_app": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
