# economic/services/admin.py
from django.contrib import admin

from .admin import *  # noqa

admin.site.site_header = "SOGENTIS — Admin Économique"
admin.site.site_title = "SOGENTIS Admin"
admin.site.index_title = "Gestion des services"
