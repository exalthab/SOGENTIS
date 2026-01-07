# config/settings/modules/logging.py
from pathlib import Path
from decouple import config

# ============================================================
# 1) BASE_DIR
# ============================================================
BASE_DIR = Path(globals().get("BASE_DIR") or Path(__file__).resolve().parents[3]).resolve()

# ============================================================
# 2) Paths
# ============================================================
DJANGO_DEBUG = config("DEBUG", cast=bool, default=False)

LOG_DIR = Path(config("LOG_DIR", default=str(BASE_DIR / "logs"))).resolve()
LOG_PATH = Path(config("LOG_PATH", default=str(LOG_DIR / "django_error.log"))).resolve()
DEBUG_LOG_PATH = Path(config("DEBUG_LOG_PATH", default=str(LOG_DIR / "django_debug.log"))).resolve()

# ============================================================
# 3) Handlers dynamiques
#   - console toujours (journalctl)
#   - file_error toujours (mais delay=True)
#   - file_debug uniquement si DEBUG=True
# ============================================================
handlers = {
    "console": {
        "level": "DEBUG" if DJANGO_DEBUG else "INFO",
        "class": "logging.StreamHandler",
        "formatter": "simple",
    },
    "file_error": {
        "level": "ERROR",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(LOG_PATH),
        "maxBytes": 10 * 1024 * 1024,
        "backupCount": 10,
        "formatter": "verbose",
        "delay": True,
    },
}

if DJANGO_DEBUG:
    handlers["file_debug"] = {
        "level": "DEBUG",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": str(DEBUG_LOG_PATH),
        "maxBytes": 10 * 1024 * 1024,
        "backupCount": 5,
        "formatter": "verbose",
        "delay": True,
    }

django_handlers = ["console", "file_error"] + (["file_debug"] if DJANGO_DEBUG else [])
root_handlers = ["console", "file_error"] + (["file_debug"] if DJANGO_DEBUG else [])

# ============================================================
# 4) LOGGING
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}:{lineno} :: {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname}: {message}",
            "style": "{",
        },
    },

    "handlers": handlers,

    "loggers": {
        "django": {
            "handlers": django_handlers,
            "level": "DEBUG" if DJANGO_DEBUG else "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": django_handlers,
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"] if DJANGO_DEBUG else [],
            "level": "DEBUG",
            "propagate": False,
        },
    },

    "root": {
        "handlers": root_handlers,
        "level": "INFO" if DJANGO_DEBUG else "WARNING",
    },
}


# ============================================================
# 5) Recommandation: s’assurer que le dossier logs existe via deploy
# ============================================================
# IMPORTANT:
# - Ne pas créer de fichiers/dossiers ici (settings import-time)
# - Crée le dossier via provisioning (bash), systemd tmpfiles, ou Ansible
#
# Exemple (une fois sur VPS):
#   sudo mkdir -p /home/ubuntu/SOGENTIS/logs
#   sudo chown -R ubuntu:www-data /home/ubuntu/SOGENTIS/logs
#   sudo chmod 775 /home/ubuntu/SOGENTIS/logs







# # config/settings/modules/logging.py 05/01/2026

# import os
# from pathlib import Path
# from decouple import config
# from django.core.exceptions import ImproperlyConfigured


# # ============================================================
# # 🔍 1) Détection robuste de BASE_DIR
# # ============================================================
# try:
#     BASE_DIR = Path(globals().get("BASE_DIR") or __file__).resolve().parents[2]
# except Exception:
#     BASE_DIR = Path(__file__).resolve().parents[2]


# # ============================================================
# # 📁 2) Chemin du fichier de log (venant de .env)
# # ============================================================
# LOG_PATH = config(
#     "LOG_PATH",
#     default=str(BASE_DIR / "logs" / "django_error.log")
# )

# log_dir = os.path.dirname(LOG_PATH)


# # ============================================================
# # 🛠️ 3) Création du dossier et du fichier log
# # ============================================================
# try:
#     # Créer le dossier logs si besoin
#     if log_dir and not os.path.exists(log_dir):
#         os.makedirs(log_dir, exist_ok=True)

#     # Créer le fichier s'il n'existe pas
#     if not os.path.exists(LOG_PATH):
#         with open(LOG_PATH, "a"):
#             os.utime(LOG_PATH, None)

#     # Vérifier permissions
#     if not os.access(LOG_PATH, os.W_OK):
#         raise PermissionError(
#             f"❌ Le fichier log '{LOG_PATH}' n'est pas accessible en écriture."
#         )

# except Exception as e:
#     raise ImproperlyConfigured(f"⚠️ Erreur configuration logging : {e}")


# # ============================================================
# # 🖥️ 4) Affichage en mode DEBUG
# # ============================================================
# if config("DEBUG", cast=bool, default=False):
#     print(f"📄 Fichier de log utilisé : {LOG_PATH}")


# # ============================================================
# # 📝 5) Configuration complète LOGGING
# # ============================================================
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,

#     # ---------- 🧱 FORMATTERS ----------
#     "formatters": {
#         "verbose": {
#             "format": "{levelname} {asctime} {name} {module} :: {message}",
#             "style": "{",
#         },
#         "simple": {
#             "format": "{levelname}: {message}",
#             "style": "{",
#         }
#     },

#     # ---------- 🎯 HANDLERS ----------
#     "handlers": {
#         # Console (toujours actif en dev)
#         "console": {
#             "level": "INFO",
#             "class": "logging.StreamHandler",
#             "formatter": "simple",
#         },

#         # Fichier pour erreurs importantes
#         "file_error": {
#             "level": "ERROR",
#             "class": "logging.FileHandler",
#             "filename": LOG_PATH,
#             "formatter": "verbose",
#         },

#         # Fichier séparé pour logs de debug (facultatif)
#         "file_debug": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": str(BASE_DIR / "logs" / "django_debug.log"),
#             "formatter": "verbose",
#         },
#     },

#     # ---------- 📚 LOGGERS ----------
#     "loggers": {
#         "django": {
#             "handlers": ["console", "file_error"],
#             "level": "ERROR",     # erreurs majeures seulement
#             "propagate": True,
#         },

#         # Affiche les logs sql quand DEBUG=True
#         "django.db.backends": {
#             "handlers": ["console"] if config("DEBUG", cast=bool, default=False) else [],
#             "level": "DEBUG",
#         },
#     },

#     # ---------- 🌐 ROOT LOGGER ----------
#     "root": {
#         "handlers": ["console", "file_error"],
#         "level": "WARNING",  # par défaut : avertissements +
#     },
# }

