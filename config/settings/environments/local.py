# #config/settings/environments/local.py
from decouple import config
from config.settings.modules.logging import *

# === DEBUG ===
DEBUG = config('DEBUG', default=True, cast=bool)

# === EMAIL CONFIGURATION (console backend for local dev) ===
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
DOMAIN_REDIRECT_ROOT = False
SECURE_SSL_REDIRECT = False
