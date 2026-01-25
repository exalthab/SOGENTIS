# economic/ecommerce/models/category.py
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    # PK explicite (sécurité DB / séquences)
    id = models.BigAutoField(primary_key=True)

    # ✅ CATCODE (utilisé pour SKU : <VENDORCODE>-<CATCODE>-<NNNN>)
    # nullable pour compatibilité legacy
    code = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Code catégorie (CATCODE)"),
        validators=[
            RegexValidator(
                r"^[A-Z0-9]{3,8}$",
                _("Format invalide. Ex: TECH, PHON, PRINT, SERV (3–8 caractères A-Z/0-9)."),
            )
        ],
        help_text=_("Code stable utilisé pour les SKU. Ex: TECH, PHON, PRINT, SERV."),
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
        verbose_name=_("Catégorie parente"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

    # -------------------------
    # Traductions (Parler)
    # -------------------------
    translations = TranslatedFields(
        name=models.CharField(max_length=200, verbose_name=_("Nom")),
        slug=models.SlugField(
            max_length=220,
            blank=True,
            db_index=True,
            verbose_name=_("Slug"),
            help_text=_("Auto-généré si vide (par langue)."),
        ),
        description=models.TextField(blank=True, verbose_name=_("Description")),
        seo_title=models.CharField(max_length=255, blank=True, verbose_name=_("Titre SEO")),
        seo_description=models.CharField(max_length=300, blank=True, verbose_name=_("Description SEO")),
    )

    class TranslatedMeta:
        unique_together = (("language_code", "slug"),)
        indexes = (models.Index(fields=("language_code", "slug")),)

    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["is_active", "order"]),
            models.Index(fields=["parent", "order"]),
            models.Index(fields=["code"]),
        ]

    def __str__(self) -> str:
        name = self.safe_translation_getter("name", any_language=True) or f"Category #{self.pk}"
        return f"{name} [{self.code}]" if self.code else name

    # -------------------------
    # Validation & normalisation
    # -------------------------
    def clean(self):
        super().clean()

        # normalise CATCODE
        if self.code:
            self.code = self.code.strip().upper() or None

        # auto-parent interdit
        if self.parent_id and self.parent_id == self.pk:
            raise ValidationError({"parent": _("Une catégorie ne peut pas être sa propre parente.")})

        # anti-cycles (A → B → C → A)
        seen = set()
        node = self.parent
        while node is not None:
            if node.pk in seen:
                raise ValidationError({"parent": _("Boucle détectée dans la hiérarchie des catégories.")})
            seen.add(node.pk)
            node = node.parent

    # -------------------------
    # Save & slugs
    # -------------------------
    def save(self, *args, **kwargs):
        # sécurité hors admin
        if self.code:
            self.code = self.code.strip().upper() or None

        super().save(*args, **kwargs)

        # garantit les slugs pour les traductions existantes
        self._ensure_translation_slugs()

    def _ensure_translation_slugs(self):
        """
        Garantit un slug unique par langue pour toutes les traductions existantes.
        """
        Translation = self.translations.model
        qs = Translation.objects.filter(master_id=self.pk)

        to_update = []
        for tr in qs:
            if tr.slug or not tr.name:
                continue

            base = slugify(tr.name)[:220] or f"category-{self.pk}"
            slug = base
            n = 2

            while Translation.objects.filter(
                language_code=tr.language_code,
                slug=slug,
            ).exclude(master_id=self.pk).exists():
                suffix = f"-{n}"
                slug = f"{base[: max(1, 220 - len(suffix))]}{suffix}"
                n += 1

            tr.slug = slug
            to_update.append(tr)

        if to_update:
            Translation.objects.bulk_update(to_update, ["slug"])

    # -------------------------
    # Helpers
    # -------------------------
    def is_root(self) -> bool:
        return self.parent_id is None

    def active_children(self):
        return self.children.filter(is_active=True).order_by("order", "id")

    def get_catcode(self) -> str:
        """Retourne le CATCODE normalisé (toujours MAJ)."""
        return (self.code or "").strip().upper()


# -------------------------------------------------------------------
# ✅ Signal Parler : une traduction peut être sauvée APRES l'objet
# => garantit slug auto même en admin Parler
# -------------------------------------------------------------------
def _category_translation_autoslug(sender, instance, **kwargs):
    master = getattr(instance, "master", None)
    if not master:
        return
    if instance.name and not instance.slug:
        master._ensure_translation_slugs()


# Connexion safe du signal (robuste à l'import)
try:
    CategoryTranslation = Category._parler_meta.model
    post_save.connect(
        _category_translation_autoslug,
        sender=CategoryTranslation,
        dispatch_uid="ecommerce_category_translation_autoslug",
        weak=False,
    )
except Exception:
    # Parler pas encore initialisé → on évite de casser l'import
    pass






# # /economic/ecommerce/models/category.py
# from __future__ import annotations

# from django.core.exceptions import ValidationError
# from django.core.validators import RegexValidator
# from django.db import models
# from django.db.models.signals import post_save
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class Category(TranslatableModel):
#     id = models.BigAutoField(primary_key=True)

#     code = models.CharField(
#         max_length=8,
#         unique=True,
#         null=True,
#         blank=True,
#         verbose_name=_("Code catégorie (CATCODE)"),
#         validators=[
#             RegexValidator(
#                 r"^[A-Z0-9]{3,8}$",
#                 _("Format invalide. Ex: TECH, PHON, PRINT, SERV (3–8 caractères A-Z/0-9)."),
#             )
#         ],
#         help_text=_("Code stable pour SKU. Ex: PHON, TECH, PRINT, SERV..."),
#         db_index=True,
#     )

#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         related_name="children",
#         on_delete=models.SET_NULL,
#         verbose_name=_("Catégorie parente"),
#     )

#     is_active = models.BooleanField(default=True, verbose_name=_("Active"))
#     order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     translations = TranslatedFields(
#         name=models.CharField(max_length=200, verbose_name=_("Nom")),
#         slug=models.SlugField(
#             max_length=220,
#             blank=True,
#             db_index=True,
#             verbose_name=_("Slug"),
#             help_text=_("Auto-généré si vide (par langue)."),
#         ),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#         seo_title=models.CharField(max_length=255, blank=True, verbose_name=_("Titre SEO")),
#         seo_description=models.CharField(max_length=300, blank=True, verbose_name=_("Description SEO")),
#     )

#     class TranslatedMeta:
#         unique_together = (("language_code", "slug"),)
#         indexes = (models.Index(fields=("language_code", "slug")),)

#     class Meta:
#         verbose_name = _("Catégorie")
#         verbose_name_plural = _("Catégories")
#         ordering = ["order", "id"]
#         indexes = [
#             models.Index(fields=["is_active", "order"]),
#             models.Index(fields=["parent", "order"]),
#             models.Index(fields=["code"]),
#         ]

#     def __str__(self) -> str:
#         name = self.safe_translation_getter("name", any_language=True) or f"Category #{self.pk}"
#         return f"{name} [{self.code}]" if self.code else name

#     def clean(self):
#         super().clean()

#         if self.code:
#             self.code = self.code.strip().upper()
#             if not self.code:
#                 self.code = None

#         if self.parent_id and self.parent_id == self.pk:
#             raise ValidationError({"parent": _("Une catégorie ne peut pas être sa propre parente.")})

#         seen = set()
#         node = self.parent
#         while node is not None:
#             if node.pk in seen:
#                 raise ValidationError({"parent": _("Boucle détectée dans la hiérarchie des catégories.")})
#             seen.add(node.pk)
#             node = node.parent

#     def save(self, *args, **kwargs):
#         if self.code:
#             self.code = self.code.strip().upper() or None

#         super().save(*args, **kwargs)
#         self._ensure_translation_slugs()

#     def _ensure_translation_slugs(self):
#         """
#         Garantit slug (par langue) pour les traductions déjà enregistrées en DB.
#         """
#         Translation = self.translations.model  # ✅ ici OK: self.translations est un manager
#         qs = Translation.objects.filter(master_id=self.pk)

#         to_update = []
#         for tr in qs:
#             if tr.slug or not tr.name:
#                 continue

#             base = slugify(tr.name)[:220] or f"category-{self.pk}"
#             slug = base
#             n = 2

#             while Translation.objects.filter(
#                 language_code=tr.language_code,
#                 slug=slug,
#             ).exclude(master_id=self.pk).exists():
#                 suffix = f"-{n}"
#                 slug = f"{base[: max(1, 220 - len(suffix))]}{suffix}"
#                 n += 1

#             tr.slug = slug
#             to_update.append(tr)

#         if to_update:
#             Translation.objects.bulk_update(to_update, ["slug"])

#     def is_root(self) -> bool:
#         return self.parent_id is None

#     def active_children(self):
#         return self.children.filter(is_active=True).order_by("order", "id")

#     def get_catcode(self) -> str:
#         return (self.code or "").strip().upper()


# # -------------------------------------------------------------------
# # ✅ Signal: en admin Parler, la traduction peut être sauvée APRES l'objet.
# # On connecte le post_save sur le modèle de traduction (Parler meta)
# # -------------------------------------------------------------------
# def _category_translation_autoslug(sender, instance, **kwargs):
#     master = getattr(instance, "master", None)
#     if not master:
#         return
#     if instance.name and not instance.slug:
#         master._ensure_translation_slugs()


# # ✅ Connexion safe du signal (évite le sender=Category.translations.model)
# try:
#     CategoryTranslation = Category._parler_meta.model  # ✅ vrai modèle de traduction
#     post_save.connect(
#         _category_translation_autoslug,
#         sender=CategoryTranslation,
#         dispatch_uid="ecommerce_category_translation_autoslug",
#         weak=False,
#     )
# except Exception:
#     # Si parler n'a pas initialisé _parler_meta à l'import (rare), on évite de casser.
#     pass



# # /economic/ecommerce/models/category.py
# from __future__ import annotations

# from django.core.exceptions import ValidationError
# from django.core.validators import RegexValidator
# from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class Category(TranslatableModel):
#     # ✅ Force un PK auto (utile si ta DB a perdu le DEFAULT de la séquence)
#     id = models.BigAutoField(primary_key=True)

#     # ✅ CATCODE (utile pour SKU : <VENDORCODE>-<CATCODE>-<NNNN>)
#     # NOTE: nullable/blank pour éviter une migration bloquante si tu as déjà des catégories.
#     # Ensuite on pourra le rendre obligatoire quand tout est rempli.
#     code = models.CharField(
#         max_length=8,
#         unique=True,
#         null=True,
#         blank=True,
#         verbose_name=_("Code catégorie (CATCODE)"),
#         validators=[
#             RegexValidator(
#                 r"^[A-Z0-9]{3,8}$",
#                 _("Format invalide. Ex: TECH, PHON, PRINT, SERV (3–8 caractères A-Z/0-9)."),
#             )
#         ],
#         help_text=_("Code stable pour SKU. Ex: PHON, TECH, PRINT, SERV..."),
#         db_index=True,
#     )

#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         related_name="children",
#         on_delete=models.SET_NULL,
#         verbose_name=_("Catégorie parente"),
#     )

#     is_active = models.BooleanField(default=True, verbose_name=_("Active"))
#     order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     translations = TranslatedFields(
#         name=models.CharField(max_length=200, verbose_name=_("Nom")),
#         slug=models.SlugField(
#             max_length=220,
#             blank=True,
#             db_index=True,
#             verbose_name=_("Slug"),
#             help_text=_("Auto-généré si vide (par langue)."),
#         ),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#         seo_title=models.CharField(
#             max_length=255,
#             blank=True,
#             verbose_name=_("Titre SEO"),
#         ),
#         seo_description=models.CharField(
#             max_length=300,
#             blank=True,
#             verbose_name=_("Description SEO"),
#         ),
#     )

#     class TranslatedMeta:
#         # ✅ Slug unique par langue
#         unique_together = (("language_code", "slug"),)
#         indexes = (models.Index(fields=("language_code", "slug")),)

#     class Meta:
#         verbose_name = _("Catégorie")
#         verbose_name_plural = _("Catégories")
#         ordering = ["order", "id"]
#         indexes = [
#             models.Index(fields=["is_active", "order"]),
#             models.Index(fields=["parent", "order"]),
#             models.Index(fields=["code"]),
#         ]

#     def __str__(self) -> str:
#         name = self.safe_translation_getter("name", any_language=True) or f"Category #{self.pk}"
#         return f"{name} [{self.code}]" if self.code else name

#     # -------------------------
#     # Validation anti-cycles + normalisation code
#     # -------------------------
#     def clean(self):
#         super().clean()

#         # normalise code
#         if self.code:
#             self.code = self.code.strip().upper()
#             if not self.code:
#                 self.code = None

#         if self.parent_id and self.parent_id == self.pk:
#             raise ValidationError({"parent": _("Une catégorie ne peut pas être sa propre parente.")})

#         # évite les cycles : A -> B -> C -> A
#         seen = set()
#         node = self.parent
#         while node is not None:
#             if node.pk in seen:
#                 raise ValidationError({"parent": _("Boucle détectée dans la hiérarchie des catégories.")})
#             seen.add(node.pk)
#             node = node.parent

#     # -------------------------
#     # Slug auto par langue
#     # -------------------------
#     def save(self, *args, **kwargs):
#         # Normalise code avant save
#         if self.code:
#             self.code = self.code.strip().upper() or None

#         super().save(*args, **kwargs)

#         # Après le save principal, on peut corriger les slugs DB si besoin
#         self._ensure_translation_slugs()

#     def _ensure_translation_slugs(self):
#         """
#         Garantit slug (par langue) pour les traductions déjà enregistrées en DB.
#         """
#         Translation = self.translations.model
#         qs = Translation.objects.filter(master_id=self.pk)

#         to_update = []
#         for tr in qs:
#             if tr.slug or not tr.name:
#                 continue

#             base = slugify(tr.name)[:220] or f"category-{self.pk}"
#             slug = base
#             n = 2

#             # assure l'unicité par langue
#             while Translation.objects.filter(
#                 language_code=tr.language_code,
#                 slug=slug,
#             ).exclude(master_id=self.pk).exists():
#                 suffix = f"-{n}"
#                 slug = f"{base[: max(1, 220 - len(suffix))]}{suffix}"
#                 n += 1

#             tr.slug = slug
#             to_update.append(tr)

#         if to_update:
#             Translation.objects.bulk_update(to_update, ["slug"])

#     # Helpers pratiques
#     def is_root(self) -> bool:
#         return self.parent_id is None

#     def active_children(self):
#         return self.children.filter(is_active=True).order_by("order", "id")

#     def get_catcode(self) -> str:
#         """
#         Retourne le CATCODE (toujours MAJ). Utile dans les services SKU.
#         """
#         return (self.code or "").strip().upper()


# # -------------------------------------------------------------------
# # ✅ Signal: en admin Parler, la traduction peut être sauvée APRES l'objet.
# # => on garantit slug auto dès qu'une traduction est enregistrée.
# # -------------------------------------------------------------------
# @receiver(
#     post_save,
#     sender=Category.translations.model,
#     dispatch_uid="ecommerce_category_translation_autoslug",
# )
# def _category_translation_autoslug(sender, instance, **kwargs):
#     master = getattr(instance, "master", None)
#     if not master:
#         return
#     if instance.name and not instance.slug:
#         # bulk_update ne retrigger pas de post_save => pas de boucle
#         master._ensure_translation_slugs()





# # /economic/ecommerce/models/category.py
# from __future__ import annotations

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class Category(TranslatableModel):
#     # ✅ Force un PK auto (utile si ta DB a perdu le DEFAULT de la séquence)
#     id = models.BigAutoField(primary_key=True)

#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         related_name="children",
#         on_delete=models.SET_NULL,
#         verbose_name=_("Catégorie parente"),
#     )

#     is_active = models.BooleanField(default=True, verbose_name=_("Active"))
#     order = models.PositiveIntegerField(default=0, verbose_name=_("Ordre"))

#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))
#     updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Mis à jour le"))

#     translations = TranslatedFields(
#         name=models.CharField(max_length=200, verbose_name=_("Nom")),
#         slug=models.SlugField(
#             max_length=220,
#             blank=True,
#             db_index=True,
#             verbose_name=_("Slug"),
#             help_text=_("Auto-généré si vide (par langue)."),
#         ),
#         description=models.TextField(blank=True, verbose_name=_("Description")),
#         seo_title=models.CharField(
#             max_length=255,
#             blank=True,
#             verbose_name=_("Titre SEO"),
#         ),
#         seo_description=models.CharField(
#             max_length=300,
#             blank=True,
#             verbose_name=_("Description SEO"),
#         ),
#     )

#     class TranslatedMeta:
#         # ✅ Slug unique par langue
#         unique_together = (("language_code", "slug"),)
#         indexes = (models.Index(fields=("language_code", "slug")),)

#     class Meta:
#         verbose_name = _("Catégorie")
#         verbose_name_plural = _("Catégories")
#         ordering = ["order", "id"]
#         indexes = [
#             models.Index(fields=["is_active", "order"]),
#             models.Index(fields=["parent", "order"]),
#         ]

#     def __str__(self) -> str:
#         return self.safe_translation_getter("name", any_language=True) or f"Category #{self.pk}"

#     # -------------------------
#     # Validation anti-cycles
#     # -------------------------
#     def clean(self):
#         super().clean()
#         if self.parent_id and self.parent_id == self.pk:
#             raise ValidationError({"parent": _("Une catégorie ne peut pas être sa propre parente.")})

#         # évite les cycles : A -> B -> C -> A
#         seen = set()
#         node = self.parent
#         while node is not None:
#             if node.pk in seen:
#                 raise ValidationError({"parent": _("Boucle détectée dans la hiérarchie des catégories.")})
#             seen.add(node.pk)
#             node = node.parent

#     # -------------------------
#     # Slug auto par langue
#     # -------------------------
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         # Après le save principal, on peut corriger les slugs DB si besoin
#         self._ensure_translation_slugs()

#     def _ensure_translation_slugs(self):
#         """
#         Garantit slug (par langue) pour les traductions déjà enregistrées en DB.
#         (En admin Parler, les traductions sont souvent sauvegardées après l'objet : d'où le signal recommandé plus bas.)
#         """
#         Translation = self.translations.model
#         qs = Translation.objects.filter(master_id=self.pk)

#         to_update = []
#         for tr in qs:
#             if tr.slug or not tr.name:
#                 continue

#             base = slugify(tr.name)[:220] or f"category-{self.pk}"
#             slug = base
#             n = 2

#             # assure l'unicité par langue
#             while Translation.objects.filter(
#                 language_code=tr.language_code,
#                 slug=slug,
#             ).exclude(master_id=self.pk).exists():
#                 suffix = f"-{n}"
#                 slug = f"{base[: max(1, 220 - len(suffix))]}{suffix}"
#                 n += 1

#             tr.slug = slug
#             to_update.append(tr)

#         if to_update:
#             Translation.objects.bulk_update(to_update, ["slug"])

#     # Helpers pratiques
#     def is_root(self) -> bool:
#         return self.parent_id is None

#     def active_children(self):
#         return self.children.filter(is_active=True).order_by("order", "id")





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
#         # 1️⃣ On sauvegarde d'abord la catégorie pour avoir un PK
#         super().save(*args, **kwargs)

#         # 2️⃣ Ensuite seulement on manipule les traductions
#         # (sinon self.translations.all() plante sur un objet sans pk)
#         if not self.pk:
#             return

#         # Génération du slug par langue (django-parler safe)
#         for translation in self.translations.all():
#             if not translation.slug and translation.name:
#                 translation.slug = slugify(translation.name)
#                 translation.save()







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
