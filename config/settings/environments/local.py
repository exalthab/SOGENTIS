# #config/settings/environments/local.py
from decouple import config

# === DEBUG ===
DEBUG = config('DEBUG', default=True, cast=bool)

# === EMAIL CONFIGURATION (console backend for local dev) ===
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# === DEVELOPMENT LOGGING LEVEL ===
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

LOGGING['root']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'

# === CORS & CSRF (optionnel si tu fais du front en local sur un autre port) ===
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
