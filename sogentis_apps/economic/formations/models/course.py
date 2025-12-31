# economic/formations/models/course.py
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from django_ckeditor_5.fields import CKEditor5Field


class Course(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=255, verbose_name=_("Titre")),
        description=CKEditor5Field(verbose_name=_("Description")),
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Formation")
        verbose_name_plural = _("Formations")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            title = self.safe_translation_getter("title", any_language=True)
            if title:
                self.slug = slugify(title)
        super().save(*args, **kwargs)







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
