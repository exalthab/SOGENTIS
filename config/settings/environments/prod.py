import os
from decouple import Csv, config
from dotenv import load_dotenv
import dj_database_url

from ..modules.base import *

# === Load environment variables ===
load_dotenv()

# ===========================================
# SECURITY & DEBUG
# ===========================================
DEBUG = False
SECRET_KEY = config("SECRET_KEY")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# ===========================================
# DATABASE
# ===========================================
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600
    )
}

if not DEBUG:
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

# ===========================================
# SECURITY SETTINGS
# ===========================================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ===========================================
# EMAIL CONFIGURATION (SMTP)
# ===========================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# ===========================================
# REDIS & CACHING
# ===========================================
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# ===========================================
# CELERY CONFIGURATION
# ===========================================
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# ===========================================
# SENTRY (OPTIONAL)
# ===========================================
# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration
# sentry_sdk.init(
#     dsn=config("SENTRY_DSN", default=""),
#     integrations=[DjangoIntegration()],
#     traces_sample_rate=0.5,
#     send_default_pii=True,
# )

# ===========================================
# AWS S3 STORAGE (OPTIONAL)
# ===========================================
USE_S3 = config("USE_S3", default=False, cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    # Optional to disable querystring auth for public files
    AWS_QUERYSTRING_AUTH = False
else:
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"

# ===========================================
# LOGGING
# ===========================================
LOG_DIR = os.getenv("DJANGO_LOG_DIR", "/var/log/sogentis")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, "django_error.log"),
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

# ===========================================
# CORS / CSRF TRUSTED ORIGINS
# ===========================================
CSRF_TRUSTED_ORIGINS = [
    "https://sogentis.org",
    "https://www.sogentis.org",
]
