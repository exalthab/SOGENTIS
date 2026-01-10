# social/models/document.py

from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    # ... other fields

