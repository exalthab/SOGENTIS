# config/settings/environments/dev.py

import os
from pathlib import Path

import dj_database_url
from decouple import config
from dotenv import load_dotenv

from config.settings.modules.base import *

# === Chargement des variables d'environnement depuis un fichier .env ===
load_dotenv()

# === Répertoire racine du projet ===
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# === Mode debug activé en développement ===
DEBUG = True

# === Hôtes autorisés ===
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# === Configuration de la base de données (par défaut PostgreSQL) ===
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default="postgres://user:pass@localhost:5432/dbname"),
        engine="django.db.backends.postgresql",
        conn_max_age=0,
    )
}

# === Fichiers statiques ===
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# === Fichiers média (uploads utilisateurs) ===
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === Cache mémoire local (pas Redis en dev) ===
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake-dev",
    }
}

# === Email : affichage en console (pas d’envoi réel) ===
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="localhost")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=1025)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@example.com")

# === Logging simple vers la console ===
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
