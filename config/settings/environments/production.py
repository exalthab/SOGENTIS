# config/settings/production.py
import os

import dj_database_url
from decouple import Csv, config
from django.core.exceptions import ImproperlyConfigured

from config.settings.modules.base import *


# ===========================================================
# UTILITAIRE – VARIABLES D’ENV OBLIGATOIRES
# ===========================================================
def require_env(name: str) -> str:
    value = config(name, default=None)
    if not value:
        raise ImproperlyConfigured(f"❌ Variable d’environnement obligatoire manquante : {name}")
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

DB_SSL_REQUIRE = config("DB_SSL_REQUIRE", cast=bool, default=False)  # ✅ évite de casser Postgres local
DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=DB_SSL_REQUIRE,
    )
}


# ===========================================================
# EMAIL
# ===========================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = require_env("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)

EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)

# ✅ TLS et SSL ne doivent pas être True ensemble
if EMAIL_USE_SSL and EMAIL_USE_TLS:
    EMAIL_USE_TLS = False

EMAIL_HOST_USER = require_env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = require_env("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)


# ===========================================================
# HEADERS DE SÉCURITÉ (Reverse Proxy Nginx)
# ===========================================================
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool, default=True)

# ✅ Indispensable si TLS est terminé côté Nginx
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_REFERRER_POLICY = "same-origin"


# ===========================================================
# CACHE / REDIS
# ===========================================================
REDIS_URL = config("REDIS_URL", default="redis://127.0.0.1:6379/1")

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
# STATIC & MEDIA – S3 OPTIONNEL (Django 5+ propre)
# ===========================================================
USE_S3 = config("USE_S3", cast=bool, default=False)

if USE_S3:
    AWS_ACCESS_KEY_ID = require_env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = require_env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = require_env("AWS_STORAGE_BUCKET_NAME")

    AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME", default=None)
    AWS_S3_CUSTOM_DOMAIN = config(
        "AWS_S3_CUSTOM_DOMAIN",
        default=f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com",
    )

    AWS_QUERYSTRING_AUTH = False

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

    # ✅ Django 4.2+ / 5.x
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "location": "media",
                "querystring_auth": False,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "location": "static",
                "querystring_auth": False,
            },
        },
    }

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
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    cast=Csv(),
    default=[
        "https://sogentis.org",
        "https://www.sogentis.org",
        "https://sogentis.sn",
        "https://www.sogentis.sn",
        "https://sogentis.com",
        "https://www.sogentis.com",
    ],
)


# ===========================================================
# TEMPLATES – CACHE FORCÉ EN PROD
# ===========================================================
USE_TEMPLATE_CACHING = True


# ===========================================================
# DOMAIN ROUTING (.com/.org/.sn)
# ===========================================================
DOMAIN_SITE_MAP = {
    "sogentis.com": "business",
    "sogentis.org": "social",
    "sogentis.sn": "sn",
}

# redirige "/" et "/en/" vers la home du site_type
DOMAIN_REDIRECT_ROOT = True
# 302 conseillé (anti-cache), mets True si tu veux 301
DOMAIN_REDIRECT_PERMANENT = False

BUSINESS_HOME_URLNAME = "economic:index"
SOCIAL_HOME_URLNAME = "social:index"
SN_HOME_URLNAME = "institution:index"
DEFAULT_HOME_URLNAME = "core:home"

# Important derrière Nginx SSL (évite boucle SECURE_SSL_REDIRECT)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True


DOMAIN_BYPASS_PREFIXES = (
    "/admin/",
    "/accounts/",
    "/dashboard/",
    "/i18n/",
    "/static/",
    "/media/",
)




# # config/settings/production.py 06/01/2026
# import os

# from decouple import config, Csv
# import dj_database_url
# from django.core.exceptions import ImproperlyConfigured

# from config.settings.modules.base import *


# # ===========================================================
# # UTILITAIRE – VARIABLES D’ENV OBLIGATOIRES
# # ===========================================================
# def require_env(name: str) -> str:
#     value = config(name, default=None)
#     if not value:
#         raise ImproperlyConfigured(
#             f"❌ Variable d’environnement obligatoire manquante : {name}"
#         )
#     return value


# # ===========================================================
# # DEBUG & SÉCURITÉ GLOBALE
# # ===========================================================
# DEBUG = config("DEBUG", cast=bool, default=False)
# if DEBUG:
#     raise ImproperlyConfigured("❌ DEBUG doit être désactivé en production.")

# SECRET_KEY = require_env("SECRET_KEY")

# ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=[])
# if not ALLOWED_HOSTS:
#     raise ImproperlyConfigured("❌ ALLOWED_HOSTS ne peut pas être vide en production.")


# # ===========================================================
# # DATABASE
# # ===========================================================
# DATABASE_URL = require_env("DATABASE_URL")

# DATABASES = {
#     "default": dj_database_url.parse(
#         DATABASE_URL,
#         conn_max_age=600,
#         ssl_require=True,
#     )
# }


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
# DEFAULT_FROM_EMAIL = config(
#     "DEFAULT_FROM_EMAIL",
#     default=EMAIL_HOST_USER,
# )


# # ===========================================================
# # HEADERS DE SÉCURITÉ
# # ===========================================================
# SECURE_SSL_REDIRECT = True

# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True

# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True

# X_FRAME_OPTIONS = "DENY"
# SECURE_CONTENT_TYPE_NOSNIFF = True

# # Django >= 4.0 : filtre XSS obsolète → volontairement retiré

# SECURE_HSTS_SECONDS = 31536000  # 1 an
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True


# # ===========================================================
# # CACHE / REDIS
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
# # STATIC & MEDIA – S3 OPTIONNEL
# # ===========================================================
# USE_S3 = config("USE_S3", cast=bool, default=False)

# if USE_S3:
#     AWS_ACCESS_KEY_ID = require_env("AWS_ACCESS_KEY_ID")
#     AWS_SECRET_ACCESS_KEY = require_env("AWS_SECRET_ACCESS_KEY")
#     AWS_STORAGE_BUCKET_NAME = require_env("AWS_STORAGE_BUCKET_NAME")

#     AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
#     AWS_QUERYSTRING_AUTH = False

#     STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
#     MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

#     STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
#     DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# else:
#     STATIC_URL = "/static/"
#     STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # collectstatic
#     MEDIA_URL = "/media/"
#     MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# # ===========================================================
# # CKEDITOR
# # ===========================================================
# CKEDITOR_UPLOAD_PATH = "uploads/"


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
# # TEMPLATES – CACHE FORCÉ EN PROD
# # ===========================================================
# USE_TEMPLATE_CACHING = True


# DOMAIN_SITE_MAP = {
#     # si tu veux matcher précisément :
#     "sogentis.com": "business",
#     "sogentis.org": "social",
#     "sogentis.sn": "sn",
# }

# DOMAIN_REDIRECT_ROOT = True

# BUSINESS_HOME_URLNAME = "economic:index"
# SOCIAL_HOME_URLNAME = "social:index"
# SN_HOME_URLNAME = "core:home"  # ou "institution:index" si tu as cette app
# DEFAULT_HOME_URLNAME = "core:home"



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

