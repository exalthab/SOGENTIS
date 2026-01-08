# config/settings/modules/database.py
import dj_database_url
from decouple import config
from django.core.exceptions import ImproperlyConfigured

DATABASE_URL = (config("DATABASE_URL", default="") or "").strip()

if not DATABASE_URL:
    raise ImproperlyConfigured(
        "❌ DATABASE_URL est vide ou non défini dans le fichier .env"
    )

DB_SSL_REQUIRE = config("DB_SSL_REQUIRE", cast=bool, default=False)

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=DB_SSL_REQUIRE,
    )
}






# # config/settings/modules/database.py
# import dj_database_url
# from decouple import config
# from django.core.exceptions import ImproperlyConfigured

# DATABASE_URL = config("DATABASE_URL", default=None)
# if not DATABASE_URL or not DATABASE_URL.strip():
#     raise ImproperlyConfigured("❌ DATABASE_URL est vide ou non défini dans le fichier .env")

# DB_SSL_REQUIRE = config("DB_SSL_REQUIRE", cast=bool, default=False)

# DATABASES = {
#     "default": dj_database_url.parse(
#         DATABASE_URL,
#         conn_max_age=600,
#         ssl_require=DB_SSL_REQUIRE,
#     )
# }





# # config/settings/modules/database.py

# import dj_database_url
# from decouple import config
# from django.core.exceptions import ImproperlyConfigured

# # =========================
# # Variables d'environnement
# # =========================
# ENV = config("DJANGO_ENV", default="local")
# DEBUG = config("DEBUG", default=False, cast=bool)
# DATABASE_URL = config("DATABASE_URL", default=None)

# # =========================
# # Vérification DATABASE_URL
# # =========================
# if not DATABASE_URL or DATABASE_URL.strip() == "":
#     raise ImproperlyConfigured("❌ DATABASE_URL est vide ou non défini dans le fichier .env")

# # =========================
# # Configuration de la DB
# # =========================
# DATABASES = {
#     "default": dj_database_url.config(
#         default=DATABASE_URL,
#         conn_max_age=600,
#         ssl_require=not DEBUG  # SSL activé si production
#     )
# }

# # ===========================================================
# # AUTHENTICATION
# # ===========================================================
# AUTH_USER_MODEL = "accounts_users.CustomUser"
# LOGIN_URL = "accounts_users_web:login"
# LOGIN_REDIRECT_URL = "dashboard:index"
# LOGOUT_REDIRECT_URL = "accounts_users_web:login"

# # ===========================================================
# # EMAIL CONFIGURATION
# # ===========================================================
# EMAIL_BACKEND = config("EMAIL_BACKEND", default=None)
# if not EMAIL_BACKEND:
#     raise ImproperlyConfigured("❌ EMAIL_BACKEND is not set in environment.")

# EMAIL_HOST = config("EMAIL_HOST")
# EMAIL_PORT = config("EMAIL_PORT", cast=int)
# EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool)
# EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool)

# # Vérification cohérence TLS/SSL
# if EMAIL_USE_TLS and EMAIL_USE_SSL:
#     raise ImproperlyConfigured("❌ EMAIL_USE_TLS and EMAIL_USE_SSL cannot both be True.")

# EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
# DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="")
# CONTACT_EMAIL = config("CONTACT_EMAIL", default="")

# # Vérification sécurité en production
# if not DEBUG and not EMAIL_HOST_PASSWORD:
#     raise ImproperlyConfigured("❌ EMAIL_HOST_PASSWORD must be set in production")

# # ===========================================================
# # URLS / WSGI
# # ===========================================================
# ROOT_URLCONF = "config.urls"
# WSGI_APPLICATION = "config.wsgi.application"
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# # =========================
# # Confirmation (optionnelle)
# # =========================
# if ENV != "local":
#     print("✅ Base de données configurée avec succès pour l'environnement production.")
