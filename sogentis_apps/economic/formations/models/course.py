# economic/formations/models/course.py
from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from parler.managers import TranslatableManager, TranslatableQuerySet
from django_ckeditor_5.fields import CKEditor5Field

from .base import TimeStampedModel
from .category import CourseCategory


class CourseQuerySet(TranslatableQuerySet):
    def active(self):
        return self.filter(is_active=True)

    def published(self):
        return self.active().filter(published_at__isnull=False)

    def featured(self):
        return self.published().filter(is_featured=True)


class Course(TimeStampedModel, TranslatableModel):
    """
    Formation (cours) multilingue.
    Online / Présentiel / Hybride.
    """

    class Type(models.TextChoices):
        ONLINE = "online", _("En ligne")
        ONSITE = "onsite", _("Présentiel")
        BLENDED = "blended", _("Hybride")

    class Level(models.TextChoices):
        BEGINNER = "beginner", _("Débutant")
        INTERMEDIATE = "intermediate", _("Intermédiaire")
        ADVANCED = "advanced", _("Avancé")

    class Currency(models.TextChoices):
        XOF = "XOF", "XOF"
        EUR = "EUR", "EUR"
        USD = "USD", "USD"

    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_("Titre")),
        short_description=models.CharField(max_length=320, blank=True, verbose_name=_("Résumé")),
        description=CKEditor5Field(verbose_name=_("Description"), blank=True),
    )

    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name=_("Domaine"),
    )

    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name=_("Slug"))

    type = models.CharField(max_length=20, choices=Type.choices, default=Type.ONLINE, verbose_name=_("Type"))
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER, verbose_name=_("Niveau"))

    # Langue “principale” (filtre rapide) — Parler gère les traductions
    language = models.CharField(max_length=20, default="FR", verbose_name=_("Langue"))

    duration_hours = models.PositiveIntegerField(default=0, verbose_name=_("Durée (heures)"))

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Prix"),
        help_text=_("Laisser vide ou 0 pour gratuit."),
    )
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.XOF, verbose_name=_("Devise"))

    start_date = models.DateField(null=True, blank=True, verbose_name=_("Date de début"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Date de fin"))
    location = models.CharField(max_length=255, blank=True, verbose_name=_("Lieu"))
    meeting_url = models.URLField(blank=True, verbose_name=_("Lien visio (optionnel)"))
    seat_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Places max"))

    cover_image = models.ImageField(
        upload_to="formations/courses/covers/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("Image de couverture"),
    )
    promo_video_url = models.URLField(blank=True, verbose_name=_("Vidéo promo (URL)"))

    is_featured = models.BooleanField(default=False, verbose_name=_("Mise en avant"))
    is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Publié le"))

    # ✅ Manager Parler + tes méthodes custom
    objects = TranslatableManager.from_queryset(CourseQuerySet)()

    class Meta:
        verbose_name = _("Formation")
        verbose_name_plural = _("Formations")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["is_active", "published_at"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["type"]),
            models.Index(fields=["level"]),
        ]

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or self.slug

    @property
    def level_label(self) -> str:
        return self.get_level_display()

    @property
    def is_free(self) -> bool:
        if self.price is None:
            return True
        try:
            return Decimal(self.price) <= 0
        except Exception:
            return True

    def save(self, *args, **kwargs):
        if not self.slug:
            title = self.safe_translation_getter("title", any_language=True)
            base = slugify(title) if title else "course"
            self.slug = base[:255]

            original = self.slug
            i = 2
            while Course.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original}-{i}"[:255]
                i += 1

        super().save(*args, **kwargs)





# # economic/formations/models/course.py
# from __future__ import annotations

# from decimal import Decimal

# from django.core.validators import MinValueValidator
# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .base import TimeStampedModel
# from .category import CourseCategory


# class CourseQuerySet(models.QuerySet):
#     def active(self):
#         return self.filter(is_active=True)

#     def published(self):
#         return self.active().filter(published_at__isnull=False)

#     def featured(self):
#         return self.published().filter(is_featured=True)


# class Course(TimeStampedModel, TranslatableModel):
#     """
#     Formation (cours) multilingue.
#     Online / Présentiel / Hybride.
#     Structure pédagogique: Course -> Module -> Lesson (TES fichiers).
#     Structure "cohorte": Course -> CourseSession (optionnel) -> Enrollment.
#     """

#     class Type(models.TextChoices):
#         ONLINE = "online", _("En ligne")
#         ONSITE = "onsite", _("Présentiel")
#         BLENDED = "blended", _("Hybride")

#     class Level(models.TextChoices):
#         BEGINNER = "beginner", _("Débutant")
#         INTERMEDIATE = "intermediate", _("Intermédiaire")
#         ADVANCED = "advanced", _("Avancé")

#     class Currency(models.TextChoices):
#         XOF = "XOF", "XOF"
#         EUR = "EUR", "EUR"
#         USD = "USD", "USD"

#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         short_description=models.CharField(max_length=320, blank=True, verbose_name=_("Résumé")),
#         description=CKEditor5Field(verbose_name=_("Description"), blank=True),
#     )

#     category = models.ForeignKey(
#         CourseCategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="courses",
#         verbose_name=_("Domaine"),
#     )

#     slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name=_("Slug"))

#     type = models.CharField(max_length=20, choices=Type.choices, default=Type.ONLINE, verbose_name=_("Type"))
#     level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER, verbose_name=_("Niveau"))

#     # Langue “principale” (filtre rapide) — parler gère les traductions
#     language = models.CharField(max_length=20, default="FR", verbose_name=_("Langue"))

#     duration_hours = models.PositiveIntegerField(default=0, verbose_name=_("Durée (heures)"))

#     price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         validators=[MinValueValidator(Decimal("0.00"))],
#         verbose_name=_("Prix"),
#         help_text=_("Laisser vide ou 0 pour gratuit."),
#     )
#     currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.XOF, verbose_name=_("Devise"))

#     # Hybride / présentiel (valeurs par défaut course; peuvent être override par session)
#     start_date = models.DateField(null=True, blank=True, verbose_name=_("Date de début"))
#     end_date = models.DateField(null=True, blank=True, verbose_name=_("Date de fin"))
#     location = models.CharField(max_length=255, blank=True, verbose_name=_("Lieu"))
#     meeting_url = models.URLField(blank=True, verbose_name=_("Lien visio (optionnel)"))
#     seat_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Places max"))

#     # média
#     cover_image = models.ImageField(
#         upload_to="formations/courses/covers/%Y/%m/",
#         null=True,
#         blank=True,
#         verbose_name=_("Image de couverture"),
#     )
#     promo_video_url = models.URLField(blank=True, verbose_name=_("Vidéo promo (URL)"))

#     is_featured = models.BooleanField(default=False, verbose_name=_("Mise en avant"))
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
#     published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Publié le"))

#     objects = CourseQuerySet.as_manager()

#     class Meta:
#         verbose_name = _("Formation")
#         verbose_name_plural = _("Formations")
#         ordering = ["-published_at", "-created_at"]
#         indexes = [
#             models.Index(fields=["is_active", "published_at"]),
#             models.Index(fields=["is_featured"]),
#             models.Index(fields=["type"]),
#             models.Index(fields=["level"]),
#         ]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or self.slug

#     @property
#     def level_label(self) -> str:
#         return self.get_level_display()

#     @property
#     def is_free(self) -> bool:
#         if self.price is None:
#             return True
#         try:
#             return Decimal(self.price) <= 0
#         except Exception:
#             return True

#     def save(self, *args, **kwargs):
#         """
#         Génère automatiquement un slug unique basé sur le titre traduit.
#         """
#         if not self.slug:
#             title = self.safe_translation_getter("title", any_language=True)
#             base = slugify(title) if title else "course"
#             self.slug = base[:255]

#             original = self.slug
#             i = 2
#             while Course.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
#                 self.slug = f"{original}-{i}"[:255]
#                 i += 1

#         super().save(*args, **kwargs)







# # economic/formations/models/course.py
# from decimal import Decimal
# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .base import TimeStampedModel
# from .category import CourseCategory


# class Course(TimeStampedModel, TranslatableModel):
#     """
#     Formation (cours) multilingue.
#     Peut être en ligne, en présentiel ou hybride.
#     """

#     class Type(models.TextChoices):
#         ONLINE = "online", _("En ligne")
#         ONSITE = "onsite", _("Présentiel")
#         BLENDED = "blended", _("Hybride")

#     class Level(models.TextChoices):
#         BEGINNER = "beginner", _("Débutant")
#         INTERMEDIATE = "intermediate", _("Intermédiaire")
#         ADVANCED = "advanced", _("Avancé")

#     translations = TranslatedFields(
#         title=models.CharField(
#             max_length=255,
#             verbose_name=_("Titre"),
#         ),
#         short_description=models.CharField(
#             max_length=320,
#             blank=True,
#             verbose_name=_("Résumé"),
#         ),
#         description=CKEditor5Field(
#             verbose_name=_("Description"),
#             blank=True,
#         ),
#     )

#     category = models.ForeignKey(
#         CourseCategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="courses",
#         verbose_name=_("Domaine"),
#     )

#     slug = models.SlugField(
#         max_length=255,
#         unique=True,
#         blank=True,
#         verbose_name=_("Slug"),
#     )

#     type = models.CharField(
#         max_length=20,
#         choices=Type.choices,
#         default=Type.ONLINE,
#         verbose_name=_("Type"),
#     )
#     level = models.CharField(
#         max_length=20,
#         choices=Level.choices,
#         default=Level.BEGINNER,
#         verbose_name=_("Niveau"),
#     )
#     language = models.CharField(
#         max_length=20,
#         default="FR",
#         verbose_name=_("Langue"),
#     )

#     duration_hours = models.PositiveIntegerField(
#         default=0,
#         verbose_name=_("Durée (heures)"),
#     )

#     price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         verbose_name=_("Prix"),
#         help_text=_("Laisser vide ou 0 pour gratuit."),
#     )

#     is_featured = models.BooleanField(
#         default=False,
#         verbose_name=_("Mise en avant"),
#     )
#     is_active = models.BooleanField(
#         default=True,
#         verbose_name=_("Actif"),
#     )
#     published_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         verbose_name=_("Publié le"),
#     )

#     class Meta:
#         verbose_name = _("Formation")
#         verbose_name_plural = _("Formations")
#         ordering = ["-published_at", "-created_at"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or self.slug

#     @property
#     def level_label(self) -> str:
#         return self.get_level_display()

#     @property
#     def is_free(self) -> bool:
#         if self.price is None:
#             return True
#         try:
#             return Decimal(self.price) <= 0
#         except Exception:
#             return True

#     def save(self, *args, **kwargs):
#         """
#         Génère automatiquement un slug unique basé sur le titre traduit.
#         """
#         if not self.slug:
#             title = self.safe_translation_getter("title", any_language=True)
#             base = slugify(title) if title else "course"
#             self.slug = base[:255]

#             original = self.slug
#             i = 2
#             while Course.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
#                 self.slug = f"{original}-{i}"[:255]
#                 i += 1

#         super().save(*args, **kwargs)






# # economic/formations/models/course.py
# from decimal import Decimal
# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field

# from .base import TimeStampedModel
# from .category import CourseCategory


# class Course(TimeStampedModel, TranslatableModel):
#     class Type(models.TextChoices):
#         ONLINE = "online", _("En ligne")
#         ONSITE = "onsite", _("Présentiel")
#         BLENDED = "blended", _("Hybride")

#     class Level(models.TextChoices):
#         BEGINNER = "beginner", _("Débutant")
#         INTERMEDIATE = "intermediate", _("Intermédiaire")
#         ADVANCED = "advanced", _("Avancé")

#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         short_description=models.CharField(max_length=320, blank=True, verbose_name=_("Résumé")),
#         description=CKEditor5Field(verbose_name=_("Description"), blank=True),
#     )

#     category = models.ForeignKey(
#         CourseCategory,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="courses",
#         verbose_name=_("Domaine"),
#     )

#     slug = models.SlugField(unique=True, blank=True, verbose_name=_("Slug"))

#     type = models.CharField(max_length=20, choices=Type.choices, default=Type.ONLINE, verbose_name=_("Type"))
#     level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER, verbose_name=_("Niveau"))
#     language = models.CharField(max_length=20, default="FR", verbose_name=_("Langue"))

#     duration_hours = models.PositiveIntegerField(default=0, verbose_name=_("Durée (heures)"))

#     price = models.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         verbose_name=_("Prix"),
#         help_text=_("Laisser vide ou 0 pour gratuit."),
#     )

#     is_featured = models.BooleanField(default=False, verbose_name=_("Mise en avant"))
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
#     published_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Publié le"))

#     class Meta:
#         verbose_name = _("Formation")
#         verbose_name_plural = _("Formations")
#         ordering = ["-published_at", "-created_at"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or self.slug

#     @property
#     def level_label(self):
#         return self.get_level_display()

#     @property
#     def is_free(self) -> bool:
#         if self.price is None:
#             return True
#         try:
#             return Decimal(self.price) <= 0
#         except Exception:
#             return True

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             title = self.safe_translation_getter("title", any_language=True)
#             base = slugify(title) if title else "course"
#             self.slug = base[:255]

#             original = self.slug
#             i = 2
#             while Course.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
#                 self.slug = f"{original}-{i}"[:255]
#                 i += 1

#         super().save(*args, **kwargs)








# from django.db import models
# from django.utils.text import slugify
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from django_ckeditor_5.fields import CKEditor5Field


# class Course(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=255, verbose_name=_("Titre")),
#         description=CKEditor5Field(verbose_name=_("Description")),
#     )

#     slug = models.SlugField(
#         unique=True,
#         blank=True,
#         verbose_name=_("Slug"),
#     )

#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Formation")
#         verbose_name_plural = _("Formations")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             title = self.safe_translation_getter("title", any_language=True)
#             if title:
#                 self.slug = slugify(title)
#         super().save(*args, **kwargs)







# # economic/formations/models/course.py
# from django.db import models
# from parler.models import TranslatableModel, TranslatedFields


# class Course(TranslatableModel):
#     is_active = models.BooleanField(default=True)

#     translations = TranslatedFields(
#         title=models.CharField(max_length=255),
#         description=models.TextField(blank=True),
#     )

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)
