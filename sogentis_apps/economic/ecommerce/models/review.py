# sogentis_apps/economic/ecommerce/models/review.py

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from .product import Product


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("Produit"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",          # 🔑 simple, sans clash
        verbose_name=_("Utilisateur"),
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_("Note"),
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Titre"),
    )

    content = CKEditor5Field(
        config_name="default",
        verbose_name=_("Commentaire"),
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Approuvé"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créé le"),
    )

    class Meta:
        verbose_name = _("Avis produit")
        verbose_name_plural = _("Avis produits")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_review_per_user_product",
            )
        ]

    def __str__(self):
        return f"{self.product} – {self.user} ({self.rating}/5)"
