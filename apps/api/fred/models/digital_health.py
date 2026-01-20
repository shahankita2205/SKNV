"""
Digital Health Models Module

Contains models related to digital health features:
- DigitalHealth

Legacy Controller Mapping: DigitalHealthController
"""
from django.db import models

# TODO: Migrate digital health-related models from models.py


class DHSettings(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=False)

    class Meta:
        db_table = "dhsettings"
        managed = False 
        app_label = "fred" 

    def __str__(self):
        return self.name


__all__ = [
    "DHSettings",
]
