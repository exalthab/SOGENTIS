from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InstitutionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "institution"
    verbose_name = _("Pôle Institutionnel / Local")
