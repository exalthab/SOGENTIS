# economic/services/models/service.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from parler.models import TranslatableModel, TranslatedFields


class Service(TranslatableModel):
    """
    Modèle de service avec champs traduisibles via Django-Parler.
    """

    # ===============================
    # CHAMPS TRADUITS
    # ===============================
    translations = TranslatedFields(
        title=models.CharField(
            max_length=255,
            verbose_name=_("Titre"),
        ),
        short_description=models.CharField(
            max_length=300,
            blank=True,
            verbose_name=_("Résumé"),
        ),
        description=CKEditor5Field(
            blank=True,
            verbose_name=_("Description"),
        ),
    )

    # ===============================
    # CHAMPS PARTAGÉS (NON TRADUITS)
    # ===============================
    slug = models.SlugField(
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Slug"),
    )

    # 🔗 Lien vers ServiceCategory dans la même app
    category = models.ForeignKey(
        "ServiceCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
        verbose_name=_("Catégorie"),
    )

    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Prix de base"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif"),
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Mis en avant"),
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
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or f"Service #{self.pk}"








# # economic/services/models/service.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django_ckeditor_5.fields import CKEditor5Field
# from parler.models import TranslatableModel, TranslatedFields


# class Service(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(
#             max_length=255,
#             verbose_name=_("Titre"),
#         ),
#         short_description=models.CharField(
#             max_length=300,
#             blank=True,
#             verbose_name=_("Résumé"),
#         ),
#         description=CKEditor5Field(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     slug = models.SlugField(
#         unique=True,
#         blank=True,
#         null=True,
#         verbose_name=_("Slug"),
#     )

#     category = models.ForeignKey(
#         "services.ServiceCategory",  # ✅ STRING REFERENCE
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="services",
#         verbose_name=_("Catégorie"),
#     )

#     base_price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         default=0,
#         verbose_name=_("Prix de base"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     is_featured = models.BooleanField(
#         default=False,
#         verbose_name=_("Mis en avant"),
#     )

#     created_at = models.DateTimeField(
#         default=timezone.now,
#         editable=False,
#         verbose_name=_("Créé le"),
#     )
#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mis à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Service")
#         verbose_name_plural = _("Services")
#         ordering = ["-created_at", "-id"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or f"Service #{self.pk}"








# # economic/services/models/service.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .service_category import ServiceCategory


# class Service(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(
#             max_length=255,
#             verbose_name=_("Titre"),
#         ),
#         short_description=models.CharField(
#             max_length=255,
#             blank=True,
#             verbose_name=_("Résumé"),
#         ),
#         description=CKEditor5Field(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     slug = models.SlugField(
#         max_length=200,
#         unique=True,
#         verbose_name=_("Slug"),
#     )

#     category = models.ForeignKey(
#         ServiceCategory,
#         on_delete=models.SET_NULL,
#         related_name="services",
#         null=True,
#         blank=True,
#         verbose_name=_("Catégorie"),
#     )

#     base_price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         verbose_name=_("Prix de base"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )

#     is_featured = models.BooleanField(
#         default=False,
#         verbose_name=_("Mis en avant"),
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
#         verbose_name = _("Service")
#         verbose_name_plural = _("Services")
#         ordering = ("-created_at", "-id")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or self.slug
