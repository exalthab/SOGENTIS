# economic/ecommerce/models/order.py

from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.utils import timezone  # ✅ needed for default

from .product import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("En attente")
        PAID = "paid", _("Payée")
        PROCESSING = "processing", _("En traitement")
        SHIPPED = "shipped", _("Expédiée")
        DELIVERED = "delivered", _("Livrée")
        CANCELLED = "cancelled", _("Annulée")
        REFUNDED = "refunded", _("Remboursée")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ecom_orders",
        help_text=_("Utilisateur connecté ayant réalisé la commande"),
    )

    tracking_code = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Infos client (snapshot)
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)

    shipping_address = models.TextField(blank=True, null=True)
    shipping_city = models.CharField(max_length=120, blank=True, null=True)
    shipping_country = models.CharField(max_length=120, blank=True, null=True)

    # Montants
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Paiement
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(default=timezone.now)

    # PDF facture (optionnel / futur)
    invoice_pdf = models.FileField(upload_to="economic/orders/invoices/", blank=True, null=True)

    # ✅ new field
    created_at = models.DateTimeField(default=timezone.now)
    
    updated_at = models.DateTimeField(default=timezone.now)


    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Commande")
        verbose_name_plural = _("Commandes")

    def __str__(self):
        return f"{self.tracking_code} — {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = get_random_string(12).upper()
        super().save(*args, **kwargs)

    @property
    def items_count(self) -> int:
        return sum(i.quantity for i in self.items.all())

    def recalc_totals(self, save: bool = True):
        subtotal = sum(i.line_total for i in self.items.all())
        self.subtotal = subtotal
        # total = subtotal + tax + shipping - discount
        self.total = (self.subtotal + self.tax + self.shipping_fee) - self.discount_total
        if save:
            self.save(update_fields=["subtotal", "total", "updated_at"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    # Snapshot produit
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    product_name = models.CharField(max_length=255)
    product_slug = models.SlugField(max_length=255, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("Article de commande")
        verbose_name_plural = _("Articles de commande")

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if self.product:
            if not self.product_name:
                self.product_name = self.product.safe_translation_getter("name", any_language=True)
            if not self.product_slug:
                self.product_slug = self.product.slug
        super().save(*args, **kwargs)




# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'En attente'),
#         ('paid', 'Payée'),
#         ('shipped', 'Expédiée'),
#         ('done', 'Livrée'),
#         ('cancel', 'Annulée'),
#     ]
#     tracking_code = models.CharField(max_length=12, unique=True, blank=True)
#     full_name = models.CharField(max_length=120)
#     email = models.EmailField()
#     phone = models.CharField(max_length=30, blank=True)
#     address = models.CharField(max_length=255, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     total = models.PositiveIntegerField(default=0)

#     def save(self, *args, **kwargs):
#         if not self.tracking_code:
#             self.tracking_code = get_random_string(10).upper()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Commande {self.tracking_code}"



# # economic/ecommerce/models/order.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils.crypto import get_random_string
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class Order(models.Model):

#     class OrderStatus(models.TextChoices):
#         PENDING = "pending", _("En attente")
#         PROCESSING = "processing", _("En traitement")
#         SHIPPED = "shipped", _("Expédiée")
#         DELIVERED = "delivered", _("Livrée")
#         CANCELLED = "cancelled", _("Annulée")

#     # --- Informations client ---
#     full_name = models.CharField(max_length=150)
#     email = models.EmailField()
#     phone = models.CharField(max_length=30, blank=True, null=True)
#     address = models.CharField(max_length=255, blank=True, null=True)

#     # --- Infos commande ---
#     tracking_code = models.CharField(max_length=12, unique=True, editable=False)
#     status = models.CharField(
#         max_length=20,
#         choices=OrderStatus.choices,
#         default=OrderStatus.PENDING
#     )
#     total = models.DecimalField(max_digits=12, decimal_places=2)

#     # --- Audit ---
#     created_at = models.DateTimeField(auto_now_add=True)

#     # --- (optionnel) association utilisateur ---
#     user = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True, blank=True,
#         related_name="orders",
#         help_text=_("Utilisateur connecté ayant passé cette commande (optionnel)")
#     )

#     class Meta:
#         ordering = ["-created_at"]
#         verbose_name = _("Commande")
#         verbose_name_plural = _("Commandes")

#     def __str__(self):
#         return f"Order #{self.id} — {self.full_name}"

#     # --- Génération code tracking ---
#     def save(self, *args, **kwargs):
#         if not self.tracking_code:
#             self.tracking_code = get_random_string(length=12).upper()
#         super().save(*args, **kwargs)

#     @property
#     def status_label(self):
#         return self.get_status_display()

#     @property
#     def items_count(self):
#         return self.items.count()

#     @property
#     def formatted_total(self):
#         return f"{self.total:,.0f} FCFA"


# # =============================================================
# # ORDER ITEM : Produits de la commande
# # =============================================================

# class OrderItem(models.Model):

#     order = models.ForeignKey(
#         Order,
#         on_delete=models.CASCADE,
#         related_name="items"
#     )
#     product_name = models.CharField(max_length=255)
#     quantity = models.PositiveIntegerField(default=1)
#     unit_price = models.DecimalField(max_digits=12, decimal_places=2)

#     def __str__(self):
#         return f"{self.product_name} x{self.quantity}"

#     @property
#     def subtotal(self):
#         return float(self.unit_price) * self.quantity
