# config/settings/modules/templates.py
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Active le cache des templates si DEBUG est False (par défaut en prod)
USE_TEMPLATE_CACHING = config("USE_TEMPLATE_CACHING", default=not config("DEBUG", cast=bool, default=True), cast=bool)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # Custom context processors
                "sogentis_apps.core.context_processors.global_context.theme_context",
                "sogentis_apps.core.context_processors.global_context.global_variables",
                "dashboard.context_processors.dashboard_context.dashboard_info",
                "sogentis_apps.core.context_processors.global_context.section_menu",
            ],
            **({
                "loaders": [
                    ("django.template.loaders.cached.Loader", [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ])
                ]
            } if USE_TEMPLATE_CACHING else {})
        },
    },
]
