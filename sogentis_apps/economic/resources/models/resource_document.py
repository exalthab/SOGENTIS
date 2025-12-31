# economic/resources/models/resource_document.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class ResourceDocument(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("UUID"),
    )

    resource = models.ForeignKey(
        "resources.ResourceMod",  # ✅ STRING REFERENCE
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Ressource"),
    )

    title = models.CharField(max_length=255, verbose_name=_("Titre"))
    file = models.FileField(
        upload_to="resources/documents/%Y/%m/",
        verbose_name=_("Fichier"),
    )
    is_public = models.BooleanField(default=True, verbose_name=_("Public"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title









# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# from .resource_mod import ResourceMod


# class ResourceDocument(models.Model):
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_("UUID"))

#     resource = models.ForeignKey(
#         ResourceMod,
#         on_delete=models.CASCADE,
#         related_name="documents",
#         verbose_name=_("Ressource"),
#     )

#     title = models.CharField(max_length=255, verbose_name=_("Titre"))
#     file = models.FileField(upload_to="resources/documents/%Y/%m/", verbose_name=_("Fichier"))
#     is_public = models.BooleanField(default=True, verbose_name=_("Public"))
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = _("Document")
#         verbose_name_plural = _("Documents")
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.title
