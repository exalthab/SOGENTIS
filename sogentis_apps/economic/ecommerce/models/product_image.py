# economic/ecommerce/models/product_image.py
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _


class ProductImage(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Produit"),
    )

    image = models.ImageField(
        upload_to="products/%Y/%m/",
        verbose_name=_("Image"),
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Texte alternatif"),
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name=_("Image principale"),
        db_index=True,
    )

    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Ordre"),
        help_text=_("Plus petit = affiché en premier."),
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Image du produit")
        verbose_name_plural = _("Images du produit")
        ordering = ["-is_main", "sort_order", "id"]
        indexes = [
            models.Index(fields=["product", "-is_main", "sort_order"]),
        ]
        constraints = [
            # ✅ Une seule image principale par produit (Postgres)
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(is_main=True),
                name="uniq_product_main_image",
            )
        ]

    def __str__(self) -> str:
        return f"Image — {self.product}#{self.pk}"

    def clean(self):
        super().clean()

        # Auto alt_text (utile SEO/accessibilité)
        if not self.alt_text and self.product_id:
            name = self.product.safe_translation_getter("name", any_language=True) or ""
            self.alt_text = name[:255]

        # Si on marque cette image comme principale, on empêche une 2e principale
        # (garde la validation, même si on auto-corrige en save)
        if self.is_main and self.product_id:
            qs = self.__class__.objects.filter(product_id=self.product_id, is_main=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError({"is_main": _("Ce produit a déjà une image principale.")})

    def save(self, *args, **kwargs):
        # Sécurise au cas où clean() n’est pas appelé (admin safe)
        self.full_clean()

        # Comportement prod: si is_main => rendre les autres images non principales
        with transaction.atomic():
            if self.is_main and self.product_id:
                # affichage stable: l'image principale en premier
                if self.sort_order != 0:
                    self.sort_order = 0

                self.__class__.objects.filter(
                    product_id=self.product_id,
                    is_main=True,
                ).exclude(pk=self.pk).update(is_main=False)

            super().save(*args, **kwargs)





# # economic/ecommerce/models/product_image.py
# from __future__ import annotations

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class ProductImage(models.Model):
#     product = models.ForeignKey(
#         "Product",
#         on_delete=models.CASCADE,
#         related_name="images",
#         verbose_name=_("Produit"),
#     )

#     image = models.ImageField(
#         upload_to="products/%Y/%m/",
#         verbose_name=_("Image"),
#     )

#     alt_text = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name=_("Texte alternatif"),
#     )

#     is_main = models.BooleanField(
#         default=False,
#         verbose_name=_("Image principale"),
#         db_index=True,
#     )

#     sort_order = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Ordre"),
#         help_text=_("Plus petit = affiché en premier."),
#         db_index=True,
#     )

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     class Meta:
#         verbose_name = _("Image du produit")
#         verbose_name_plural = _("Images du produit")
#         ordering = ["-is_main", "sort_order", "id"]
#         indexes = [
#             models.Index(fields=["product", "-is_main", "sort_order"]),
#         ]
#         constraints = [
#             # ✅ Une seule image principale par produit (Postgres)
#             models.UniqueConstraint(
#                 fields=["product"],
#                 condition=models.Q(is_main=True),
#                 name="uniq_product_main_image",
#             )
#         ]

#     def __str__(self) -> str:
#         return f"Image — {self.product}#{self.pk}"

#     def clean(self):
#         super().clean()
#         # Si on marque cette image comme principale, on empêche une 2e principale
#         if self.is_main and self.product_id:
#             qs = ProductImage.objects.filter(product_id=self.product_id, is_main=True)
#             if self.pk:
#                 qs = qs.exclude(pk=self.pk)
#             if qs.exists():
#                 raise ValidationError({"is_main": _("Ce produit a déjà une image principale.")})

#     def save(self, *args, **kwargs):
#         # Sécurise au cas où clean() n’est pas appelé (admin safe)
#         self.full_clean()
#         super().save(*args, **kwargs)





# # economic/ecommerce/models/product_image.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .product import Product


# class ProductImage(models.Model):
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="images",
#         verbose_name=_("Produit"),
#     )

#     image = models.ImageField(
#         upload_to="products/",
#         verbose_name=_("Image"),
#     )

#     alt_text = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name=_("Texte alternatif"),
#     )

#     is_main = models.BooleanField(
#         default=False,
#         verbose_name=_("Image principale"),
#     )

#     class Meta:
#         verbose_name = _("Image du produit")
#         verbose_name_plural = _("Images du produit")
#         ordering = ["-is_main", "id"]

#     def __str__(self):
#         return f"Image – {self.product}"
