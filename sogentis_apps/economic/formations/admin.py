# economic/formations/admin.py
from django.contrib import admin  # noqa: F401

from .admin.course_admin import *       # noqa
from .admin.module_admin import *       # noqa
from .admin.enrollment_admin import *   # noqa

# ✅ à ajouter quand tu crées ces fichiers
from .admin.lesson_admin import *       # noqa
from .admin.session_admin import *      # noqa
from .admin.certificate_admin import *  # noqa
from .admin.category_admin import *     # noqa




# # economic/formations/admin.py
# from django.contrib import admin
# from .admin.course_admin import *   # noqa
# from .admin.module_admin import *   # noqa
# from .admin.enrollment_admin import *  # noqa
