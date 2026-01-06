# config/settings/templates/middleware.py
from pathlib import Path
from decouple import config

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment
DEBUG = config("DEBUG", cast=bool, default=False)
USE_TEMPLATE_CACHING = config(
    "USE_TEMPLATE_CACHING",
    cast=bool,
    default=not DEBUG,
)

# Context processors communs
BASE_CONTEXT_PROCESSORS = [
    "django.template.context_processors.request",
    "django.template.context_processors.i18n",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",

    # Custom global context
    "core.context_processors.global_context.theme_context",
    "core.context_processors.global_context.global_variables",
    "core.context_processors.global_context.section_menu",
    "core.context_processors.global_context.seo_context",
    "core.context_processors.global_context.social_links",
    "core.context_processors.global_context.site_domains",

    # Dashboard
    "dashboard.context_processors.dashboard_context.dashboard_info",
    "dashboard.context_processors.dashboard_context.dashboard_roles",

    # Economic / Ecommerce
    "economic.context_processors.context_processors.economic_context",
    "economic.ecommerce.context_processors.ecommerce_context",
    "economic.ecommerce.context_processors.ecommerce_counts",
]

# Debug context uniquement en DEV
if DEBUG:
    BASE_CONTEXT_PROCESSORS.insert(
        0, "django.template.context_processors.debug"
    )

# Templates
if USE_TEMPLATE_CACHING:
    # PROD / cache activé
    TEMPLATES = [{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                ),
            ],
            "context_processors": BASE_CONTEXT_PROCESSORS,
        },
    }]
else:
    # DEV / local
    TEMPLATES = [{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": BASE_CONTEXT_PROCESSORS,
        },
    }]






# # config/settings/modules/templates.py
# from pathlib import Path
# from decouple import config

# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# DEBUG = config("DEBUG", cast=bool, default=True)
# USE_TEMPLATE_CACHING = config("USE_TEMPLATE_CACHING", cast=bool, default=not DEBUG)

# # 👇 Options partagées (modulaire)
# BASE_CONTEXT_PROCESSORS = [
#     "django.template.context_processors.debug",
#     "django.template.context_processors.request",
#     "django.template.context_processors.i18n",
#     "django.contrib.auth.context_processors.auth",
#     "django.contrib.messages.context_processors.messages",
#     # custom
#     "core.context_processors.global_context.theme_context",
#     "core.context_processors.global_context.global_variables",
#     "core.context_processors.global_context.section_menu",
#     "core.context_processors.global_context.seo_context",
#     "core.context_processors.global_context.social_links",
#     "dashboard.context_processors.dashboard_context.dashboard_info",
#     "dashboard.context_processors.dashboard_context.dashboard_roles",
#     # "economic.context_processors.economic_context",
#     "economic.context_processors.context_processors.economic_context",
#     # "economic.context_processors.commerce.commerce_mode",
#     "economic.ecommerce.context_processors.ecommerce_context",
#     "economic.ecommerce.context_processors.ecommerce_counts",

# ]

# if USE_TEMPLATE_CACHING:
#     # PROD (ou quand tu veux du cache) → pas d’APP_DIRS, loaders explicites
#     TEMPLATES = [{
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": False,
#         "OPTIONS": {
#             "loaders": [
#                 ("django.template.loaders.cached.Loader", [
#                     "django.template.loaders.filesystem.Loader",
#                     "django.template.loaders.app_directories.Loader",  # ← charge les templates des apps
#                 ])
#             ],
#             "context_processors": BASE_CONTEXT_PROCESSORS,
#         },
#     }]
# else:
#     # DEV / LOCAL → simple et identique à VSCode
#     TEMPLATES = [{
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": True,  # ← comme chez toi en local
#         "OPTIONS": {
#             "context_processors": BASE_CONTEXT_PROCESSORS,
#         },
#     }]





# # config/settings/modules/templates.py
# from pathlib import Path
# from decouple import config

# BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# # Active le cache des templates si DEBUG est False (par défaut en prod)
# USE_TEMPLATE_CACHING = config("USE_TEMPLATE_CACHING", default=not config("DEBUG", cast=bool, default=True), cast=bool)

# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": False,  # Doit être False si on utilise des loaders personnalisés
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.debug",
#                 "django.template.context_processors.request",
#                 "django.template.context_processors.i18n",   # <= présent par défaut en général

#                 "django.contrib.auth.context_processors.auth",
#                 "django.contrib.messages.context_processors.messages",

#                 # Custom context processors
#                 "core.context_processors.global_context.theme_context",
#                 "core.context_processors.global_context.global_variables",
#                 "core.context_processors.global_context.section_menu",
#                 "core.context_processors.global_context.seo_context",
#                 "core.context_processors.global_context.social_links",

#                 # Si dashboard doit rester dans une autre app :
#                 "dashboard.context_processors.dashboard_context.dashboard_info",

#             ],
#             **({
#                 "loaders": [
#                     ("django.template.loaders.cached.Loader", [
#                         "django.template.loaders.filesystem.Loader",
#                         "django.template.loaders.app_directories.Loader",
#                     ])
#                 ]
#             } if USE_TEMPLATE_CACHING else {})
#         },
#     },
# ]
