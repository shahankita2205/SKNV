"""
Reference Models Module

Contains models related to lookup/reference data:
- State
- Address
- Faq

Legacy Controller Mapping: StateController, AddressController, FaqController

Grouping Rationale: State, Address, and Faq are all lookup/reference data.
"""

from django.db import models
from datetime import datetime


class Faq(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=10485760, blank=True, null=True)
    answer = models.CharField(max_length=10485760, blank=True, null=True)
    category = models.CharField(max_length=10485760, blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "faq"


__all__ = [
    # 'State',
    # 'Address',
    "Faq",
]


class Address(models.Model):
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.TextField(blank=True, null=True)
    zip4 = models.CharField(max_length=5, blank=True, null=True)
    latlong = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "address"
