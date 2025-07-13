# config/settings/modules/authentication.py

# Backend d’authentification par défaut de Django
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = "accounts_users.CustomUser"
