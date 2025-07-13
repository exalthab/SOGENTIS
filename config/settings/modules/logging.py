# config/settings/modules/logging.py

import os
from pathlib import Path
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# === BASE_DIR fallback ===
try:
    BASE_DIR = Path(globals().get("BASE_DIR") or __file__).resolve().parent.parent.parent
except Exception:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

# === Fichier de log défini dans .env ou par défaut
LOG_PATH = config("LOG_PATH", default=str(BASE_DIR / "logs/django_error.log"))
log_dir = os.path.dirname(LOG_PATH)

# === Crée le dossier de logs s’il n'existe pas
try:
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'a'):
            os.utime(LOG_PATH, None)
    if not os.access(LOG_PATH, os.W_OK):
        raise PermissionError(
            f"❌ Le fichier log '{LOG_PATH}' n’est pas accessible en écriture pour l’utilisateur courant."
        )
except Exception as e:
    raise ImproperlyConfigured(f"⚠️ Erreur lors de la configuration du fichier de log : {e}")

# ✅ Affichage utile uniquement si DEBUG est activé
if config("DEBUG", cast=bool, default=False):
    print(f"✅ Fichier de log utilisé : {LOG_PATH}")

# === LOGGING CONFIGURATION ===
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": LOG_PATH,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "ERROR",
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["file", "console"],
        "level": "WARNING",
    },
}
