"""
Logs Models Module

Contains models related to audit and logging:
- Log
- FailedFulfillLog

Legacy Controller Mapping: LogsController, FailedfulfilllogController

Grouping Rationale: Logs and FailedFulfillLog are both audit/logging domain.
"""
from django.db import models


class Failedfulfilllog(models.Model):
    rxid = models.CharField(max_length=255)
    rxfillid = models.CharField(max_length=255)
    fulfillmentpartner = models.CharField(max_length=255)
    log = models.TextField()
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "failedfulfilllog"

__all__ = [
    # 'Log',
    'Failedfulfilllog',
]
