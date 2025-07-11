# config/settings/modules/authentication.py

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_USER_MODEL = "accounts_users.CustomUser"
