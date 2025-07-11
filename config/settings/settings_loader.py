import os
import sys
from pathlib import Path

from decouple import config
from django.core.exceptions import ImproperlyConfigured
from split_settings.tools import include

# Load base settings
from .modules.base import *

# === Base directory ===
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# === Add sogentis_apps to Python path ===
sys.path.insert(0, str(BASE_DIR / "sogentis_apps"))


def get_settings_module() -> str:
    """
    Returns the settings module path based on the DJANGO_ENV environment variable.
    Raises ImproperlyConfigured for invalid values.
    """
    env = config("DJANGO_ENV", default="local").strip().lower()

    env_settings = {
        "local": "local",
        "dev": "dev",
        "prod": "prod",
        "test": "test",
    }

    if env not in env_settings:
        raise ImproperlyConfigured(
            f"L'environnement DJANGO_ENV='{env}' est invalide. "
            f"Valeurs valides : {', '.join(env_settings)}"
        )

    return env_settings[env]

print("TEST_ENV_VAR =", config("TEST_ENV_VAR", default="not found"))

# === Set the Django settings module dynamically ===
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

# === Include settings modules dynamically ===
ENVIRONMENT = get_settings_module()

include(
    "modules/base.py",
    "modules/database.py",
    "modules/logging.py",
    "modules/celery.py",
    "modules/middleware.py",
    "modules/static.py",
    "modules/security.py",
    "modules/templates.py",
    "modules/internationalization.py",
    "modules/third_party.py",
    "modules/authentication.py",
    f"environments/{ENVIRONMENT}.py",
)
