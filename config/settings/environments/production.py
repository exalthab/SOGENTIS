import os

from decouple import config, Csv
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from config.settings.modules.base import *


# ===========================================================
# UTILITAIRE – VARIABLES D’ENV OBLIGATOIRES
# ===========================================================
def require_env(name: str) -> str:
    value = config(name, default=None)
    if not value:
        raise ImproperlyConfigured(
            f"❌ Variable d’environnement obligatoire manquante : {name}"
        )
    return value


# ===========================================================
# DEBUG & SÉCURITÉ GLOBALE
# ===========================================================
DEBUG = config("DEBUG", cast=bool, default=False)
if DEBUG:
    raise ImproperlyConfigured("❌ DEBUG doit être désactivé en production.")

SECRET_KEY = require_env("SECRET_KEY")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=[])
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("❌ ALLOWED_HOSTS ne peut pas être vide en production.")


# ===========================================================
# DATABASE
# ===========================================================
DATABASE_URL = require_env("DATABASE_URL")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )
}


# ===========================================================
# EMAIL
# ===========================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = require_env("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_HOST_USER = require_env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = require_env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER,
)


# ===========================================================
# HEADERS DE SÉCURITÉ
# ===========================================================
SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Django >= 4.0 : filtre XSS obsolète → volontairement retiré

SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# ===========================================================
# CACHE / REDIS
# ===========================================================
REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/1")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}


# ===========================================================
# CELERY
# ===========================================================
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"


# ===========================================================
# STATIC & MEDIA – S3 OPTIONNEL
# ===========================================================
USE_S3 = config("USE_S3", cast=bool, default=False)

if USE_S3:
    AWS_ACCESS_KEY_ID = require_env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = require_env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = require_env("AWS_STORAGE_BUCKET_NAME")

    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_QUERYSTRING_AUTH = False

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

else:
    STATIC_URL = "/static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # collectstatic
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# ===========================================================
# CKEDITOR
# ===========================================================
CKEDITOR_UPLOAD_PATH = "uploads/"


# ===========================================================
# CSRF TRUSTED ORIGINS
# ===========================================================
CSRF_TRUSTED_ORIGINS = [
    "https://sogentis.org",
    "https://www.sogentis.org",
    "https://sogentis.sn",
    "https://www.sogentis.sn",
    "https://sogentis.com",
    "https://www.sogentis.com",
]


# ===========================================================
# TEMPLATES – CACHE FORCÉ EN PROD
# ===========================================================
USE_TEMPLATE_CACHING = True





# # config/settings/environments/production.py

# import os
# from decouple import config, Csv
# import dj_database_url
# from django.core.exceptions import ImproperlyConfigured

# from config.settings.modules.base import *



# # ===========================================================
# # FONCTION D'AIDE POUR VARIABLES D'ENV
# # ===========================================================
# def require_env(name: str) -> str:
#     value = config(name, default=None)
#     if not value:
#         raise ImproperlyConfigured(f"❌ Variable d’environnement obligatoire manquante : {name}")
#     return value

# # ===========================================================
# # DEBUG & SECURITY
# # ===========================================================
# DEBUG = config("DEBUG", cast=bool, default=False)
# if DEBUG:
#     raise ImproperlyConfigured("DEBUG doit être désactivé en production.")

# SECRET_KEY = require_env("SECRET_KEY")
# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
# if not ALLOWED_HOSTS:
#     raise ImproperlyConfigured("❌ ALLOWED_HOSTS ne peut pas être vide en production.")

# # ===========================================================
# # DATABASE
# # ===========================================================
# DATABASE_URL = require_env("DATABASE_URL")
# DATABASES = {
#     "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
# }
# DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

# # ===========================================================
# # EMAIL
# # ===========================================================
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = require_env("EMAIL_HOST")
# EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
# EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
# EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
# EMAIL_HOST_USER = require_env("EMAIL_HOST_USER")
# EMAIL_HOST_PASSWORD = require_env("EMAIL_HOST_PASSWORD")
# DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)

# # ===========================================================
# # SECURITY HEADERS
# # ===========================================================
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
# CSRF_COOKIE_HTTPONLY = True
# X_FRAME_OPTIONS = "DENY"
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# # ===========================================================
# # CACHING / REDIS
# # ===========================================================
# REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/1")
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": REDIS_URL,
#     }
# }

# # ===========================================================
# # CELERY
# # ===========================================================
# CELERY_BROKER_URL = REDIS_URL
# CELERY_RESULT_BACKEND = REDIS_URL
# CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"

# # ===========================================================
# # S3 OPTIONNEL
# # ===========================================================
# USE_S3 = config("USE_S3", default=False, cast=bool)
# if USE_S3:
#     AWS_ACCESS_KEY_ID = require_env("AWS_ACCESS_KEY_ID")
#     AWS_SECRET_ACCESS_KEY = require_env("AWS_SECRET_ACCESS_KEY")
#     AWS_STORAGE_BUCKET_NAME = require_env("AWS_STORAGE_BUCKET_NAME")
#     AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

#     STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
#     MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

#     STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
#     DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
#     AWS_QUERYSTRING_AUTH = False
# else:
#     STATIC_URL = "/static/"
#     STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")   # IMPORTANT: pour collectstatic
#     MEDIA_URL = "/media/"
#     MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# # ===========================================================
# # CKEDITOR
# # ===========================================================
# CKEDITOR_UPLOAD_PATH = "uploads/"  # sous MEDIA_ROOT/uploads

# # ===========================================================
# # CSRF TRUSTED ORIGINS
# # ===========================================================
# CSRF_TRUSTED_ORIGINS = [
#     "https://sogentis.org",
#     "https://www.sogentis.org",
#     "https://sogentis.sn",
#     "https://www.sogentis.sn",
#     "https://sogentis.com",
#     "https://www.sogentis.com",
# ]

# # ===========================================================
# # TEMPLATE CACHING
# # ===========================================================
# USE_TEMPLATE_CACHING = True

