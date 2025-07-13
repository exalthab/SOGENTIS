# config/settings/modules/database.py

import dj_database_url
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# Récupération de l'URL de connexion à la base
DATABASE_URL = config("DATABASE_URL", default=None)

if not DATABASE_URL or DATABASE_URL.strip() == "":
    raise ImproperlyConfigured("❌ DATABASE_URL est vide ou non défini dans le fichier .env")

# Configuration principale de la base de données
DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# SSL activé uniquement en production (DEBUG=False)
DEBUG = config("DEBUG", default=False, cast=bool)
if not DEBUG:
    DATABASES["default"]["OPTIONS"] = {
        "sslmode": "require"
    }

# Test facultatif : affichage de confirmation en console
if config("DJANGO_ENV", default="local") != "local":
    print("✅ Base de données configurée avec succès pour l'environnement production.")
