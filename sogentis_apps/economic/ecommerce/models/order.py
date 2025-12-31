# /economic/ecommerce/models/order.py
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    # ==========================
    # STATUTS COMMANDE
    # ==========================
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, _("En attente")),
        (STATUS_PAID, _("Payée")),
        (STATUS_SHIPPED, _("Expédiée")),
        (STATUS_COMPLETED, _("Terminée")),
        (STATUS_CANCELLED, _("Annulée")),
    ]

    # ==========================
    # IDENTIFIANT PUBLIC
    # ==========================
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    # ==========================
    # UTILISATEUR (source de vérité)
    # ==========================
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # 🔒 on ne supprime jamais une commande
        related_name="orders",
        verbose_name=_("Utilisateur"),
    )

    # ==========================
    # SNAPSHOT EMAIL (facture / export / guest)
    # ==========================
    customer_email = models.EmailField(
        _("Email client"),
        blank=True,
        db_index=True,
        help_text=_("Copie de l'email au moment de la commande (facture / export)."),
    )

    # ==========================
    # STATUT & MONTANT
    # ==========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_("Statut"),
        db_index=True,
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Montant total"),
    )

    # ==========================
    # TIMESTAMPS
    # ==========================
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Créée le"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Mise à jour le"),
    )

    class Meta:
        verbose_name = _("Commande")
        verbose_name_plural = _("Commandes")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
            models.Index(fields=["customer_email"]),
        ]

    def __str__(self):
        return f"Commande {self.uuid}"

    def save(self, *args, **kwargs):
        """
        Remplit automatiquement customer_email lors de la création,
        afin de figer l'email au moment de l'achat.
        """
        if self.user and not self.customer_email:
            self.customer_email = getattr(self.user, "email", "") or ""
        super().save(*args, **kwargs)

    # ==========================
    # HELPERS MÉTIER
    # ==========================
    @property
    def is_paid(self):
        return self.status in {
            self.STATUS_PAID,
            self.STATUS_SHIPPED,
            self.STATUS_COMPLETED,
        }

    @property
    def is_editable(self):
        """
        Une commande ne doit plus être modifiée après paiement
        """
        return self.status == self.STATUS_PENDING






# # /economic/ecommerce/models/order.py
# import uuid
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Order(models.Model):
#     # ==========================
#     # STATUTS COMMANDE
#     # ==========================
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     # ==========================
#     # IDENTIFIANT PUBLIC
#     # ==========================
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     # ==========================
#     # UTILISATEUR
#     # ==========================
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,   # 🔒 on ne supprime jamais une commande
#         related_name="orders",
#         verbose_name=_("Utilisateur"),
#     )

#     # ==========================
#     # STATUT & MONTANT
#     # ==========================
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#         db_index=True,  # 🔑 important pour filtres admin / dashboard
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant total"),
#     )

#     # ==========================
#     # TIMESTAMPS
#     # ==========================
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#         verbose_name=_("Mise à jour le"),
#     )

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["status"]),
#             models.Index(fields=["created_at"]),
#         ]

#     def __str__(self):
#         return f"Commande {self.uuid}"

#     # ==========================
#     # HELPERS MÉTIER
#     # ==========================
#     @property
#     def is_paid(self):
#         return self.status in {self.STATUS_PAID, self.STATUS_SHIPPED, self.STATUS_COMPLETED}

#     @property
#     def is_editable(self):
#         """
#         Une commande ne doit plus être modifiée après paiement
#         """
#         return self.status == self.STATUS_PENDING








# # /economic/ecommerce/models/order.py

# import uuid
# from django.conf import settings
# from django.db import models
# from django.utils.translation import gettext_lazy as _


# class Order(models.Model):
#     STATUS_PENDING = "pending"
#     STATUS_PAID = "paid"
#     STATUS_SHIPPED = "shipped"
#     STATUS_COMPLETED = "completed"
#     STATUS_CANCELLED = "cancelled"

#     STATUS_CHOICES = [
#         (STATUS_PENDING, _("En attente")),
#         (STATUS_PAID, _("Payée")),
#         (STATUS_SHIPPED, _("Expédiée")),
#         (STATUS_COMPLETED, _("Terminée")),
#         (STATUS_CANCELLED, _("Annulée")),
#     ]

#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         editable=False,
#         unique=True,
#         verbose_name=_("UUID"),
#     )

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="orders",          # 🔑 simple et sans clash
#         verbose_name=_("Utilisateur"),
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default=STATUS_PENDING,
#         verbose_name=_("Statut"),
#     )

#     total_amount = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         verbose_name=_("Montant total"),
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("Créée le"),
#     )

#     class Meta:
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"Commande {self.uuid}"
