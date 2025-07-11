import os

import dj_database_url
from decouple import config
from dotenv import load_dotenv

from ..modules.base import *

# Load .env file (typically at project root)
load_dotenv()

# Enable debug mode
DEBUG = True

# Allow local access
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Database configuration from DATABASE_URL
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"), engine="django.db.backends.postgresql"
    )
}

# Static files (CSS, JS, etc.)
STATIC_URL = "/static/"

# Media files (user uploads, etc.)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Local in-memory cache for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=1025)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='no-reply@example.com')

# Logging - print errors and debug info to console
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
        "level": "DEBUG",
    },
}
