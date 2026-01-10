# config/settings/modules/base.py
from pathlib import Path
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured

# ===========================================================
# BASE
# ===========================================================
BASE_DIR = Path(__file__).resolve().parents[2]

DEBUG = config("DEBUG", cast=bool, default=False)
DJANGO_ENV = config("DJANGO_ENV", default="local").strip().lower()

# ===========================================================
# SECURITY
# ===========================================================
SECRET_KEY = config("SECRET_KEY", default="insecure-secret-for-dev")

# En prod (DEBUG=False), on refuse une clé “dev”
if (not SECRET_KEY) or (SECRET_KEY == "insecure-secret-for-dev"):
    if not DEBUG:
        raise ImproperlyConfigured("❌ SECRET_KEY must be securely defined in your .env (production).")

# ===========================================================
# HOSTS
# ===========================================================
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=[])
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("❌ ALLOWED_HOSTS must not be empty.")

# En prod (DEBUG=False), on refuse une liste vide
if (not ALLOWED_HOSTS) and (not DEBUG):
    raise ImproperlyConfigured("❌ ALLOWED_HOSTS must not be empty in production.")

# ===========================================================
# PROJECT META
# ===========================================================
PROJECT_NAME = config("PROJECT_NAME", default="SOGENTIS")
APP_VERSION = config("APP_VERSION", default="1.0")

SLOGAN = config("SLOGAN", default="Unir le social et l’économique")
FOOTER_CITATION = config("FOOTER_CITATION", default="“Ensemble, faisons la différence.”")

CONTACT_EMAIL = config("CONTACT_EMAIL", default="contact@sogentis.org")
CONTACT_PHONE = config("CONTACT_PHONE", default="+221 123 456 789")
GITHUB_URL = config("GITHUB_URL", default="https://github.com/sogentis")

SOCIAL_LINKS = {
    "facebook": config("FACEBOOK_URL", default="https://facebook.com/sogentis"),
    "twitter": config("TWITTER_URL", default="https://x.com/sogentis_org"),
    "youtube": config("YOUTUBE_URL", default="https://youtube.com/@sogentis"),
}

# ===========================================================
# URLS / WSGI
# ===========================================================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===========================================================
# DOMAINS / BASE URLS
# ===========================================================
SOCIAL_BASE_URL = config("SOCIAL_BASE_URL", default="https://sogentis.org").rstrip("/")
COMMERCIAL_BASE_URL = config("COMMERCIAL_BASE_URL", default="https://sogentis.com").rstrip("/")
INSTITUTION_BASE_URL = config("INSTITUTION_BASE_URL", default="https://sogentis.sn").rstrip("/")

# ===========================================================
# SEO DEFAULTS (optionnel)
# ===========================================================
SEO_TITLE_DEFAULT = config("SEO_TITLE_DEFAULT", default=f"{PROJECT_NAME} – {SLOGAN}")
SEO_DESCRIPTION_DEFAULT = config(
    "SEO_DESCRIPTION_DEFAULT",
    default=(
        "SOGENTIS est une plateforme sociale et économique dédiée à l'enfance, "
        "aux mamans, aux communautés et aux projets de développement."
    ),
)

# Chemin static (pas une URL absolue) : utilisé via static() dans le context processor
SEO_OG_IMAGE_DEFAULT_PATH = config("SEO_OG_IMAGE_DEFAULT_PATH", default="global/image/og_default_sogentis.png")






# # config/settings/modules/base.py
# from pathlib import Path
# from decouple import config, Csv
# from django.core.exceptions import ImproperlyConfigured

# BASE_DIR = Path(__file__).resolve().parents[3]

# DEBUG = config("DEBUG", cast=bool, default=False)
# DJANGO_ENV = config("DJANGO_ENV", default="local").strip().lower()

# SECRET_KEY = config("SECRET_KEY", default=None)
# if not SECRET_KEY or SECRET_KEY == "insecure-secret-for-dev":
#     raise ImproperlyConfigured("❌ SECRET_KEY must be securely defined in your .env!")

# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=[])
# if not ALLOWED_HOSTS:
#     raise ImproperlyConfigured("❌ ALLOWED_HOSTS must not be empty.")

# PROJECT_NAME = "SOGENTIS"
# APP_VERSION = "1.0"

# SOCIAL_LINKS = {
#     "facebook": "https://facebook.com/sogentis",
#     "twitter": "https://x.com/sogentis_org",
#     "youtube": "https://youtube.com/@sogentis",
# }

# # ===========================================================
# # URLS / WSGI
# # ===========================================================
# ROOT_URLCONF = "config.urls"
# WSGI_APPLICATION = "config.wsgi.application"
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# SOCIAL_BASE_URL = config("SOCIAL_BASE_URL", default="https://sogentis.org").rstrip("/")
# COMMERCIAL_BASE_URL = config("COMMERCIAL_BASE_URL", default="https://sogentis.com").rstrip("/")
# INSTITUTION_BASE_URL = config("INSTITUTION_BASE_URL", default="https://sogentis.sn").rstrip("/")





# # config/settings/modules/base.py
# from pathlib import Path
# from decouple import config, Csv
# from django.core.exceptions import ImproperlyConfigured

# BASE_DIR = Path(__file__).resolve().parents[3]

# DEBUG = config("DEBUG", cast=bool, default=False)
# DJANGO_ENV = config("DJANGO_ENV", default="local").strip().lower()

# SECRET_KEY = config("SECRET_KEY", default=None)
# if not SECRET_KEY or SECRET_KEY == "insecure-secret-for-dev":
#     raise ImproperlyConfigured("❌ SECRET_KEY must be securely defined in your .env!")

# ALLOWED_HOSTS = config(
#     "ALLOWED_HOSTS",
#     cast=Csv(),
#     default=[],
# )
# if not ALLOWED_HOSTS:
#     raise ImproperlyConfigured("❌ ALLOWED_HOSTS must not be empty.")

# PROJECT_NAME = "SOGENTIS"
# APP_VERSION = "1.0"

# # Stripe (si tu veux les garder en base)
# STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
# STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
# STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

# SOCIAL_LINKS = {
#     "facebook": "https://facebook.com/sogentis",
#     "twitter": "https://x.com/sogentis_org",
#     "youtube": "https://youtube.com/@sogentis",
# }

# # # ===========================================================
# # # URLS / WSGI
# # # ===========================================================
# ROOT_URLCONF = "config.urls"
# WSGI_APPLICATION = "config.wsgi.application"
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# SOCIAL_BASE_URL = config("SOCIAL_BASE_URL", default="https://sogentis.org").rstrip("/")
# COMMERCIAL_BASE_URL = config("COMMERCIAL_BASE_URL", default="https://sogentis.com").rstrip("/")
# INSTITUTION_BASE_URL = config("INSTITUTION_BASE_URL", default="https://sogentis.sn").rstrip("/")

# # Optionnel si tu sépares dashboard



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
