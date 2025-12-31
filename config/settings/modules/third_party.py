# config/settings/modules/third_party.py

from decouple import config

# === Stripe Configuration ===
STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY", default="")
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET", default="")

# PayPal
PAYPAL_CLIENT_ID = config("PAYPAL_CLIENT_ID", default="")
PAYPAL_SECRET = config("PAYPAL_SECRET", default="")
PAYPAL_BASE_URL = config("PAYPAL_BASE_URL", default="https://api-m.sandbox.paypal.com")
# === Project Domain ===
DOMAIN = config("DOMAIN", default="localhost")

# === Email Configuration ===
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend"
)

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@sogentis.org")
CONTACT_EMAIL = config("CONTACT_EMAIL", default="admin@sogentis.org")

EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", cast=bool, default=False)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# === Sentry Configuration ===
SENTRY_DSN = config("SENTRY_DSN", default="")

# === AWS S3 (si utilisé) ===
USE_S3 = config("USE_S3", default=False, cast=bool)
if USE_S3:
    AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
    AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
    AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_QUERYSTRING_AUTH = config("AWS_QUERYSTRING_AUTH", cast=bool, default=False)


# ==============================
# reCAPTCHA v3 Settings
# ==============================

# Google reCAPTCHA v3 site key (public)
RECAPTCHA_PUBLIC_KEY = "your-google-site-key"

# Google reCAPTCHA v3 secret key (private)
RECAPTCHA_PRIVATE_KEY = "your-google-secret-key"

# Minimum score threshold for v3 validation (0.0 – 1.0)
# 0.85 is usually a good balance between security and usability
RECAPTCHA_REQUIRED_SCORE = 0.85

# Optional: to log errors during captcha validation
# Useful for debugging in development
# (Requires setting up logging)
RECAPTCHA_PROXY = None  # e.g., 'http://proxyserver:port' if behind a proxy

# === Firebase (optionnel) ===
# FIREBASE_API_KEY = config("FIREBASE_API_KEY", default="")

# === Mailgun / SendGrid (optionnel) ===
# MAILGUN_API_KEY = config("MAILGUN_API_KEY", default="")
# SENDGRID_API_KEY = config("SENDGRID_API_KEY", default="")

# Tu peux continuer à ajouter ici toute nouvelle intégration
