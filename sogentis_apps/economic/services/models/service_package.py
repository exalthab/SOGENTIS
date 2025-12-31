# economic/services/models/service_package.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field

from .service import Service


class ServicePackage(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(
            max_length=200,
            verbose_name=_("Nom du pack"),
        ),
        description=CKEditor5Field(
            blank=True,
            verbose_name=_("Description"),
        ),
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
    )

    services = models.ManyToManyField(
        Service,
        related_name="packages",
        blank=True,
        verbose_name=_("Services inclus"),
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Prix total"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif"),
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("Créé le"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Mis à jour le"),
    )

    class Meta:
        verbose_name = _("Pack de services")
        verbose_name_plural = _("Packs de services")
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"Pack #{self.pk}"






# # economic/services/models/service_package.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .service import Service


# class ServicePackage(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=255,
#             verbose_name=_("Nom du pack"),
#         ),
#         description=CKEditor5Field(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     slug = models.SlugField(
#         max_length=255,
#         unique=True,
#         verbose_name=_("Slug"),
#     )

#     services = models.ManyToManyField(
#         Service,
#         related_name="packages",
#         blank=True,
#         verbose_name=_("Services inclus"),
#     )

#     total_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=0,
#         verbose_name=_("Prix du pack"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Pack de services")
#         verbose_name_plural = _("Packs de services")
#         ordering = ["slug", "id"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)
