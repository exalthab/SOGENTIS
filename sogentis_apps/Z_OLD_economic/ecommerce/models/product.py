# economic/ecommerce/models/product.py
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field

from .category import Category


class Product(TranslatableModel):
    """
    Modèle Produit principal
    - Multilingue (Parler)
    - Compatible marketplace pro
    - SEO ready
    - Promotions, flash sales, badges
    """

    # =====================================================
    # BADGES VISUELS (shop / product_detail)
    # =====================================================
    class Badges(models.TextChoices):
        NONE = "none", _("Aucun")
        HOT = "hot", _("🔥 Hot")
        NEW = "new", _("🆕 Nouveau")
        TOP = "top", _("⭐ Top Vente")
        LIMITED = "limited", _("⚡ Édition limitée")

    # =====================================================
    # RELATIONS
    # =====================================================
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name=_("Catégorie"),
    )

    # =====================================================
    # CHAMPS TRADUITS
    # =====================================================
    translations = TranslatedFields(
        name=models.CharField(_("Nom du produit"), max_length=200),
        short_description=models.CharField(
            _("Description courte"), max_length=300, blank=True
        ),
        description=CKEditor5Field(
            _("Description détaillée"), config_name="default", blank=True
        ),
        specifications=CKEditor5Field(
            _("Fiche technique"), config_name="default", blank=True
        ),
        seo_title=models.CharField(
            _("Titre SEO"), max_length=255, blank=True
        ),
        seo_description=models.CharField(
            _("Description SEO"), max_length=300, blank=True
        ),
    )

    # =====================================================
    # IDENTITÉ / SEO
    # =====================================================
    slug = models.SlugField(_("Slug"), max_length=255, unique=True, blank=True)

    # =====================================================
    # PRIX & PROMOTIONS
    # =====================================================
    price = models.DecimalField(_("Prix"), max_digits=12, decimal_places=2)
    old_price = models.DecimalField(
        _("Ancien prix"), max_digits=12, decimal_places=2, blank=True, null=True
    )
    promo_percent = models.PositiveIntegerField(
        _("Réduction (%)"), default=0
    )

    # =====================================================
    # STOCK & PERFORMANCE
    # =====================================================
    stock = models.PositiveIntegerField(_("Stock disponible"), default=0)
    sold_count = models.PositiveIntegerField(_("Nombre de ventes"), default=0)

    rating = models.DecimalField(
        _("Note moyenne"), max_digits=3, decimal_places=1, default=0
    )
    reviews_count_cached = models.PositiveIntegerField(
        _("Nombre d’avis"), default=0
    )

    # =====================================================
    # MARKETING & VISIBILITÉ
    # =====================================================
    badge = models.CharField(
        _("Badge"),
        max_length=20,
        choices=Badges.choices,
        default=Badges.NONE,
    )
    badge_text = models.CharField(
        _("Texte badge personnalisé"),
        max_length=50,
        blank=True,
        help_text=_("Optionnel – affiché sur la carte produit"),
    )

    is_featured = models.BooleanField(_("Produit vedette"), default=False)
    is_flash_sale = models.BooleanField(_("Flash sale"), default=False)
    flash_ends_at = models.DateTimeField(
        _("Fin flash sale"), blank=True, null=True
    )

    is_new = models.BooleanField(_("Nouveau produit"), default=False)
    is_active = models.BooleanField(_("Actif"), default=True)

    # =====================================================
    # DATES
    # =====================================================
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    # =====================================================
    # META
    # =====================================================
    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["price"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_featured"]),
        ]

    # =====================================================
    # STRING
    # =====================================================
    def __str__(self):
        return (
            self.safe_translation_getter("name", any_language=True)
            or _("Produit sans nom")
        )

    # =====================================================
    # PROPRIÉTÉS MÉTIER (UTILISÉES PARTOUT)
    # =====================================================
    @property
    def in_stock(self) -> bool:
        return self.stock > 0

    @property
    def has_promo(self) -> bool:
        return self.promo_percent > 0

    @property
    def discounted_price(self):
        if self.has_promo:
            return self.price - (self.price * self.promo_percent / 100)
        return self.price

    @property
    def reviews_count(self) -> int:
        return int(self.reviews_count_cached or 0)

    @property
    def is_flash_active(self) -> bool:
        if not self.is_flash_sale:
            return False
        if self.flash_ends_at:
            return timezone.now() <= self.flash_ends_at
        return True

    # =====================================================
    # SAVE OVERRIDE
    # =====================================================
    def save(self, *args, **kwargs):
        # Génération du slug
        if not self.slug:
            base = slugify(
                self.safe_translation_getter("name", any_language=True)
            ) or "produit"
            slug = base
            i = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug

        # Auto old_price si promo
        if self.has_promo and not self.old_price:
            self.old_price = self.price

        super().save(*args, **kwargs)





# # economic/ecommerce/models/product.py

# from django.db import models
# from django.utils.text import slugify
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone


# class Product(TranslatableModel):
#     """Main product model with multilingual support."""

#     class Badges(models.TextChoices):
#         NONE = "none", _("Aucun")
#         HOT = "hot", _("🔥 Hot")
#         NEW = "new", _("🆕 Nouveau")
#         TOP = "top", _("⭐ Top Vente")
#         LIMITED = "limited", _("⚡ Edition Limitée")

#     from .category import Category  # local import to avoid circular import

#     category = models.ForeignKey(
#         Category,
#         related_name="products",
#         on_delete=models.CASCADE,
#         verbose_name=_("Catégorie"),
#     )

#     translations = TranslatedFields(
#         name=models.CharField(_("Nom"), max_length=200),
#         short_description=models.CharField(_("Courte description"), max_length=300, blank=True),
#         description=CKEditor5Field(_("Description"), config_name="default", blank=True),
#         specifications=CKEditor5Field(_("Spécifications"), config_name="default", blank=True),
#     )

#     slug = models.SlugField(max_length=255, unique=True, blank=True)

#     price = models.DecimalField(max_digits=12, decimal_places=2)
#     old_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
#     promo_percent = models.PositiveIntegerField(default=0, help_text=_("Pourcentage de réduction"))

#     stock = models.PositiveIntegerField(default=0)
#     sold_count = models.PositiveIntegerField(default=0)

#     rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
#     reviews_count_cached = models.PositiveIntegerField(default=0)
#     badge = models.CharField(max_length=20, choices=Badges.choices, default=Badges.NONE)
#     badge_text = models.CharField(max_length=50, blank=True, help_text=_("Texte badge libre (optionnel)"))

#     is_featured = models.BooleanField(default=False)
#     is_flash_sale = models.BooleanField(default=False)
#     flash_ends_at = models.DateTimeField(blank=True, null=True)
#     is_new = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         ordering = ["-created_at"]
#         verbose_name = _("Produit")
#         verbose_name_plural = _("Produits")

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True) or "Unnamed product"

#     @property
#     def in_stock(self) -> bool:
#         return self.stock > 0

#     @property
#     def has_promo(self) -> bool:
#         return (self.promo_percent or 0) > 0

#     @property
#     def discounted_price(self):
#         if self.has_promo:
#             return self.price - (self.price * self.promo_percent / 100)
#         return self.price

#     @property
#     def reviews_count(self) -> int:
#         return int(self.reviews_count_cached or 0)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base = slugify(self.safe_translation_getter("name", any_language=True)) or "produit"
#             slug = base
#             num = 1
#             while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#                 slug = f"{base}-{num}"
#                 num += 1
#             self.slug = slug

#         if self.old_price is None and self.has_promo:
#             self.old_price = self.price

#         super().save(*args, **kwargs)





# # economic/ecommerce/models/product.py

# from django.db import models
# from django.utils.text import slugify
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone  # ✅ needed for default

# from .category import Category


# class Product(TranslatableModel):
#     class Badges(models.TextChoices):
#         NONE = "none", _("Aucun")
#         HOT = "hot", _("🔥 Hot")
#         NEW = "new", _("🆕 Nouveau")
#         TOP = "top", _("⭐ Top Vente")
#         LIMITED = "limited", _("⚡ Edition Limitée")

#     category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)

#     translations = TranslatedFields(
#         name=models.CharField(max_length=200, default="N/A"),
#         short_description=models.CharField(max_length=300, blank=True),
#         description=CKEditor5Field(config_name="default", blank=True),
#         specifications=CKEditor5Field(config_name="default", blank=True),
#     )

#     slug = models.SlugField(max_length=255, unique=True, blank=True)

#     # Prix
#     price = models.DecimalField(max_digits=12, decimal_places=2)
#     old_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
#     promo_percent = models.PositiveIntegerField(default=0, help_text=_("Pourcentage de réduction"))

#     # Stock & ventes
#     stock = models.PositiveIntegerField(default=0)
#     sold_count = models.PositiveIntegerField(default=0)

#     # Affichage marketplace
#     rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)  # ex 4.5
#     reviews_count_cached = models.PositiveIntegerField(default=0)
#     badge = models.CharField(max_length=20, choices=Badges.choices, default=Badges.NONE)
#     badge_text = models.CharField(max_length=50, blank=True, help_text=_("Texte badge libre (optionnel)"))

#     is_featured = models.BooleanField(default=False)
#     is_flash_sale = models.BooleanField(default=False)
#     flash_ends_at = models.DateTimeField(blank=True, null=True)

#     is_new = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         ordering = ["-created_at"]
#         verbose_name = _("Produit")
#         verbose_name_plural = _("Produits")

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)

#     @property
#     def in_stock(self) -> bool:
#         return self.stock > 0

#     @property
#     def has_promo(self) -> bool:
#         return (self.promo_percent or 0) > 0

#     @property
#     def discounted_price(self):
#         if self.has_promo:
#             return self.price - (self.price * self.promo_percent / 100)
#         return self.price

#     @property
#     def reviews_count(self) -> int:
#         # rapide (cache) — on recalculera propre en signal/admin plus tard
#         return int(self.reviews_count_cached or 0)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             base = slugify(self.safe_translation_getter("name", any_language=True))
#             slug = base
#             num = 1
#             while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
#                 slug = f"{base}-{num}"
#                 num += 1
#             self.slug = slug

#         if self.old_price is None and self.has_promo:
#             self.old_price = self.price

#         super().save(*args, **kwargs)
