# /economic/ecommerce/models/category.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
        verbose_name=_("Catégorie parente"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordre"),
    )

    translations = TranslatedFields(
        name=models.CharField(
            max_length=200,
            verbose_name=_("Nom"),
        ),
        slug=models.SlugField(
            max_length=220,
            blank=True,
            db_index=True,
            verbose_name=_("Slug"),
        ),
        description=models.TextField(
            blank=True,
            verbose_name=_("Description"),
        ),
    )

    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ["order", "id"]

    def __str__(self):
        return self.safe_translation_getter("name", any_language=True)

    def save(self, *args, **kwargs):
        # 1️⃣ On sauvegarde d'abord la catégorie pour avoir un PK
        super().save(*args, **kwargs)

        # 2️⃣ Ensuite seulement on manipule les traductions
        # (sinon self.translations.all() plante sur un objet sans pk)
        if not self.pk:
            return

        # Génération du slug par langue (django-parler safe)
        for translation in self.translations.all():
            if not translation.slug and translation.name:
                translation.slug = slugify(translation.name)
                translation.save()







# # /economic/ecommerce/models/category.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils.text import slugify
# from parler.models import TranslatableModel, TranslatedFields


# class Category(TranslatableModel):
#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         related_name="children",
#         on_delete=models.SET_NULL,
#         verbose_name=_("Catégorie parente"),
#     )

#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Active"),
#     )

#     order = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Ordre"),
#     )

#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=200,
#             verbose_name=_("Nom"),
#         ),
#         slug=models.SlugField(
#             max_length=220,
#             blank=True,
#             db_index=True,
#             verbose_name=_("Slug"),
#         ),
#         description=models.TextField(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     class Meta:
#         verbose_name = _("Catégorie")
#         verbose_name_plural = _("Catégories")
#         ordering = ["order", "id"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)

#     def save(self, *args, **kwargs):
#         # Génération du slug par langue (django-parler safe)
#         for translation in self.translations.all():
#             if not translation.slug and translation.name:
#                 translation.slug = slugify(translation.name)

#         super().save(*args, **kwargs)
