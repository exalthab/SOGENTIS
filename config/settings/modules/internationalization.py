# modules/internationalization.py
from pathlib import Path
from django.utils.translation import gettext_lazy as _
# IMPORTANT : pas d'import de base.py ici pour éviter les imports circulaires

# ============================================================
# 🧱 0) BASE_DIR (version indépendante)
#    On remonte jusqu'à la racine du projet (même niveau que manage.py)
# ============================================================
# Adapté à la structure :
#   <PROJECT_ROOT>/
#       manage.py
#       SOGENTIS/
#       config/settings/modules/internationalization.py
BASE_DIR = Path(__file__).resolve(strict=True).parents[3]


# ============================================================
# 🌍 1) Paramètres Parler (traductions des modèles)
# ============================================================
PARLER_LANGUAGES = {
    None: (
        {"code": "fr"},
        {"code": "en"},
    ),
    "default": {
        "fallbacks": ["fr"],   # si la traduction manque, fallback en FR
        "hide_untranslated": False,
    },
}


# ============================================================
# ⏰ 2) Réglages i18n / timezone
# ============================================================
LANGUAGE_CODE = "fr"
TIME_ZONE = "Africa/Dakar"

USE_I18N = True
USE_TZ = True


# ============================================================
# 🌐 3) Liste des langues actives
# ============================================================
LANGUAGES = [
    ("fr", _("Français")),
    ("en", _("Anglais")),
]


# ============================================================
# 📁 4) Fichiers de traduction (.po / .mo)
# ============================================================
# Ici on suppose que tes locales sont dans :
#   <PROJECT_ROOT>/SOGENTIS/locale/
LOCALE_PATHS = [
    (BASE_DIR / "SOGENTIS" / "locale").resolve()
]


# ============================================================
# 🍪 5) Cookies et persistance de la langue
# ============================================================
# ⚠️ Très important pour les tests en local :
# - en DEV (DEBUG=True, HTTP), le cookie ne doit PAS être "secure"
# - en PROD (HTTPS), tu pourras forcer SECURE=True dans les settings prod

try:
    from decouple import config
    DEBUG = config("DEBUG", default=False, cast=bool)
except Exception:
    DEBUG = False

LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # 1 an

# En dev (HTTP) => False, sinon le cookie n'est jamais posé
LANGUAGE_COOKIE_SECURE = not DEBUG

# Lax est souvent plus pratique que Strict
LANGUAGE_COOKIE_SAMESITE = "Lax"


# ============================================================
# 🧩 6) Rappel middleware requis dans settings/base.py
# ============================================================
# Dans config/settings/modules/base.py → MIDDLEWARE :
#
# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.locale.LocaleMiddleware",   # 👈 ICI
#     "django.middleware.common.CommonMiddleware",
#     ...
# ]
#
# Et dans TEMPLATES[0]["OPTIONS"]["context_processors"] :
#
#     "django.template.context_processors.i18n",
# ============================================================






# # modules/internationalization.py
# from pathlib import Path
# from django.utils.translation import gettext_lazy as _
# from django.conf.locale import LANG_INFO


# # ============================================================
# # 🌍 1) Paramètres Parler (traductions des modèles)
# # ============================================================
# PARLER_LANGUAGES = {
#     None: (
#         {'code': 'fr'},
#         {'code': 'en'},
#     ),
#     'default': {
#         'fallbacks': ['fr'],  # si la traduction manque, fallback en FR
#         'hide_untranslated': False,
#     }
# }


# # ============================================================
# # 🗣️ 2) Infos langues personnalisées
# # (👉 Supprimé car on ne garde que fr/en)
# # ============================================================


# # ============================================================
# # ⏰ 3) Réglages i18n / timezone
# # ============================================================
# LANGUAGE_CODE = "fr"
# TIME_ZONE = "Africa/Dakar"

# USE_I18N = True
# USE_TZ = True


# # ============================================================
# # 🌐 4) Liste complète des langues activées sur le site
# # ============================================================
# LANGUAGES = [
#     ('fr', _('Français')),
#     ('en', _('Anglais')),
# ]


# # ============================================================
# # 📁 5) Fichiers de traduction (.po / .mo)
# # ============================================================
# try:
#     from .base import BASE_DIR  # si settings modulaires
# except Exception:
#     BASE_DIR = Path(__file__).resolve().parents[3]

# # chemin principal pour les fichiers de traduction
# LOCALE_PATHS = [
#     (BASE_DIR / "SOGENTIS" / "locale").resolve()
# ]


# # ============================================================
# # 🍪 6) Cookies et persistance de la langue
# # ============================================================
# LANGUAGE_COOKIE_NAME = "django_language"
# LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365   # 1 an
# # LANGUAGE_COOKIE_SAMESITE = "Lax"
# LANGUAGE_COOKIE_SECURE = True # en PROD (HTTPS) .= False en DEV
# LANGUAGE_COOKIE_SAMESITE = "Strict"


# # ============================================================
# # 🧩 7) Middleware requis dans settings/base.py
# # ============================================================
# # Assurer :
# #
# # 'django.middleware.locale.LocaleMiddleware',
# #
# # Et dans les context_processors :
# # 'django.template.context_processors.i18n',
# # ============================================================


