from decouple import config

# -------------------------------------------------------------------
# EMAIL BACKEND (DEV ou PROD)
# -------------------------------------------------------------------
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)

# -------------------------------------------------------------------
# EXPÉDITEUR PAR DEFAUT
# -------------------------------------------------------------------
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="SOGENTIS <no-reply@sogentis.test>"
)

# -------------------------------------------------------------------
# SMTP CONFIG — UTILISÉ SEULEMENT SI EMAIL_BACKEND = SMTP
# -------------------------------------------------------------------
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)

# -------------------------------------------------------------------
# (OPTIONNEL)
# -------------------------------------------------------------------
EMAIL_TIMEOUT = 30
