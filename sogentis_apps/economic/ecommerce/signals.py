# economic/ecommerce/signals.py
from __future__ import annotations

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from economic.ecommerce.models.category import Category


@receiver(pre_save, sender=Category.translations.model)
def autoslug_category_translation(sender, instance, **kwargs):
    if instance.slug or not instance.name:
        return

    base = slugify(instance.name)[:220] or "category"
    slug = base
    n = 2

    qs = sender.objects.filter(language_code=instance.language_code, slug=slug)
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)

    while qs.exists():
        suffix = f"-{n}"
        slug = f"{base[: max(1, 220 - len(suffix))]}{suffix}"
        n += 1
        qs = sender.objects.filter(language_code=instance.language_code, slug=slug)
        if instance.pk:
            qs = qs.exclude(pk=instance.pk)

    instance.slug = slug
