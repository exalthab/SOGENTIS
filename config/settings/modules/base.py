# config/settings/modules/base.py
from pathlib import Path
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parents[3]

DEBUG = config("DEBUG", cast=bool, default=False)
DJANGO_ENV = config("DJANGO_ENV", default="local").strip().lower()

SECRET_KEY = config("SECRET_KEY", default=None)
if not SECRET_KEY or SECRET_KEY == "insecure-secret-for-dev":
    raise ImproperlyConfigured("❌ SECRET_KEY must be securely defined in your .env!")

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=Csv(),
    default=[],
)
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("❌ ALLOWED_HOSTS must not be empty.")

PROJECT_NAME = "SOGENTIS"
APP_VERSION = "1.0"

# Stripe (si tu veux les garder en base)
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

SOCIAL_LINKS = {
    "facebook": "https://facebook.com/sogentis",
    "twitter": "https://x.com/sogentis_org",
    "youtube": "https://youtube.com/@sogentis",
}

# # ===========================================================
# # URLS / WSGI
# # ===========================================================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SOCIAL_BASE_URL = config("SOCIAL_BASE_URL", default="https://sogentis.org").rstrip("/")
COMMERCIAL_BASE_URL = config("COMMERCIAL_BASE_URL", default="https://sogentis.com").rstrip("/")
INSTITUTION_BASE_URL = config("INSTITUTION_BASE_URL", default="https://sogentis.sn").rstrip("/")

# Optionnel si tu sépares dashboard



# # config/settings/modules/base.py

# import os
# from pathlib import Path
# from decouple import config, Csv
# from django.core.exceptions import ImproperlyConfigured
# import dj_database_url

# # ------------------------------------------------------------
# # IMPORTS DES AUTRES MODULES SETTINGS
# # ------------------------------------------------------------

# # Internationalisation (LANGUAGES, LOCALE_PATHS, etc.)
# from config.settings.modules.internationalization import *

# # Static / Media / CKEditor
# from config.settings.modules.apps import *
# from config.settings.modules.static import *
# from config.settings.modules.ckeditor import *

# # ------------------------------------------------------------
# # BASE DIRECTORY
# # ------------------------------------------------------------
# # BASE_DIR = Path(__file__).resolve(strict=True).parents[2]
# BASE_DIR = Path(__file__).resolve().parents[2]


# # ------------------------------------------------------------
# # ENVIRONMENT FLAGS
# # ------------------------------------------------------------
# DEBUG = config("DEBUG", default=False, cast=bool)
# DJANGO_ENV = config("DJANGO_ENV", default="local").lower()


# # ------------------------------------------------------------
# # SECURITY KEY
# # ------------------------------------------------------------
# SECRET_KEY = config("SECRET_KEY", default=None)
# if not SECRET_KEY or SECRET_KEY == "insecure-secret-for-dev":
#     raise ImproperlyConfigured("❌ SECRET_KEY must be securely defined in your .env!")


# # ------------------------------------------------------------
# # ALLOWED HOSTS
# # ------------------------------------------------------------
# ALLOWED_HOSTS = config(
#     "ALLOWED_HOSTS",
#     default="sogentis.org,www.sogentis.org,sogentis.com,www.sogentis.com,sogentis.sn,www.sogentis.sn,127.0.0.1,localhost",
#     cast=Csv()
# )

# if not ALLOWED_HOSTS:
#     raise ImproperlyConfigured("❌ ALLOWED_HOSTS must not be empty.")


# # ------------------------------------------------------------
# # PROJECT INFO
# # ------------------------------------------------------------
# PROJECT_NAME = "SOGENTIS"
# APP_VERSION = "1.0"


# # ------------------------------------------------------------
# # STRIPE
# # ------------------------------------------------------------
# STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
# STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
# STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")
# DOMAIN = config("DOMAIN", default="https://sogentis.org")


# # ----------------------------------------------------------
# # SOCIAL LINKS
# # ----------------------------------------------------------
 
# SOCIAL_LINKS = {
#     "facebook": "https://facebook.com/sogentis",
#     "twitter": "https://x.com/sogentis_org",
#     "youtube": "https://youtube.com/@sogentis",
#     # "linkedin": "https://linkedin.com/company/sogentis",
# }
