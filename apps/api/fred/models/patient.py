"""
Patient Models Module

Contains models related to patient management:
- Patient
- PatientAddress
- PatientInsurance

Legacy Controller Mapping: PatientController
"""

from django.db import models
from fred.models import reference
from datetime import datetime


# TODO: Migrate patient-related models from models.py
# Example structure:
#
# class Patient(models.Model):
#     """Patient model"""
#     pass
#
# class PatientAddress(models.Model):
#     """Patient address model"""
#     pass
#
# class PatientInsurance(models.Model):
#     """Patient insurance model"""
#     pass

__all__ = [
    # 'Patient',
    # 'PatientAddress',
    # 'PatientInsurance',
]


class Patient(models.Model):
    # addressid = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    dob = models.TextField(blank=True, null=True)
    gender = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True, default="5555555555")
    email = models.TextField(blank=True, null=True, default="no@email.com")
    allergies = models.TextField(blank=True, null=True, default="n/a")
    otherdrugs = models.TextField(blank=True, null=True, default="n/a")
    otherinfo = models.TextField(blank=True, null=True, default="n/a")
    created = models.DateTimeField(auto_now_add=True)
    pregnant = models.BooleanField(blank=True, null=True)
    prefix = models.TextField(blank=True, null=True, default="")
    firstname = models.TextField(blank=True, null=True, default="")
    middlename = models.TextField(blank=True, null=True, default="")
    lastname = models.TextField(blank=True, null=True, default="")
    suffix = models.TextField(blank=True, null=True, default="")
    userid = models.IntegerField(blank=True, null=True)
    pharmetikaid = models.IntegerField(blank=True, null=True)

    addressid = models.ForeignKey(
        reference.Address, on_delete=models.SET_NULL, null=True, db_column="addressid"
    )

    def save(self, *args, **kwargs):
        self.name = f"{self.firstname} {self.lastname}"
        super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = "patient"
