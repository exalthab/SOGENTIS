# config/settings/modules/email.py
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
# EXPÉDITEUR PAR DÉFAUT + EMAIL SERVEUR (erreurs Django)
# ===========================================================
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default="no-reply@sogentis.org",
)

SERVER_EMAIL = config(
    "SERVER_EMAIL",
    default=DEFAULT_FROM_EMAIL,
)

# (optionnel mais pratique)
CONTACT_EMAIL = config("CONTACT_EMAIL", default="contact@sogentis.org")

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

# Optionnel (utile pour certains providers)
EMAIL_SSL_KEYFILE = config("EMAIL_SSL_KEYFILE", default=None)
EMAIL_SSL_CERTFILE = config("EMAIL_SSL_CERTFILE", default=None)

# ===========================================================
# RÈGLES DE COHÉRENCE
# ===========================================================
if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured("❌ EMAIL_USE_TLS et EMAIL_USE_SSL ne peuvent pas être True en même temps.")

# ===========================================================
# GARDE PROD – ÉVITER UNE CONFIG SMTP INCOMPLÈTE
# ===========================================================
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    missing = [
        name
        for name, value in {
            "EMAIL_HOST": EMAIL_HOST,
            # Si ton provider autorise SMTP sans auth, commente ces 2 checks.
            "EMAIL_HOST_USER": EMAIL_HOST_USER,
            "EMAIL_HOST_PASSWORD": EMAIL_HOST_PASSWORD,
        }.items()
        if not value
    ]

    if missing:
        raise ImproperlyConfigured(f"❌ Configuration SMTP incomplète : {', '.join(missing)}")

    # En production, on évite les emails bidons
    env = config("DJANGO_ENV", default="local").strip().lower()
    if env in {"prod", "production"}:
        df = (DEFAULT_FROM_EMAIL or "").strip()
        invalid = (not df) or ("@" not in df) or df.endswith(".test")
        if invalid:
            raise ImproperlyConfigured(
                "❌ DEFAULT_FROM_EMAIL doit être une adresse valide en production (ex: no-reply@sogentis.org)."
            )







# # config/settings/modules/email.py
# from decouple import config
# from django.core.exceptions import ImproperlyConfigured


# # ===========================================================
# # EMAIL BACKEND (DEV / PROD)
# # ===========================================================
# EMAIL_BACKEND = config(
#     "EMAIL_BACKEND",
#     default="django.core.mail.backends.console.EmailBackend",
# )

# # ===========================================================
# # EXPÉDITEUR PAR DÉFAUT + EMAIL SERVEUR (erreurs Django)
# # ===========================================================
# DEFAULT_FROM_EMAIL = config(
#     "DEFAULT_FROM_EMAIL",
#     default="no-reply@sogentis.org",
# )

# SERVER_EMAIL = config(
#     "SERVER_EMAIL",
#     default=DEFAULT_FROM_EMAIL,
# )

# # ===========================================================
# # SMTP CONFIG — UTILISÉ UNIQUEMENT SI SMTP
# # ===========================================================
# EMAIL_HOST = config("EMAIL_HOST", default="")
# EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)

# EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
# EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)

# EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", cast=int, default=30)

# # Optionnel (utile pour certains providers)
# EMAIL_SSL_KEYFILE = config("EMAIL_SSL_KEYFILE", default=None)
# EMAIL_SSL_CERTFILE = config("EMAIL_SSL_CERTFILE", default=None)


# # ===========================================================
# # RÈGLES DE COHÉRENCE
# # ===========================================================
# # TLS et SSL ne doivent pas être True en même temps
# if EMAIL_USE_TLS and EMAIL_USE_SSL:
#     raise ImproperlyConfigured("❌ EMAIL_USE_TLS et EMAIL_USE_SSL ne peuvent pas être True en même temps.")

# # ===========================================================
# # GARDE PROD – ÉVITER UNE CONFIG SMTP INCOMPLÈTE
# # ===========================================================
# if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
#     missing = [
#         name
#         for name, value in {
#             "EMAIL_HOST": EMAIL_HOST,
#             "EMAIL_HOST_USER": EMAIL_HOST_USER,
#             "EMAIL_HOST_PASSWORD": EMAIL_HOST_PASSWORD,
#         }.items()
#         if not value
#     ]

#     if missing:
#         raise ImproperlyConfigured(
#             f"❌ Configuration SMTP incomplète : {', '.join(missing)}"
#         )

#     # Si DEFAULT_FROM_EMAIL n’est pas crédible en prod, on force
#     if DEFAULT_FROM_EMAIL.endswith(".test") or "contact@sogentis.org" not in DEFAULT_FROM_EMAIL:
#         # pas de blocage dur si tu veux rester flexible :
#         # mais en prod c’est mieux d’obliger une vraie adresse
#         if config("DJANGO_ENV", default="local").strip().lower() in {"prod", "production"}:
#             raise ImproperlyConfigured(
#                 "❌ DEFAULT_FROM_EMAIL doit être une adresse réelle en production."
#             )





# # # config/settings/modules/email.py
# # from decouple import config
# # from django.core.exceptions import ImproperlyConfigured

# # # ===========================================================
# # # EMAIL BACKEND (DEV / PROD)
# # # ===========================================================
# # EMAIL_BACKEND = config(
# #     "EMAIL_BACKEND",
# #     default="django.core.mail.backends.console.EmailBackend",
# # )

# # # ===========================================================
# # # EXPÉDITEUR PAR DÉFAUT
# # # ===========================================================
# # DEFAULT_FROM_EMAIL = config(
# #     "DEFAULT_FROM_EMAIL",
# #     default="SOGENTIS <no-reply@sogentis.test>",
# # )

# # # ===========================================================
# # # SMTP CONFIG — UTILISÉ UNIQUEMENT SI SMTP
# # # ===========================================================
# # EMAIL_HOST = config("EMAIL_HOST", default="")
# # EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
# # EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# # EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
# # EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
# # EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
# # EMAIL_TIMEOUT = config("EMAIL_TIMEOUT", cast=int, default=30)

# # # ===========================================================
# # # GARDE PROD – ÉVITER UNE CONFIG SMTP INCOMPLÈTE
# # # ===========================================================
# # if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
# #     missing = [
# #         name for name, value in {
# #             "EMAIL_HOST": EMAIL_HOST,
# #             "EMAIL_HOST_USER": EMAIL_HOST_USER,
# #             "EMAIL_HOST_PASSWORD": EMAIL_HOST_PASSWORD,
# #         }.items() if not value
# #     ]

# #     if missing:
# #         raise ImproperlyConfigured(
# #             f"❌ Configuration SMTP incomplète : {', '.join(missing)}"
# #         )







# # # settings/modules/email.com
# # from decouple import config

# # # -------------------------------------------------------------------
# # # EMAIL BACKEND (DEV ou PROD)
# # # -------------------------------------------------------------------
# # EMAIL_BACKEND = config(
# #     "EMAIL_BACKEND",
# #     default="django.core.mail.backends.console.EmailBackend"
# # )

# # # -------------------------------------------------------------------
# # # EXPÉDITEUR PAR DEFAUT
# # # -------------------------------------------------------------------
# # DEFAULT_FROM_EMAIL = config(
# #     "DEFAULT_FROM_EMAIL",
# #     default="SOGENTIS <no-reply@sogentis.test>"
# # )

# # # -------------------------------------------------------------------
# # # SMTP CONFIG — UTILISÉ SEULEMENT SI EMAIL_BACKEND = SMTP
# # # -------------------------------------------------------------------
# # EMAIL_HOST = config("EMAIL_HOST", default="")
# # EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
# # EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
# # EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
# # EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
# # EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)

# # # -------------------------------------------------------------------
# # # (OPTIONNEL)
# # # -------------------------------------------------------------------
# # EMAIL_TIMEOUT = 30
