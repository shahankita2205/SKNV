from django.db import models


class Officetype(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = "officetype"
