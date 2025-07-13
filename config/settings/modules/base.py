import os
from pathlib import Path
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

# === BASE DIRECTORY ===
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# === ENV FLAGS ===
DEBUG = config("DEBUG", default=False, cast=bool)
DJANGO_ENV = config("DJANGO_ENV", default="local").lower()

# === SECURITY KEY ===
SECRET_KEY = config("SECRET_KEY", default=None)
if not SECRET_KEY or SECRET_KEY == "insecure-secret-for-dev":
    raise ImproperlyConfigured("❌ SECRET_KEY must be securely defined in your .env!")

# === ALLOWED HOSTS ===
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="sogentis.org,www.sogentis.org,127.0.0.1,localhost",
    cast=Csv()
)

# === PROJECT INFO ===
PROJECT_NAME = "SOGENTIS"
APP_VERSION = "1.0"

# === STRIPE ===
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")
DOMAIN = config("DOMAIN", default="https://sogentis.org")

# === INSTALLED APPS ===
INSTALLED_APPS = [
    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Local Apps
    "core",
    "accounts_users",
    "accounts_users.authentication",
    "accounts_users.global_permissions",
    "economic",
    "economic.ecommerce",
    "economic.formations",
    "economic.gestion_projets",
    "social",
    "social.aid",
    "dashboard",
    "stakeholders",
    "stakeholders.beneficiaries",
    "stakeholders.volunteers",
    "stakeholders.members",
    "stakeholders.friends",

    # Développement uniquement
    # "sslserver",  # ❌ à désactiver en production
]

# === AUTH ===
AUTH_USER_MODEL = "accounts_users.CustomUser"
LOGIN_URL = "accounts_users_web:login"
LOGIN_REDIRECT_URL = "dashboard:index"
LOGOUT_REDIRECT_URL = "accounts_users_web:logout"

# === EMAIL ===
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="mail.infomaniak.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="contact@sogentis.org")
CONTACT_EMAIL = config("CONTACT_EMAIL", default="admin@sogentis.org")

ADMINS = [("Admin SOGENTIS", "utracorp@gmail.com")]

# === EMAIL SECURE CHECK ===
if not DEBUG and not EMAIL_HOST_PASSWORD:
    raise ImproperlyConfigured("❌ EMAIL_HOST_PASSWORD must be set in production")

# === WSGI/URL ===
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === STATIC & MEDIA ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === DATABASE ===
DATABASE_URL = config("DATABASE_URL", default=None)
if not DATABASE_URL:
    raise ImproperlyConfigured("❌ DATABASE_URL must be defined in your .env")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600
    )
}

if not DEBUG:
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

# === SECURITY HEADERS (production only) ===
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
