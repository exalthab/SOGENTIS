# config/settings/environments/local.py

from decouple import config
from config.settings.modules.base import *  # Assure l'import des bases : BASE_DIR, etc.

# === DEBUG MODE ===
DEBUG = config("DEBUG", default=True, cast=bool)

# === ALLOWED HOSTS (local uniquement) ===
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# === EMAIL BACKEND (console) ===
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# === LOGGING (console only, verbose) ===
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

# === CORS (React/Vite local dev) ===
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# === CSRF ORIGINS (backend local) ===
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
