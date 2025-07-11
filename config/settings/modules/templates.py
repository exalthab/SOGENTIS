from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sogentis_apps.core.context_processors.global_context.theme_context",
                "sogentis_apps.core.context_processors.global_context.global_variables",
                "dashboard.context_processors.dashboard_context.dashboard_info",
                "sogentis_apps.core.context_processors.global_context.section_menu",

            ],
        },
    },
]
