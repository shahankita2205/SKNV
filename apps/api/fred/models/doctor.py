"""
Doctor Model

Fully migrated from PHP Doctor entity.
This is the single source of truth for the Doctor model.

Database Table: doctor
Database Alias: fred
"""

from django.db import models


class Doctor(models.Model):
    """
    Doctor model representing prescribing physicians.

    PHP Equivalent: app/Entities/Doctor.php

    Attributes:
        id: Primary key
        name: Full name (legacy field)
        phone: Phone number
        email: Email address
        dea: DEA number
        npi: National Provider Identifier (10 digits)
        spi: Secondary Provider Identifier
        created: Creation timestamp
        prefix: Name prefix (Dr., Mr., etc.)
        firstname: First name
        middlename: Middle name
        lastname: Last name
        suffix: Name suffix (MD, PhD, etc.)
        pin: PIN for authentication
        pharmetikaid: Pharmetika system ID
        approval: Approval status
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    dea = models.CharField(max_length=50, blank=True, null=True)
    npi = models.CharField(max_length=50, blank=True, null=True)
    spi = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    prefix = models.CharField(max_length=20, blank=True, null=True)
    firstname = models.CharField(max_length=100, blank=True, null=True)
    middlename = models.CharField(max_length=100, blank=True, null=True)
    lastname = models.CharField(max_length=100, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    pin = models.CharField(max_length=50, blank=True, null=True)
    pharmetikaid = models.CharField(max_length=50, blank=True, null=True)
    approval = models.BooleanField(default=True, blank=True, null=True)

    class Meta:
        managed = False  # Django won't create/modify this table
        db_table = "doctor"
        ordering = ["id"]

    def __str__(self):
        return self.display_name

    @property
    def full_name(self) -> str:
        """
        Get full name from name parts.

        Returns:
            str: Concatenated name parts or legacy name field
        """
        parts = [
            self.prefix,
            self.firstname,
            self.middlename,
            self.lastname,
            self.suffix,
        ]
        full = " ".join(filter(None, parts))
        return full if full else (self.name or "")

    @property
    def display_name(self) -> str:
        """
        Get display name (full_name or name).

        Returns:
            str: Best available name for display
        """
        return self.full_name or self.name or f"Doctor #{self.id}"

    @property
    def has_valid_npi(self) -> bool:
        """
        Check if doctor has a valid 10-digit NPI.

        Returns:
            bool: True if NPI is exactly 10 digits
        """
        import re

        if not self.npi:
            return False
        return bool(re.match(r"^\d{10}$", str(self.npi)))
