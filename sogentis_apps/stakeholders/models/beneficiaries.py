from django.db import models

class Beneficiary(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=100)
    supported_since = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name
