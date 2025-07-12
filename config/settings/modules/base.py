import os
from pathlib import Path
from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

# === BASE DIRECTORY ===
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# === ENVIRONMENT FLAGS ===
DEBUG = config("DEBUG", default=False, cast=bool)

# === SECRET KEY ===
SECRET_KEY = config("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY == "insecure-secret-for-dev":
    raise ImproperlyConfigured("SECRET_KEY must be set securely in production!")

# === ALLOWED HOSTS ===
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="sogentis.org,www.sogentis.org,127.0.0.1,localhost", cast=Csv())

# === STRIPE CONFIGURATION ===
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")
DOMAIN = config("DOMAIN", default="sogentis.org")

# === APPLICATION DEFINITION ===
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Externes (désactive ce que tu n'utilises pas)
    # "rest_framework",
    # "crispy_forms",
    # "django_countries",
    # Local apps
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
    # "sslserver",  # ❌ à retirer en production
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==== AUTHENTICATION REDIRECTS ====
LOGIN_URL = 'accounts_users_web:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'accounts_users_web:logout'

# === EMAIL CONFIG ===
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="mail.infomaniak.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="contact@sogentis.org")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

if not DEBUG and not EMAIL_HOST_PASSWORD:
    raise ImproperlyConfigured("EMAIL_HOST_PASSWORD must be set in production")

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="contact@sogentis.org")
CONTACT_EMAIL = config("CONTACT_EMAIL", default="contact@sogentis.org")
ADMINS = [("Admin SOGENTIS", "utracorp@gmail.com")]

PROJECT_NAME = "SOGENTIS"
APP_VERSION = "1.0"

# === SECURE PRODUCTION SETTINGS ===
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# === STATIC & MEDIA ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === DATABASE ===
import dj_database_url
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL")
    )
}
