# config/settings/settings_loader.py

import os
import sys
import logging
from pathlib import Path

from decouple import config
from django.core.exceptions import ImproperlyConfigured
from split_settings.tools import include

# ------------------------------------------------------------------
# Logging (sera configuré plus tard par logging.py)
# ------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# ✅ Base directory = dossier qui contient manage.py (le VRAI root)
# ------------------------------------------------------------------
def find_project_root(start: Path) -> Path:
    start = start.resolve()
    for p in [start] + list(start.parents):
        if (p / "manage.py").exists():
            return p
    # fallback (si manage.py introuvable)
    return start.parent.parent.parent

BASE_DIR = find_project_root(Path(__file__))

# # ------------------------------------------------------------------
# # Base directory
# # ------------------------------------------------------------------
# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent


# ------------------------------------------------------------------
# Ajout de sogentis_apps au PYTHONPATH (si nécessaire)
# ------------------------------------------------------------------
apps_path = BASE_DIR / "sogentis_apps"
if apps_path.exists() and str(apps_path) not in sys.path:
    sys.path.insert(0, str(apps_path))

# ------------------------------------------------------------------
# Détermination de l’environnement Django
# ------------------------------------------------------------------
def get_settings_environment() -> str:
    env = config("DJANGO_ENV", default="local").strip().lower()
    valid_envs = {
        "local": "local",
        "dev": "dev",
        "prod": "production",
        "production": "production",
        "test": "test",
    }

    if env not in valid_envs:
        raise ImproperlyConfigured(
            f"DJANGO_ENV='{env}' invalide. "
            f"Valeurs acceptées : {', '.join(sorted(valid_envs))}"
        )

    return valid_envs[env]


ENVIRONMENT = get_settings_environment()

logger.info("Django settings environment: %s", ENVIRONMENT.upper())

# ------------------------------------------------------------------
# Chargement modulaire des settings
# ------------------------------------------------------------------
include(
    # Base
    BASE_DIR / "config" / "settings" / "modules" / "base.py",
    BASE_DIR / "config" / "settings" / "modules" / "apps.py",

    # Core services
    BASE_DIR / "config" / "settings" / "modules" / "database.py",
    BASE_DIR / "config" / "settings" / "modules" / "email.py",
    BASE_DIR / "config" / "settings" / "modules" / "logging.py",
    BASE_DIR / "config" / "settings" / "modules" / "celery.py",

    # UI / content
    BASE_DIR / "config" / "settings" / "modules" / "ckeditor.py",
    BASE_DIR / "config" / "settings" / "modules" / "templates.py",
    BASE_DIR / "config" / "settings" / "modules" / "static.py",
    BASE_DIR / "config" / "settings" / "modules" / "internationalization.py",

    # Security & auth
    BASE_DIR / "config" / "settings" / "modules" / "middleware.py",
    BASE_DIR / "config" / "settings" / "modules" / "security.py",
    BASE_DIR / "config" / "settings" / "modules" / "authentication.py",
    BASE_DIR / "config" / "settings" / "modules" / "antispam.py",


    # Third-party
    BASE_DIR / "config" / "settings" / "modules" / "third_party.py",

    # Environment-specific overrides (LAST)
    BASE_DIR / "config" / "settings" / "environments" / f"{ENVIRONMENT}.py",
)






# # config/settings/settings_loader.py 10/01/2026
# import os
# import sys
# from pathlib import Path

# from decouple import config
# from django.core.exceptions import ImproperlyConfigured
# from split_settings.tools import include


# # ===========================================================
# # BASE DIR (robuste)
# # config/settings/settings_loader.py -> config/settings -> config -> project root
# # ===========================================================
# BASE_DIR = Path(__file__).resolve().parent.parent.parent


# # ===========================================================
# # Ajouter "sogentis_apps" au PYTHONPATH (sans doublon)
# # ===========================================================
# SOGENTIS_APPS_PATH = str(BASE_DIR / "sogentis_apps")
# if SOGENTIS_APPS_PATH not in sys.path:
#     sys.path.insert(0, SOGENTIS_APPS_PATH)


# # ===========================================================
# # Définir le module de configuration Django
# # (utile si import direct; en général géré par manage.py / wsgi.py)
# # ===========================================================
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")


# # ===========================================================
# # Déterminer l’environnement actif via DJANGO_ENV
# # ===========================================================
# def get_settings_module() -> str:
#     env = (config("DJANGO_ENV", default="local") or "local").strip().lower()
#     mapping = {
#         "local": "local",
#         "dev": "dev",
#         "prod": "production",
#         "production": "production",
#         "test": "test",
#     }
#     if env not in mapping:
#         raise ImproperlyConfigured(
#             f"❌ DJANGO_ENV='{env}' invalide. Valeurs acceptées : {', '.join(sorted(mapping.keys()))}"
#         )
#     return mapping[env]


# ENVIRONMENT = get_settings_module()



# # ===========================================================
# # Log optionnel (désactivé par défaut en prod)
# # ===========================================================
# if config("SETTINGS_LOADER_LOG", cast=bool, default=False):
#     # pas de print par défaut : activable via env
#     sys.stderr.write(f"✅ Django settings loader: ENV={ENVIRONMENT}\n")


# # ===========================================================
# # Chargement modulaire (ordre cohérent)
# # ===========================================================
# include(
#     BASE_DIR / "config" / "settings" / "modules" / "base.py",
#     BASE_DIR / "config" / "settings" / "modules" / "apps.py",
#     BASE_DIR / "config" / "settings" / "modules" / "database.py",
#     BASE_DIR / "config" / "settings" / "modules" / "email.py",
#     BASE_DIR / "config" / "settings" / "modules" / "logging.py",
#     BASE_DIR / "config" / "settings" / "modules" / "celery.py",
#     BASE_DIR / "config" / "settings" / "modules" / "ckeditor.py",
#     BASE_DIR / "config" / "settings" / "modules" / "middleware.py",
#     BASE_DIR / "config" / "settings" / "modules" / "static.py",
#     BASE_DIR / "config" / "settings" / "modules" / "security.py",
#     BASE_DIR / "config" / "settings" / "modules" / "templates.py",
#     BASE_DIR / "config" / "settings" / "modules" / "internationalization.py",
#     BASE_DIR / "config" / "settings" / "modules" / "third_party.py",
#     BASE_DIR / "config" / "settings" / "modules" / "authentication.py",
#     BASE_DIR / "config" / "settings" / "environments" / f"{ENVIRONMENT}.py",
# )





# # config/settings/settings_loader.py 09/01/2026

# import os
# import sys
# from pathlib import Path
# from decouple import config
# from django.core.exceptions import ImproperlyConfigured
# from split_settings.tools import include

# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# # Ajouter "sogentis_apps" au PYTHONPATH
# sys.path.insert(0, str(BASE_DIR / "sogentis_apps"))

# # Définir le module de configuration Django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

# # Déterminer l’environnement actif via DJANGO_ENV
# def get_settings_module() -> str:
#     env = config("DJANGO_ENV", default="local").strip().lower()
#     valid_envs = {
#         "local": "local",
#         "dev": "dev",
#         "prod": "production",
#         "test": "test",
#     }
#     if env not in valid_envs:
#         raise ImproperlyConfigured(
#             f"❌ DJANGO_ENV='{env}' invalide. Valeurs acceptées : {', '.join(valid_envs)}"
#         )
#     return valid_envs[env]

# ENVIRONMENT = get_settings_module()

# # ✅ Log utile pour VPS / CI / Shell
# print(f"✅ Configuration Django : environnement {ENVIRONMENT.upper()}")

# # Chargement modulaire
# include(
#     BASE_DIR / "config" / "settings" / "modules" / "base.py",
#     BASE_DIR / "config" / "settings" / "modules" / "apps.py",
#     BASE_DIR / "config" / "settings" / "modules" / "database.py",
#     BASE_DIR / "config" / "settings" / "modules" / "email.py",
#     BASE_DIR / "config" / "settings" / "modules" / "logging.py",
#     BASE_DIR / "config" / "settings" / "modules" / "celery.py",
#     BASE_DIR / "config" / "settings" / "modules" / "ckeditor.py",
#     BASE_DIR / "config" / "settings" / "modules" / "middleware.py",
#     BASE_DIR / "config" / "settings" / "modules" / "static.py",
#     BASE_DIR / "config" / "settings" / "modules" / "security.py",
#     BASE_DIR / "config" / "settings" / "modules" / "templates.py",
#     BASE_DIR / "config" / "settings" / "modules" / "internationalization.py",
#     BASE_DIR / "config" / "settings" / "modules" / "third_party.py",
#     BASE_DIR / "config" / "settings" / "modules" / "authentication.py",
#     BASE_DIR / "config" / "settings" / "environments" / f"{ENVIRONMENT}.py",
# )



