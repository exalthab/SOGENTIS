# sogentis_apps/economic/ecommerce/models/vendor.py

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Vendor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor",          # 🔑 simple, unique, sans clash
        verbose_name=_("Utilisateur"),
    )

    company_name = models.CharField(
        max_length=255,
        verbose_name=_("Nom de l’entreprise"),
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Vérifié"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créé le"),
    )

    class Meta:
        verbose_name = _("Vendeur")
        verbose_name_plural = _("Vendeurs")

    def __str__(self):
        return self.company_name
