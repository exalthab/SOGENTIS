import os
from decouple import config
from pathlib import Path

# BASE_DIR est défini par le context global dans settings_loader
try:
    BASE_DIR = Path(globals().get("BASE_DIR") or __file__).resolve().parent.parent.parent
except Exception:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

LOG_PATH = config("LOG_PATH", default=str(BASE_DIR / "logs/django_error.log"))

# Crée le dossier log si inexistant, et le fichier log s'il n'existe pas
log_dir = os.path.dirname(LOG_PATH)
try:
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'a'):
            os.utime(LOG_PATH, None)
except Exception as e:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(f"Erreur lors de la création du fichier de log : {e}")

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
