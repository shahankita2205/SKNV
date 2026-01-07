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
    'Faq',
]
