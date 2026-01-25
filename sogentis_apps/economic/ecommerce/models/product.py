# /economic/ecommerce/models/product.py
from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .sku_sequence import SkuSequence


SKU_RE = re.compile(r"^[A-Z0-9]{3,8}-[A-Z0-9]{3,8}-\d{4}$")


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

    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("SKU"),
        blank=True,
        help_text=_("Format recommandé : <VENDORCODE>-<CATCODE>-<NNNN> (ex: SOG-TECH-0001)."),
        db_index=True,
    )

    fiche_technique = models.TextField(blank=True, verbose_name=_("Fiche technique"))
    image = models.ImageField(
        upload_to="products/main/%Y/%m/",
        blank=True,
        null=True,
        verbose_name=_("Image principale"),
    )
    is_new = models.BooleanField(default=False, verbose_name=_("Nouveau"), db_index=True)

    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Prix"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))

    is_active = models.BooleanField(default=True, verbose_name=_("Actif"), db_index=True)
    is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"), db_index=True)

    track_stock = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Suivre le stock"),
        help_text=_("Décochez pour services / sur commande (stock illimité)."),
    )

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
            models.Index(fields=["is_new", "is_active"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self) -> str:
        name = self.safe_translation_getter("name", any_language=True)
        if name:
            return f"{name} ({self.sku})" if self.sku else name
        return self.sku or f"Product #{self.pk}"

    def clean(self):
        super().clean()

        if self.sku:
            self.sku = self.sku.strip().upper()

        if self.price is None:
            raise ValidationError({"price": _("Le prix est obligatoire.")})
        if self.price is not None and self.price < 0:
            raise ValidationError({"price": _("Le prix ne peut pas être négatif.")})

        if self.is_featured and not self.is_active:
            raise ValidationError({"is_featured": _("Un produit inactif ne peut pas être mis en avant.")})

        if self.sku and not SKU_RE.match(self.sku):
            raise ValidationError({"sku": _("Format SKU invalide. Ex: SOG-TECH-0001 (VENDOR-CAT-0001).")})

        if not self.sku:
            if not self.vendor_id:
                raise ValidationError({"vendor": _("Le vendeur est requis pour générer automatiquement le SKU.")})

            vcode = getattr(self.vendor, "code", None)
            ccode = getattr(self.category, "code", None)
            if not vcode:
                raise ValidationError({"vendor": _("Le vendeur doit avoir un code (VENDORCODE) pour générer le SKU.")})
            if not ccode:
                raise ValidationError({"category": _("La catégorie doit avoir un code (CATCODE) pour générer le SKU.")})

    @property
    def main_image_obj(self):
        img = getattr(self, "images", None)
        if img is not None:
            main = self.images.filter(is_main=True).first()
            if main:
                return main
            first = self.images.order_by("sort_order", "id").first()
            if first:
                return first
        return None

    @property
    def main_image_url(self) -> str | None:
        obj = self.main_image_obj
        if obj and getattr(obj, "image", None):
            try:
                return obj.image.url
            except Exception:
                return None
        if self.image:
            try:
                return self.image.url
            except Exception:
                return None
        return None

    # ✅ stock respectant track_stock
    @property
    def in_stock(self) -> bool:
        if not self.track_stock:
            return True
        return self.stock > 0

    @property
    def purchasable(self) -> bool:
        if not self.is_active:
            return False
        if not self.track_stock:
            return True
        return self.stock > 0

    def _generate_sku(self) -> str:
        if not self.vendor:
            raise ValidationError({"vendor": _("Vendeur requis pour générer le SKU.")})

        vcode = (getattr(self.vendor, "code", "") or "").strip().upper()
        ccode = (getattr(self.category, "code", "") or "").strip().upper()

        if not vcode:
            raise ValidationError({"vendor": _("Le vendeur doit avoir un code (VENDORCODE).")})
        if not ccode:
            raise ValidationError({"category": _("La catégorie doit avoir un code (CATCODE).")})

        prefix = f"{vcode}-{ccode}-"

        # ✅ Prod-safe: séquence lockée
        with transaction.atomic():
            seq, _ = SkuSequence.objects.select_for_update().get_or_create(
                vendor_code=vcode,
                category_code=ccode,
                defaults={"last_number": 0},
            )
            seq.last_number += 1
            seq.save(update_fields=["last_number", "updated_at"])
            return f"{prefix}{seq.last_number:04d}"

    @staticmethod
    def _clean_seo_text(text: str, max_len: int) -> str:
        t = (text or "").strip()
        if not t:
            return ""
        t = " ".join(t.split())
        return t[:max_len]

    def save(self, *args, **kwargs):
        if self.sku:
            self.sku = self.sku.strip().upper()
        else:
            self.sku = self._generate_sku()

        super().save(*args, **kwargs)
        self._ensure_translation_slugs_and_seo()

    def _ensure_translation_slugs_and_seo(self):
        Translation = self.translations.model
        qs = Translation.objects.filter(master_id=self.pk)

        to_update = []
        for tr in qs:
            changed = False

            if not tr.slug and tr.name:
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
                changed = True

            if tr.name and not tr.seo_title:
                tr.seo_title = self._clean_seo_text(tr.name, 255)
                changed = True

            if not tr.short_description and tr.description:
                tr.short_description = self._clean_seo_text(tr.description, 500)
                changed = True

            if not tr.seo_description:
                src = tr.short_description or tr.description or tr.name or ""
                tr.seo_description = self._clean_seo_text(src, 300)
                changed = True

            if changed:
                to_update.append(tr)

        if to_update:
            Translation.objects.bulk_update(
                to_update,
                ["slug", "seo_title", "seo_description", "short_description"],
            )


# -------------------------------------------------------------------
# ✅ Signal Parler: connect sur le vrai modèle de traduction
# -------------------------------------------------------------------
def _product_translation_autofill(sender, instance, **kwargs):
    master = getattr(instance, "master", None)
    if not master:
        return
    master._ensure_translation_slugs_and_seo()


try:
    ProductTranslation = Product._parler_meta.model  # ✅ vrai modèle de traduction
    post_save.connect(
        _product_translation_autofill,
        sender=ProductTranslation,
        dispatch_uid="ecommerce_product_translation_autofill",
        weak=False,
    )
except Exception:
    pass






# # /economic/ecommerce/models/product.py
# from __future__ import annotations

# import re

# from django.core.exceptions import ValidationError
# from django.db import models, transaction
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from .sku_sequence import SkuSequence


# SKU_RE = re.compile(r"^[A-Z0-9]{3,8}-[A-Z0-9]{3,8}-\d{4}$")


# class Product(TranslatableModel):
#     # Relations
#     category = models.ForeignKey(
#         "Category",
#         on_delete=models.PROTECT,
#         related_name="products",
#         verbose_name=_("Catégorie"),
#     )

#     vendor = models.ForeignKey(
#         "Vendor",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="products",
#         verbose_name=_("Vendeur"),
#     )

#     # Identifiants
#     # ✅ sku peut être saisi OU auto-généré si vide (admin/prod)
#     sku = models.CharField(
#         max_length=100,
#         unique=True,
#         verbose_name=_("SKU"),
#         blank=True,
#         help_text=_("Format recommandé : <VENDORCODE>-<CATCODE>-<NNNN> (ex: SOG-TECH-0001)."),
#         db_index=True,
#     )

#     # ✅ Champs legacy que tu veux garder
#     fiche_technique = models.TextField(blank=True, verbose_name=_("Fiche technique"))
#     image = models.ImageField(
#         upload_to="products/main/%Y/%m/",
#         blank=True,
#         null=True,
#         verbose_name=_("Image principale"),
#     )
#     is_new = models.BooleanField(default=False, verbose_name=_("Nouveau"), db_index=True)

#     # Commerce
#     price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Prix"))
#     stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))

#     # Statuts
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"), db_index=True)
#     is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"), db_index=True)

#     # ✅ Stock prod: services / impression peuvent désactiver le tracking
#     track_stock = models.BooleanField(
#         default=True,
#         db_index=True,
#         verbose_name=_("Suivre le stock"),
#         help_text=_("Décochez pour services / sur commande (stock illimité)."),
#     )
#     # Dates
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     # Traductions (Parler)
#     translations = TranslatedFields(
#         name=models.CharField(max_length=255, verbose_name=_("Nom")),
#         slug=models.SlugField(max_length=260, blank=True, db_index=True, verbose_name=_("Slug")),
#         short_description=models.CharField(max_length=500, blank=True, verbose_name=_("Description courte")),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#         seo_title=models.CharField(max_length=255, blank=True, verbose_name=_("Titre SEO")),
#         seo_description=models.CharField(max_length=300, blank=True, verbose_name=_("Description SEO")),
#     )

#     class TranslatedMeta:
#         unique_together = (("language_code", "slug"),)
#         indexes = (models.Index(fields=("language_code", "slug")),)

#     class Meta:
#         verbose_name = _("Produit")
#         verbose_name_plural = _("Produits")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["is_active", "is_featured", "-created_at"]),
#             models.Index(fields=["category", "is_active"]),
#             models.Index(fields=["vendor", "is_active"]),
#             models.Index(fields=["is_new", "is_active"]),
#             models.Index(fields=["sku"]),
#         ]

#     def __str__(self) -> str:
#         name = self.safe_translation_getter("name", any_language=True)
#         if name:
#             return f"{name} ({self.sku})" if self.sku else name
#         return self.sku or f"Product #{self.pk}"

#     # -------------------------
#     # Validations prod
#     # -------------------------
#     def clean(self):
#         super().clean()

#         # normalise SKU (si fourni)
#         if self.sku:
#             self.sku = self.sku.strip().upper()

#         if self.price is None:
#             raise ValidationError({"price": _("Le prix est obligatoire.")})
#         if self.price is not None and self.price < 0:
#             raise ValidationError({"price": _("Le prix ne peut pas être négatif.")})

#         # logique "featured"
#         if self.is_featured and not self.is_active:
#             raise ValidationError({"is_featured": _("Un produit inactif ne peut pas être mis en avant.")})

#         # si SKU est fourni, on peut valider son format (convention prod)
#         if self.sku and not SKU_RE.match(self.sku):
#             raise ValidationError(
#                 {"sku": _("Format SKU invalide. Ex: SOG-TECH-0001 (VENDOR-CAT-0001).")}
#             )

#         # si SKU vide, il sera auto-généré => vendor + category codes requis
#         if not self.sku:
#             if not self.vendor_id:
#                 raise ValidationError({"vendor": _("Le vendeur est requis pour générer automatiquement le SKU.")})

#             # On attend Vendor.code et Category.code (CATCODE) que tu viens d’ajouter
#             vcode = getattr(self.vendor, "code", None)
#             ccode = getattr(self.category, "code", None)
#             if not vcode:
#                 raise ValidationError({"vendor": _("Le vendeur doit avoir un code (VENDORCODE) pour générer le SKU.")})
#             if not ccode:
#                 raise ValidationError({"category": _("La catégorie doit avoir un code (CATCODE) pour générer le SKU.")})

#     # -------------------------
#     # Helpers images (inchangés)
#     # -------------------------
#     @property
#     def main_image_obj(self):
#         """
#         Priorité :
#         1) image principale via ProductImage (gallery)
#         2) fallback legacy: self.image
#         """
#         img = getattr(self, "images", None)
#         if img is not None:
#             main = self.images.filter(is_main=True).first()
#             if main:
#                 return main
#             first = self.images.order_by("sort_order", "id").first()
#             if first:
#                 return first
#         return None

#     @property
#     def main_image_url(self) -> str | None:
#         obj = self.main_image_obj
#         if obj and getattr(obj, "image", None):
#             try:
#                 return obj.image.url
#             except Exception:
#                 return None
#         if self.image:
#             try:
#                 return self.image.url
#             except Exception:
#                 return None
#         return None

#     # -------------------------
#     # Stock / disponibilité (utile templates)
#     # -------------------------
#     @property
#     def in_stock(self) -> bool:
#         return self.stock > 0

#     @property
#     def purchasable(self) -> bool:
#         return self.is_active and self.stock > 0

#     # -------------------------
#     # SKU auto (robuste)
#     # - utilise SkuSequence si présent (on l’ajoutera après)
#     # - fallback: calcule le prochain NNNN via le dernier SKU
#     # -------------------------
#     def _generate_sku(self) -> str:
#         if not self.vendor:
#             raise ValidationError({"vendor": _("Vendeur requis pour générer le SKU.")})

#         vcode = (getattr(self.vendor, "code", "") or "").strip().upper()
#         ccode = (getattr(self.category, "code", "") or "").strip().upper()

#         if not vcode:
#             raise ValidationError({"vendor": _("Le vendeur doit avoir un code (VENDORCODE).")})
#         if not ccode:
#             raise ValidationError({"category": _("La catégorie doit avoir un code (CATCODE).")})

#         prefix = f"{vcode}-{ccode}-"

#         # 1) Si le modèle SkuSequence existe => méthode prod-safe (anti-concurrence)
#         try:
#             from economic.ecommerce.models.sku_sequence import SkuSequence  # on l’ajoute juste après

#             with transaction.atomic():
#                 seq, _ = SkuSequence.objects.select_for_update().get_or_create(
#                     vendor_code=vcode,
#                     category_code=ccode,
#                     defaults={"last_number": 0},
#                 )
#                 seq.last_number += 1
#                 seq.save(update_fields=["last_number"])
#                 return f"{prefix}{seq.last_number:04d}"

#         except Exception:
#             # 2) Fallback (si SkuSequence pas encore ajouté)
#             with transaction.atomic():
#                 # lock "soft" du vendeur si possible (réduit les collisions)
#                 try:
#                     type(self.vendor).objects.select_for_update().filter(pk=self.vendor_id).only("id").first()
#                 except Exception:
#                     pass

#                 last_sku = (
#                     self.__class__.objects.select_for_update()
#                     .filter(sku__startswith=prefix)
#                     .order_by("-sku")
#                     .values_list("sku", flat=True)
#                     .first()
#                 )
#                 last_num = 0
#                 if last_sku:
#                     try:
#                         last_num = int(last_sku.split("-")[-1])
#                     except Exception:
#                         last_num = 0

#                 return f"{prefix}{(last_num + 1):04d}"

#     # -------------------------
#     # Slug + SEO auto par langue (prod)
#     # -------------------------
#     @staticmethod
#     def _clean_seo_text(text: str, max_len: int) -> str:
#         t = (text or "").strip()
#         if not t:
#             return ""
#         t = " ".join(t.split())
#         return t[:max_len]

#     def save(self, *args, **kwargs):
#         # SKU auto si vide
#         if self.sku:
#             self.sku = self.sku.strip().upper()
#         else:
#             self.sku = self._generate_sku()

#         super().save(*args, **kwargs)

#         # slugs + seo auto (traductions)
#         self._ensure_translation_slugs_and_seo()

#     def _ensure_translation_slugs_and_seo(self):
#         Translation = self.translations.model
#         qs = Translation.objects.filter(master_id=self.pk)

#         to_update = []
#         for tr in qs:
#             changed = False

#             # slug auto
#             if not tr.slug and tr.name:
#                 base = slugify(tr.name)[:260] or f"product-{self.pk}"
#                 slug = base
#                 n = 2
#                 while Translation.objects.filter(
#                     language_code=tr.language_code,
#                     slug=slug,
#                 ).exclude(master_id=self.pk).exists():
#                     suffix = f"-{n}"
#                     slug = f"{base[: max(1, 260 - len(suffix))]}{suffix}"
#                     n += 1
#                 tr.slug = slug
#                 changed = True

#             # SEO auto si vide (utile prod)
#             if tr.name and not tr.seo_title:
#                 tr.seo_title = self._clean_seo_text(tr.name, 255)
#                 changed = True

#             if not tr.short_description and tr.description:
#                 tr.short_description = self._clean_seo_text(tr.description, 500)
#                 changed = True

#             if not tr.seo_description:
#                 src = tr.short_description or tr.description or tr.name or ""
#                 tr.seo_description = self._clean_seo_text(src, 300)
#                 changed = True

#             if changed:
#                 to_update.append(tr)

#         if to_update:
#             Translation.objects.bulk_update(
#                 to_update,
#                 ["slug", "seo_title", "seo_description", "short_description"],
#             )


# # -------------------------------------------------------------------
# # ✅ Signal: en admin Parler, la traduction peut être sauvée APRES l'objet.
# # => garantit slug + SEO auto dès qu'une traduction est enregistrée.
# # -------------------------------------------------------------------
# @receiver(
#     post_save,
#     sender=Product.translations.model,
#     dispatch_uid="ecommerce_product_translation_autofill",
# )
# def _product_translation_autofill(sender, instance, **kwargs):
#     master = getattr(instance, "master", None)
#     if not master:
#         return
#     # bulk_update ne retrigger pas post_save => pas de boucle
#     master._ensure_translation_slugs_and_seo()





# # /economic/ecommerce/models/product.py
# from __future__ import annotations

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class Product(TranslatableModel):
#     # Relations
#     category = models.ForeignKey(
#         "Category",
#         on_delete=models.PROTECT,
#         related_name="products",
#         verbose_name=_("Catégorie"),
#     )

#     vendor = models.ForeignKey(
#         "Vendor",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="products",
#         verbose_name=_("Vendeur"),
#     )

#     # Identifiants
#     sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU"))

#     # ✅ Champs legacy que tu veux garder
#     fiche_technique = models.TextField(blank=True, verbose_name=_("Fiche technique"))
#     image = models.ImageField(upload_to="products/main/%Y/%m/", blank=True, null=True, verbose_name=_("Image principale"))
#     is_new = models.BooleanField(default=False, verbose_name=_("Nouveau"), db_index=True)

#     # Commerce
#     price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Prix"))
#     stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))

#     # Statuts
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"), db_index=True)
#     is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"), db_index=True)

#     # Dates
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     # Traductions (Parler)
#     translations = TranslatedFields(
#         name=models.CharField(max_length=255, verbose_name=_("Nom")),
#         slug=models.SlugField(max_length=260, blank=True, db_index=True, verbose_name=_("Slug")),
#         short_description=models.CharField(max_length=500, blank=True, verbose_name=_("Description courte")),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#         seo_title=models.CharField(max_length=255, blank=True, verbose_name=_("Titre SEO")),
#         seo_description=models.CharField(max_length=300, blank=True, verbose_name=_("Description SEO")),
#     )

#     class TranslatedMeta:
#         unique_together = (("language_code", "slug"),)
#         indexes = (models.Index(fields=("language_code", "slug")),)

#     class Meta:
#         verbose_name = _("Produit")
#         verbose_name_plural = _("Produits")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["is_active", "is_featured", "-created_at"]),
#             models.Index(fields=["category", "is_active"]),
#             models.Index(fields=["vendor", "is_active"]),
#             models.Index(fields=["is_new", "is_active"]),
#         ]

#     def __str__(self) -> str:
#         return self.safe_translation_getter("name", any_language=True) or f"Product #{self.pk}"

#     def clean(self):
#         super().clean()
#         if self.price is None:
#             raise ValidationError({"price": _("Le prix est obligatoire.")})

#     @property
#     def main_image_obj(self):
#         """
#         Priorité :
#         1) image principale via ProductImage (gallery)
#         2) fallback legacy: self.image
#         """
#         # nécessite models/product_image.py avec related_name="images"
#         img = getattr(self, "images", None)
#         if img is not None:
#             main = self.images.filter(is_main=True).first()
#             if main:
#                 return main
#             first = self.images.order_by("sort_order", "id").first()
#             if first:
#                 return first
#         return None

#     @property
#     def main_image_url(self) -> str | None:
#         obj = self.main_image_obj
#         if obj and getattr(obj, "image", None):
#             try:
#                 return obj.image.url
#             except Exception:
#                 return None
#         if self.image:
#             try:
#                 return self.image.url
#             except Exception:
#                 return None
#         return None

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         self._ensure_translation_slugs()

#     def _ensure_translation_slugs(self):
#         Translation = self.translations.model
#         qs = Translation.objects.filter(master_id=self.pk)

#         to_update = []
#         for tr in qs:
#             if tr.slug or not tr.name:
#                 continue

#             base = slugify(tr.name)[:260] or f"product-{self.pk}"
#             slug = base
#             n = 2
#             while Translation.objects.filter(
#                 language_code=tr.language_code,
#                 slug=slug,
#             ).exclude(master_id=self.pk).exists():
#                 suffix = f"-{n}"
#                 slug = f"{base[: max(1, 260 - len(suffix))]}{suffix}"
#                 n += 1

#             tr.slug = slug
#             to_update.append(tr)

#         if to_update:
#             Translation.objects.bulk_update(to_update, ["slug"])




# # /economic/ecommerce/models/product.py
# from __future__ import annotations

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class Product(TranslatableModel):
#     category = models.ForeignKey(
#         "Category",
#         on_delete=models.PROTECT,
#         related_name="products",
#         verbose_name=_("Catégorie"),
#     )

#     vendor = models.ForeignKey(
#         "Vendor",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="products",
#         verbose_name=_("Vendeur"),
#     )

#     sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU"))

#     # ✅ Prix “rapide” (affichage). En prod, tu peux le garder comme fallback si pas de ProductPricing.
#     price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Prix"))
#     stock = models.PositiveIntegerField(default=0, verbose_name=_("Stock"))

#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"), db_index=True)
#     is_featured = models.BooleanField(default=False, verbose_name=_("Mis en avant"), db_index=True)

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     translations = TranslatedFields(
#         name=models.CharField(max_length=255, verbose_name=_("Nom")),
#         slug=models.SlugField(max_length=260, blank=True, db_index=True, verbose_name=_("Slug")),
#         short_description=models.CharField(max_length=500, blank=True, verbose_name=_("Description courte")),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#         seo_title=models.CharField(max_length=255, blank=True, verbose_name=_("Titre SEO")),
#         seo_description=models.CharField(max_length=300, blank=True, verbose_name=_("Description SEO")),
#     )

#     class TranslatedMeta:
#         unique_together = (("language_code", "slug"),)
#         indexes = (models.Index(fields=("language_code", "slug")),)

#     class Meta:
#         verbose_name = _("Produit")
#         verbose_name_plural = _("Produits")
#         ordering = ["-created_at"]
#         indexes = [
#             models.Index(fields=["is_active", "is_featured", "-created_at"]),
#             models.Index(fields=["category", "is_active"]),
#             models.Index(fields=["vendor", "is_active"]),
#         ]

#     def __str__(self) -> str:
#         return self.safe_translation_getter("name", any_language=True) or f"Product #{self.pk}"

#     def clean(self):
#         super().clean()
#         if self.price is None:
#             raise ValidationError({"price": _("Le prix est obligatoire.")})

#     @property
#     def main_image(self):
#         # image principale si existe, sinon la première
#         img = self.images.filter(is_main=True).first()
#         return img or self.images.order_by("sort_order", "id").first()

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         self._ensure_translation_slugs()

#     def _ensure_translation_slugs(self):
#         Translation = self.translations.model
#         qs = Translation.objects.filter(master_id=self.pk)

#         to_update = []
#         for tr in qs:
#             if tr.slug or not tr.name:
#                 continue

#             base = slugify(tr.name)[:260] or f"product-{self.pk}"
#             slug = base
#             n = 2
#             while Translation.objects.filter(
#                 language_code=tr.language_code,
#                 slug=slug,
#             ).exclude(master_id=self.pk).exists():
#                 suffix = f"-{n}"
#                 slug = f"{base[: max(1, 260 - len(suffix))]}{suffix}"
#                 n += 1

#             tr.slug = slug
#             to_update.append(tr)

#         if to_update:
#             Translation.objects.bulk_update(to_update, ["slug"])





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
