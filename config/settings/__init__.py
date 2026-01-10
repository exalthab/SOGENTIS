# config/settings/modules/__init__.py
"""
Settings loader (modules).
L'ordre compte. On charge d'abord le socle (base), puis le reste.
Les overrides d'environnement viennent en dernier.
"""

from decouple import config

ENV = config("DJANGO_ENV", default="prod").lower().strip()

# ==========================
# Core (socle en premier)
# ==========================
from .modules.base import *
from .modules.database import *

# ==========================
# Django structure
# ==========================
from .modules.apps import *
from .modules.middleware import *
from .modules.templates import *
from .modules.static import *
from .modules.internationalization import *
from .modules.authentication import *

# ==========================
# Features & integrations
# ==========================
from .modules.ckeditor import *
from .modules.third_party import *     # hCaptcha est ici maintenant
from .modules.email import *           # si tu veux que email.py "gagne", mets-le après third_party
from .modules.antispam import *
from .modules.security import *
from .modules.logging import *
from .modules.celery import *

# ==========================
# Overrides par environnement (TOUJOURS À LA FIN)
# ==========================
if ENV in ("dev", "development"):
    from .environments.dev import *
elif ENV in ("local",):
    from .environments.local import *
else:  # prod / production
    from .environments.production import *






# # config/settings/__init__.py
# from decouple import config

# ENV = config("DJANGO_ENV", default="prod").lower().strip()
# """
# Settings loader (modules).
# L'ordre compte: base -> apps -> templates -> static -> email -> security -> logging, etc.
# """
# from .modules.antispam import *
# from .modules.apps import *
# from .modules.authentication import *
# from .modules.base import *
# from .modules.celery import *
# from .modules.ckeditor import *
# from .modules.database import *
# from .modules.email import *
# from .modules.internationalization import *
# from .modules.logging import *
# from .modules.middleware import *
# from .modules.security import *
# from .modules.static import *
# from .modules.templates import *
# from .modules.third_party import *


# # overrides par environnement
# if ENV in ("dev", "local"):
#     from .environments.dev import *
# elif ENV in ("local",):
#     from .environments.local import *
# else:
#     from .environments.production import *