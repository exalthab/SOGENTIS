# config/settings/modules/logging.py

import os
from pathlib import Path
from decouple import config
from django.core.exceptions import ImproperlyConfigured


# ============================================================
# 🔍 1) Détection robuste de BASE_DIR
# ============================================================
try:
    BASE_DIR = Path(globals().get("BASE_DIR") or __file__).resolve().parents[2]
except Exception:
    BASE_DIR = Path(__file__).resolve().parents[2]


# ============================================================
# 📁 2) Chemin du fichier de log (venant de .env)
# ============================================================
LOG_PATH = config(
    "LOG_PATH",
    default=str(BASE_DIR / "logs" / "django_error.log")
)

log_dir = os.path.dirname(LOG_PATH)


# ============================================================
# 🛠️ 3) Création du dossier et du fichier log
# ============================================================
try:
    # Créer le dossier logs si besoin
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Créer le fichier s'il n'existe pas
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "a"):
            os.utime(LOG_PATH, None)

    # Vérifier permissions
    if not os.access(LOG_PATH, os.W_OK):
        raise PermissionError(
            f"❌ Le fichier log '{LOG_PATH}' n'est pas accessible en écriture."
        )

except Exception as e:
    raise ImproperlyConfigured(f"⚠️ Erreur configuration logging : {e}")


# ============================================================
# 🖥️ 4) Affichage en mode DEBUG
# ============================================================
if config("DEBUG", cast=bool, default=False):
    print(f"📄 Fichier de log utilisé : {LOG_PATH}")


# ============================================================
# 📝 5) Configuration complète LOGGING
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # ---------- 🧱 FORMATTERS ----------
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {module} :: {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname}: {message}",
            "style": "{",
        }
    },

    # ---------- 🎯 HANDLERS ----------
    "handlers": {
        # Console (toujours actif en dev)
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },

        # Fichier pour erreurs importantes
        "file_error": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": LOG_PATH,
            "formatter": "verbose",
        },

        # Fichier séparé pour logs de debug (facultatif)
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": str(BASE_DIR / "logs" / "django_debug.log"),
            "formatter": "verbose",
        },
    },

    # ---------- 📚 LOGGERS ----------
    "loggers": {
        "django": {
            "handlers": ["console", "file_error"],
            "level": "ERROR",     # erreurs majeures seulement
            "propagate": True,
        },

        # Affiche les logs sql quand DEBUG=True
        "django.db.backends": {
            "handlers": ["console"] if config("DEBUG", cast=bool, default=False) else [],
            "level": "DEBUG",
        },
    },

    # ---------- 🌐 ROOT LOGGER ----------
    "root": {
        "handlers": ["console", "file_error"],
        "level": "WARNING",  # par défaut : avertissements +
    },
}

