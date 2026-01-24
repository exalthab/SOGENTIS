# /economic/ecommerce/models/product.py
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Product(TranslatableModel):
    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Catégorie"),
    )

    vendor = models.ForeignKey(
        "Vendor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Vendeur"),
    )

    sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU"))

    # ✅ Prix “rapide” (affichage). En prod, tu peux le garder comme fallback si pas de ProductPricing.
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Prix"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))

    is_active = models.BooleanField(default=True, verbose_name=_("Actif"), db_index=True)
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"), db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name=_("Nom")),
        slug=models.SlugField(max_length=260, blank=True, db_index=True, verbose_name=_("Slug")),
        short_description=models.CharField(max_length=500, blank=True, verbose_name=_("Description courte")),
        description=models.TextField(blank=True, verbose_name=_("Description")),
        seo_title=models.CharField(max_length=255, blank=True, verbose_name=_("Titre SEO")),
        seo_description=models.CharField(max_length=300, blank=True, verbose_name=_("Description SEO")),
    )

    class TranslatedMeta:
        unique_together = (("language_code", "slug"),)
        indexes = (models.Index(fields=("language_code", "slug")),)

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "is_featured", "-created_at"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["vendor", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or f"Product #{self.pk}"

    def clean(self):
        super().clean()
        if self.price is None:
            raise ValidationError({"price": _("Le prix est obligatoire.")})

    @property
    def main_image(self):
        # image principale si existe, sinon la première
        img = self.images.filter(is_main=True).first()
        return img or self.images.order_by("sort_order", "id").first()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_translation_slugs()

    def _ensure_translation_slugs(self):
        Translation = self.translations.model
        qs = Translation.objects.filter(master_id=self.pk)

        to_update = []
        for tr in qs:
            if tr.slug or not tr.name:
                continue

            base = slugify(tr.name)[:260] or f"product-{self.pk}"
            slug = base
            n = 2
            while Translation.objects.filter(
                language_code=tr.language_code,
                slug=slug,
            ).exclude(master_id=self.pk).exists():
                suffix = f"-{n}"
                slug = f"{base[: max(1, 260 - len(suffix))]}{suffix}"
                n += 1

            tr.slug = slug
            to_update.append(tr)

        if to_update:
            Translation.objects.bulk_update(to_update, ["slug"])





# # /economic/ecommerce/models/product.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils.text import slugify
# from parler.models import TranslatableModel, TranslatedFields

# from .category import Category
# from .vendor import Vendor


# class Product(TranslatableModel):
#     category = models.ForeignKey(
#         Category,
#         on_delete=models.PROTECT,
#         related_name="products",
#         verbose_name=_("Catégorie"),
#     )

#     vendor = models.ForeignKey(
#         Vendor,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="products",
#         verbose_name=_("Vendeur"),
#     )

#     sku = models.CharField(
#         max_length=100,
#         unique=True,
#         verbose_name=_("SKU"),
#     )

#     price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Prix"),
#     )

#     stock = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Stock"),
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

#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=255,
#             verbose_name=_("Nom"),
#         ),
#         slug=models.SlugField(
#             max_length=260,
#             blank=True,
#             db_index=True,
#             verbose_name=_("Slug"),
#         ),
#         short_description=models.CharField(
#             max_length=500,
#             blank=True,
#             verbose_name=_("Description courte"),
#         ),
#         description=models.TextField(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     class Meta:
#         verbose_name = _("Produit")
#         verbose_name_plural = _("Produits")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or f"Product #{self.pk}"

#     def save(self, *args, **kwargs):
#         """
#         IMPORTANT :
#         - On sauvegarde d’abord le Product pour qu’il ait un pk
#         - Ensuite seulement on manipule les traductions (Parler)
#         afin d’éviter :
#         "ValueError: 'Product' instance needs to have a primary key value
#         before this relationship can be used."
#         """
#         # 1️⃣ Sauvegarde principale : crée le PK si nouveau
#         super().save(*args, **kwargs)

#         # 2️⃣ Si, pour une raison quelconque, pas de pk -> on arrête là
#         if not self.pk:
#             return

#         # 3️⃣ Génération du slug pour chaque langue si manquant
#         for translation in self.translations.all():
#             if not translation.slug and translation.name:
#                 translation.slug = slugify(translation.name)
#                 translation.save()






# # /economic/ecommerce/models/product.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils.text import slugify
# from parler.models import TranslatableModel, TranslatedFields

# from .category import Category
# from .vendor import Vendor


# class Product(TranslatableModel):
#     category = models.ForeignKey(
#         Category,
#         on_delete=models.PROTECT,
#         related_name="products",
#         verbose_name=_("Catégorie"),
#     )

#     vendor = models.ForeignKey(
#         Vendor,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="products",
#         verbose_name=_("Vendeur"),
#     )

#     sku = models.CharField(
#         max_length=100,
#         unique=True,
#         verbose_name=_("SKU"),
#     )

#     price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Prix"),
#     )

#     stock = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Stock"),
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

#     translations = TranslatedFields(
#         name=models.CharField(
#             max_length=255,
#             verbose_name=_("Nom"),
#         ),
#         slug=models.SlugField(
#             max_length=260,
#             blank=True,
#             db_index=True,
#             verbose_name=_("Slug"),
#         ),
#         short_description=models.CharField(
#             max_length=500,
#             blank=True,
#             verbose_name=_("Description courte"),
#         ),
#         description=models.TextField(
#             blank=True,
#             verbose_name=_("Description"),
#         ),
#     )

#     class Meta:
#         verbose_name = _("Produit")
#         verbose_name_plural = _("Produits")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)

#     def save(self, *args, **kwargs):
#         # Génération du slug par langue (django-parler safe)
#         for translation in self.translations.all():
#             if not translation.slug and translation.name:
#                 translation.slug = slugify(translation.name)

#         super().save(*args, **kwargs)
