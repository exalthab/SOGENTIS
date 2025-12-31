# economic/services/models/service_category.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from parler.models import TranslatableModel, TranslatedFields


class ServiceCategory(TranslatableModel):
    """
    Catégorie de service (translatable via Django-Parler).
    """

    # ===============================
    # CHAMPS TRADUITS
    # ===============================
    translations = TranslatedFields(
        name=models.CharField(
            max_length=150,
            verbose_name=_("Nom"),
        ),
        description=models.TextField(
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

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
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
        verbose_name = _("Catégorie de service")
        verbose_name_plural = _("Catégories de services")
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True) or f"ServiceCategory #{self.pk}"







# # economic/services/models/service_category.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from parler.models import TranslatableModel, TranslatedFields


# class ServiceCategory(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=150,
#             verbose_name=_("Nom"),
#         ),
#         description=models.TextField(
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

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Active"),
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
#         verbose_name = _("Catégorie de service")
#         verbose_name_plural = _("Catégories de services")
#         ordering = ["-created_at", "-id"]  # ✅ plus d'erreur sur 'name'

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or f"ServiceCategory #{self.pk}"





# # economic/services/models/service_category.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class ServiceCategory(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=150,
#             verbose_name=_("Nom"),
#         ),
#     )

#     slug = models.SlugField(
#         max_length=200,
#         unique=True,
#         verbose_name=_("Slug"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Active"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mise à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Catégorie de service")
#         verbose_name_plural = _("Catégories de services")
#         # ⚠️ PAS "name" (n’existe pas en base)
#         ordering = ("slug",)

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or self.slug
