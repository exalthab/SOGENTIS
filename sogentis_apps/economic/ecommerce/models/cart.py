# economic/ecommerce/models/cart.py
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("Utilisateur"),
        null=True,
        blank=True,
    )

    session_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name=_("Clé session"),
        help_text=_("Pour les paniers invités (si user est vide)."),
    )

    currency = models.CharField(
        max_length=5,
        default="XOF",
        db_index=True,
        verbose_name=_("Devise"),
        help_text=_("Ex: XOF, EUR, USD"),
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Actif"),
        help_text=_("Désactiver un panier sans le supprimer."),
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expire le"),
        help_text=_("Optionnel : permet de purger les paniers inactifs."),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    class Meta:
        verbose_name = _("Panier")
        verbose_name_plural = _("Paniers")
        indexes = [
            models.Index(fields=["is_active", "created_at"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["session_key", "is_active"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        if self.user_id:
            return f"Panier de {self.user}"
        return f"Panier invité {self.session_key or self.pk}"

    def clean(self):
        super().clean()

        if self.currency:
            self.currency = self.currency.strip().upper()

        if self.session_key:
            self.session_key = self.session_key.strip() or None

        # ✅ règle prod : user XOR session_key (pas les deux, pas aucun)
        has_user = bool(self.user_id)
        has_session = bool(self.session_key)

        if not has_user and not has_session:
            raise ValidationError({"session_key": _("Renseignez un utilisateur ou une clé de session.")})

        if has_user and has_session:
            raise ValidationError({"session_key": _("Un panier ne peut pas avoir à la fois user et session_key.")})

    def save(self, *args, **kwargs):
        if self.currency:
            self.currency = self.currency.strip().upper()
        if self.session_key:
            self.session_key = self.session_key.strip() or None

        self.full_clean()
        super().save(*args, **kwargs)

    # -------------------------
    # Helpers
    # -------------------------
    @property
    def total_items(self) -> int:
        return sum((item.quantity or 0) for item in self.items.all())

    @property
    def subtotal_amount(self) -> Decimal:
        total = Decimal("0")
        for item in self.items.all():
            try:
                total += (item.total_price or Decimal("0"))
            except Exception:
                continue
        return total

    @property
    def total_amount(self) -> Decimal:
        return self.subtotal_amount

    @property
    def is_empty(self) -> bool:
        return self.total_items == 0

    def assert_active(self):
        if not self.is_active:
            raise ValidationError(_("Ce panier est inactif."))

    def clear(self):
        self.items.all().delete()

    def touch(self):
        """Utile si tu veux forcer updated_at après des actions panier."""
        type(self).objects.filter(pk=self.pk).update(updated_at=models.functions.Now())




# # economic/ecommerce/models/cart.py

# from __future__ import annotations

# from decimal import Decimal

# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="cart",
#         verbose_name=_("Utilisateur"),
#         null=True,
#         blank=True,
#     )

#     # ✅ Panier invité (sans compte) - très utile en prod
#     session_key = models.CharField(
#         max_length=64,
#         null=True,
#         blank=True,
#         unique=True,
#         db_index=True,
#         verbose_name=_("Clé session"),
#         help_text=_("Pour les paniers invités (si user est vide)."),
#     )

#     # ✅ Devise (cohérence affichage / factures)
#     currency = models.CharField(
#         max_length=5,
#         default="XOF",
#         db_index=True,
#         verbose_name=_("Devise"),
#         help_text=_("Ex: XOF, EUR, USD"),
#     )

#     # ✅ Statut simple (prod)
#     is_active = models.BooleanField(
#         default=True,
#         db_index=True,
#         verbose_name=_("Actif"),
#         help_text=_("Désactiver un panier sans le supprimer."),
#     )

#     # ✅ Optionnel : expiration (nettoyage cron / management command)
#     expires_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Expire le"),
#         help_text=_("Optionnel : permet de purger les paniers inactifs."),
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
#         verbose_name = _("Panier")
#         verbose_name_plural = _("Paniers")
#         indexes = [
#             models.Index(fields=["is_active", "created_at"]),
#             models.Index(fields=["user", "is_active"]),
#             models.Index(fields=["session_key", "is_active"]),
#             models.Index(fields=["expires_at"]),
#         ]

#     def __str__(self):
#         if self.user_id:
#             return f"Panier de {self.user}"
#         return f"Panier invité {self.session_key or self.pk}"

#     def clean(self):
#         super().clean()

#         # normalise currency
#         if self.currency:
#             self.currency = self.currency.strip().upper()

#         # règle prod : on doit avoir user OU session_key
#         if not self.user_id and not (self.session_key and self.session_key.strip()):
#             raise ValidationError({"session_key": _("Renseignez un utilisateur ou une clé de session.")})

#         # normalise session_key
#         if self.session_key:
#             self.session_key = self.session_key.strip() or None

#     @property
#     def total_items(self) -> int:
#         # ⚠️ utilise CartItem via related_name="items"
#         return sum((item.quantity or 0) for item in self.items.all())

#     @property
#     def subtotal_amount(self) -> Decimal:
#         # ⚠️ utilise CartItem.total_price (Decimal)
#         total = Decimal("0")
#         for item in self.items.all():
#             try:
#                 total += (item.total_price or Decimal("0"))
#             except Exception:
#                 continue
#         return total

#     @property
#     def total_amount(self) -> Decimal:
#         # pour l’instant = sous-total (si tu ajoutes livraison/taxes plus tard, ça évoluera ici)
#         return self.subtotal_amount

#     def clear(self):
#         self.items.all().delete()





# # economic/ecommerce/models/cart.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="cart",
#         verbose_name=_("Utilisateur"),
#         null=True,
#         blank=True,
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     def __str__(self):
#         return f"Panier de {self.user}"

#     @property
#     def total_amount(self):
#         # ⚠️ utilise CartItem via related_name="items"
#         return sum(item.total_price for item in self.items.all())







# # /economic/ecommerce/models/cart.py

# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="cart",          # 🔑 simple, unique
#         verbose_name=_("Utilisateur"),
#         null=True,
#         blank=True,
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créé le"),
#     )

#     def __str__(self):
#         return f"Panier #{self.pk}"
