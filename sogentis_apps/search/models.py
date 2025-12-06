from django.db import models
from django.conf import settings
from django.utils import timezone

class IndexedDocument(models.Model):
    """
    Modèle générique stockant un index simple pour la recherche.
    Nous conservons un lien vers la source par (source_app, source_model, object_id)
    pour être résilient si ton modèle source est ailleurs.
    """
    source_app = models.CharField(max_length=100, blank=True, help_text="App label of source model")
    source_model = models.CharField(max_length=100, blank=True, help_text="Model name of source")
    object_id = models.BigIntegerField(null=True, blank=True, help_text="PK of the source object")

    title = models.CharField(max_length=512, blank=True)
    description = models.TextField(blank=True)
    body = models.TextField(blank=True, help_text="Extracted text from file (if any)")
    file_url = models.CharField(max_length=1000, blank=True, help_text="Path or URL to file")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # metadata for ranking / counters
    purchase_counter = models.IntegerField(default=0)
    download_tokens = models.IntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        if self.title:
            return self.title
        return f"IndexedDocument {self.pk} ({self.source_app}.{self.source_model}:{self.object_id})"
