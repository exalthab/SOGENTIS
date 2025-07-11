from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now


class Service(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="economic/services/", blank=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('gestion_projets:service_detail', args=[self.slug])  # ✅ corrigé ici

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
