from decouple import config
from django.core.exceptions import ImproperlyConfigured

# ===========================================================
# EMAIL BACKEND (DEV / PROD)
# ===========================================================
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

# ===========================================================
# EXPÉDITEUR PAR DÉFAUT
# ===========================================================
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="SOGENTIS <no-reply@sogentis.test>",
)

# ===========================================================
# SMTP CONFIG — UTILISÉ UNIQUEMENT SI SMTP
# ===========================================================
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", cast=int, default=30)

# ===========================================================
# GARDE PROD – ÉVITER UNE CONFIG SMTP INCOMPLÈTE
# ===========================================================
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    missing = [
        name for name, value in {
            "EMAIL_HOST": EMAIL_HOST,
            "EMAIL_HOST_USER": EMAIL_HOST_USER,
            "EMAIL_HOST_PASSWORD": EMAIL_HOST_PASSWORD,
        }.items() if not value
    ]

    if missing:
        raise ImproperlyConfigured(
            f"❌ Configuration SMTP incomplète : {', '.join(missing)}"
        )







# # settings/modules/email.com
# from decouple import config

# # -------------------------------------------------------------------
# # EMAIL BACKEND (DEV ou PROD)
# # -------------------------------------------------------------------
# EMAIL_BACKEND = config(
#     "EMAIL_BACKEND",
#     default="django.core.mail.backends.console.EmailBackend"
# )

# # -------------------------------------------------------------------
# # EXPÉDITEUR PAR DEFAUT
# # -------------------------------------------------------------------
# DEFAULT_FROM_EMAIL = config(
#     "DEFAULT_FROM_EMAIL",
#     default="SOGENTIS <no-reply@sogentis.test>"
# )

# # -------------------------------------------------------------------
# # SMTP CONFIG — UTILISÉ SEULEMENT SI EMAIL_BACKEND = SMTP
# # -------------------------------------------------------------------
# EMAIL_HOST = config("EMAIL_HOST", default="")
# EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
# EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
# EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
# EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)

# # -------------------------------------------------------------------
# # (OPTIONNEL)
# # -------------------------------------------------------------------
# EMAIL_TIMEOUT = 30
