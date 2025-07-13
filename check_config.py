# check_config.py
import os
import sys
from pathlib import Path

import django
from decouple import config, UndefinedValueError
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent

# Set DJANGO_SETTINGS_MODULE if not already set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings_loader")

# Add sogentis_apps to path
sys.path.insert(0, str(BASE_DIR / "sogentis_apps"))

# Initialise Django
try:
    django.setup()
except Exception as e:
    print(f"❌ Erreur d'initialisation Django : {e}")
    sys.exit(1)

print("✅ Django initialisé avec succès")

# === ENV TESTS ===
env_checks = {
    "DJANGO_ENV": None,
    "SECRET_KEY": None,
    "DATABASE_URL": None,
    "EMAIL_HOST": None,
    "EMAIL_HOST_USER": None,
    "EMAIL_HOST_PASSWORD": None,
    "STRIPE_SECRET_KEY": None,
    "STRIPE_PUBLISHABLE_KEY": None,
    "DOMAIN": None,
    "LOG_PATH": None,
}

print("🔍 Vérification des variables d'environnement critiques :")
for var in env_checks:
    try:
        env_checks[var] = config(var)
        print(f"✅ {var} = {env_checks[var]}")
    except UndefinedValueError:
        print(f"❌ {var} n'est **pas défini** dans le fichier .env")
    except Exception as e:
        print(f"⚠️ Erreur lors de la lecture de {var} : {e}")

# === Settings Check ===
from django.conf import settings

print("\n🔎 Vérification des modules de settings chargés :")
required_attrs = [
    "BASE_DIR",
    "INSTALLED_APPS",
    "DATABASES",
    "TEMPLATES",
    "STATIC_URL",
    "MEDIA_URL",
    "ALLOWED_HOSTS",
]

missing = []
for attr in required_attrs:
    if not hasattr(settings, attr):
        print(f"❌ settings.{attr} est manquant")
        missing.append(attr)
    else:
        print(f"✅ settings.{attr} est présent")

if missing:
    print("\n⚠️ Des modules critiques de configuration semblent manquants !")
    sys.exit(2)

print("\n✅ Configuration Django complète et fonctionnelle.")
