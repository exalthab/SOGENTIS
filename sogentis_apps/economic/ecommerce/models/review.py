# /economic/ecommerce/models/review.py
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
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
        related_name="reviews",
        verbose_name=_("Utilisateur"),
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name=_("Note"),
        db_index=True,
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Titre"),
    )

    content = CKEditor5Field(
        config_name="default",
        verbose_name=_("Commentaire"),
    )

    # ✅ Soft display control (prod)
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Actif"),
        help_text=_("Désactiver pour masquer sans supprimer."),
    )

    # ✅ Modération
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Approuvé"),
        db_index=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approuvé le"),
    )

    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_reviews",
        verbose_name=_("Modéré par"),
    )

    moderation_note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Note de modération"),
        help_text=_("Optionnel: raison du refus/suppression."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créé le"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Mis à jour le"),
    )

    class Meta:
        verbose_name = _("Avis produit")
        verbose_name_plural = _("Avis produits")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "is_active", "is_approved"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["rating", "created_at"]),
        ]
        constraints = [
            # ✅ DB safety: note ∈ [1..5]
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="chk_review_rating_1_5",
            ),
            # ✅ Soft-delete compatible: un seul avis ACTIF par (product,user)
            models.UniqueConstraint(
                fields=["product", "user"],
                condition=Q(is_active=True),
                name="unique_active_review_per_user_product",
            ),
        ]

    def __str__(self):
        return f"{self.product} – {self.user} ({self.rating}/5)"

    def clean(self):
        super().clean()

        try:
            r = int(self.rating or 0)
        except Exception:
            r = 0
        if not (1 <= r <= 5):
            raise ValidationError({"rating": _("La note doit être entre 1 et 5.")})

        if self.title:
            self.title = " ".join(self.title.strip().split())

        if self.moderation_note:
            self.moderation_note = " ".join(self.moderation_note.strip().split())

        # cohérence soft delete
        if not self.is_active:
            self.is_approved = False
            self.approved_at = None

        # cohérence approval
        if self.is_approved and not self.is_active:
            raise ValidationError({"is_approved": _("Un avis inactif ne peut pas être approuvé.")})

    def save(self, *args, **kwargs):
        # timestamps modération cohérents
        if self.is_approved:
            if self.approved_at is None:
                self.approved_at = timezone.now()
            # si approuvé, pas de note de refus
            self.moderation_note = ""
        else:
            self.approved_at = None

        # si désactivé => désapprouvé (sécurité)
        if not self.is_active:
            self.is_approved = False
            self.approved_at = None

        self.full_clean()
        super().save(*args, **kwargs)

    # Helpers modération
    def approve(self, moderator=None):
        self.is_active = True
        self.is_approved = True
        self.moderated_by = moderator
        self.moderation_note = ""
        self.approved_at = timezone.now()
        self.save(update_fields=["is_active", "is_approved", "moderated_by", "moderation_note", "approved_at", "updated_at"])

    def reject(self, moderator=None, note: str = ""):
        self.is_approved = False
        self.moderated_by = moderator
        self.moderation_note = (note or "").strip()
        self.approved_at = None
        self.save(update_fields=["is_approved", "moderated_by", "moderation_note", "approved_at", "updated_at"])






# # /economic/ecommerce/models/review.py
# from __future__ import annotations

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _
# from django_ckeditor_5.fields import CKEditor5Field

# from .product import Product


# class Review(models.Model):
#     RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="reviews",
#         verbose_name=_("Produit"),
#     )

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="reviews",  # 🔑 simple, sans clash
#         verbose_name=_("Utilisateur"),
#     )

#     rating = models.PositiveSmallIntegerField(
#         choices=RATING_CHOICES,
#         verbose_name=_("Note"),
#         db_index=True,
#     )

#     title = models.CharField(
#         max_length=255,
#         verbose_name=_("Titre"),
#     )

#     content = CKEditor5Field(
#         config_name="default",
#         verbose_name=_("Commentaire"),
#     )

#     # ✅ Soft display control (prod)
#     is_active = models.BooleanField(
#         default=True,
#         db_index=True,
#         verbose_name=_("Actif"),
#         help_text=_("Désactiver pour masquer sans supprimer."),
#     )

#     # ✅ Modération
#     is_approved = models.BooleanField(
#         default=False,
#         verbose_name=_("Approuvé"),
#         db_index=True,
#     )

#     approved_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Approuvé le"),
#     )

#     moderated_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="moderated_reviews",
#         verbose_name=_("Modéré par"),
#     )

#     moderation_note = models.CharField(
#         max_length=255,
#         blank=True,
#         verbose_name=_("Note de modération"),
#         help_text=_("Optionnel: raison du refus/suppression."),
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
#         verbose_name = _("Avis produit")
#         verbose_name_plural = _("Avis produits")
#         ordering = ["-created_at"]
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["product", "user"],
#                 name="unique_review_per_user_product",
#             )
#         ]
#         indexes = [
#             models.Index(fields=["product", "is_active", "is_approved"]),
#             models.Index(fields=["user", "created_at"]),
#             models.Index(fields=["rating", "created_at"]),
#         ]

#     def __str__(self):
#         return f"{self.product} – {self.user} ({self.rating}/5)"

#     def clean(self):
#         super().clean()
#         if not (1 <= int(self.rating or 0) <= 5):
#             raise ValidationError({"rating": _("La note doit être entre 1 et 5.")})

#         if self.title:
#             self.title = self.title.strip()

#     def save(self, *args, **kwargs):
#         # timestamps modération cohérents
#         if self.is_approved and self.approved_at is None:
#             self.approved_at = timezone.now()
#         if not self.is_approved:
#             # si on désapprouve, on peut nettoyer approved_at
#             # (optionnel, mais cohérent)
#             self.approved_at = None

#         self.full_clean()
#         super().save(*args, **kwargs)

#     # Helpers modération
#     def approve(self, moderator=None):
#         self.is_approved = True
#         self.moderated_by = moderator
#         self.moderation_note = ""
#         self.approved_at = timezone.now()
#         self.save(update_fields=["is_approved", "moderated_by", "moderation_note", "approved_at", "updated_at"])

#     def reject(self, moderator=None, note: str = ""):
#         self.is_approved = False
#         self.moderated_by = moderator
#         self.moderation_note = (note or "").strip()
#         self.approved_at = None
#         self.save(update_fields=["is_approved", "moderated_by", "moderation_note", "approved_at", "updated_at"])






# # /economic/ecommerce/models/review.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django_ckeditor_5.fields import CKEditor5Field

# from .product import Product


# class Review(models.Model):
#     RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name="reviews",
#         verbose_name=_("Produit"),
#     )

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="reviews",          # 🔑 simple, sans clash
#         verbose_name=_("Utilisateur"),
#     )

#     rating = models.PositiveSmallIntegerField(
#         choices=RATING_CHOICES,
#         verbose_name=_("Note"),
#     )

#     title = models.CharField(
#         max_length=255,
#         verbose_name=_("Titre"),
#     )

#     content = CKEditor5Field(
#         config_name="default",
#         verbose_name=_("Commentaire"),
#     )

#     is_approved = models.BooleanField(
#         default=False,
#         verbose_name=_("Approuvé"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     class Meta:
#         verbose_name = _("Avis produit")
#         verbose_name_plural = _("Avis produits")
#         ordering = ["-created_at"]
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["product", "user"],
#                 name="unique_review_per_user_product",
#             )
#         ]

#     def __str__(self):
#         return f"{self.product} – {self.user} ({self.rating}/5)"
