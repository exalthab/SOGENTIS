# config/settings/modules/third_party.py

from decouple import config

# === Stripe settings ===
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="sk_test_FAKE_KEY_FOR_DEV")
STRIPE_PUBLISHABLE_KEY = config(
    "STRIPE_PUBLISHABLE_KEY", default="pk_test_FAKE_KEY_FOR_DEV"
)
STRIPE_WEBHOOK_SECRET = config(
    "STRIPE_WEBHOOK_SECRET", default="whsec_FAKE_WEBHOOK_SECRET"
)

# === Domain ===
DOMAIN = config("DOMAIN", default="localhost")

# === Email settings ===
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="contact@sogentis.org")
CONTACT_EMAIL = config("CONTACT_EMAIL", default="admin@sogentis.org")

EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# === Autres intégrations tierces ===
# Exemples :
# - Sentry
# - AWS S3
# - Firebase
# - Mailgun
# - SendGrid

# Tu peux continuer à étendre ce fichier proprement avec d'autres services
