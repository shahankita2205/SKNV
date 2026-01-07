"""
Gen AI Calling Models Module

Contains models related to gen ai calling

"""

from django.db import models
from decimal import Decimal


class PatientOutreach(models.Model):
    rxid = models.IntegerField()
    patient_firstname = models.TextField(blank=True, null=True)
    patient_lastname = models.TextField(blank=True, null=True)
    phonenumber = models.TextField(blank=True, null=True)
    prescriber_name = models.TextField(blank=True, null=True)
    rx_name = models.TextField(blank=True, null=True)
    rx_fillid = models.IntegerField()
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    remaining_refills = models.IntegerField(blank=True, null=True)
    address1 = models.TextField(blank=True, null=True)
    address2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    timezone = models.TextField(blank=True, null=True)
    patient_dob = models.TextField(blank=True, null=True)
    call_outcome = models.TextField(blank=True, null=True)
    outreach_attempt = models.IntegerField()
    request_id = models.TextField(blank=True, null=True)
    shipping_fee = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(max_length=20, default="pending")
    processed = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField()
    modified = models.DateTimeField(blank=True, null=True)
    call_summary = models.TextField(blank=True, null=True)
    call_back = models.BooleanField(default=False)
    patient_id = models.IntegerField()

    # Status choices for better validation and admin interface
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("retry", "Retry"),
    ]

    class Meta:
        managed = False
        db_table = "patient_outreach"
        unique_together = (("rx_fillid", "outreach_attempt"),)


class PatientCallQueue(models.Model):
    """
    Model for patient call queue table
    """

    patient_id = models.IntegerField()
    cybersource_customerid = models.CharField(max_length=100, blank=True, null=True)
    patient_firstname = models.CharField(max_length=100, blank=True, null=True)
    patient_lastname = models.CharField(max_length=100, blank=True, null=True)
    patient_dob = models.CharField(max_length=20, blank=True, null=True)
    phonenumber = models.CharField(max_length=20, blank=True, null=True)
    address1 = models.CharField(max_length=200, blank=True, null=True)
    address2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=10, blank=True, null=True)
    zip = models.CharField(max_length=20, blank=True, null=True)
    timezone = models.CharField(max_length=100, blank=True, null=True)
    rx_name = models.CharField(max_length=200, blank=True, null=True)
    rx_number = models.IntegerField(blank=True, null=True)
    rx_fillid = models.IntegerField(unique=True)
    outstanding_balance = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_refills = models.IntegerField(blank=True, null=True)
    balance_date = models.DateField()
    prescriber_name = models.CharField(max_length=200, blank=True, null=True)
    prescriber_npi = models.CharField(max_length=20, blank=True, null=True)
    txt_msg = models.TextField(blank=True, null=True)
    txt_error_message = models.TextField(blank=True, null=True)
    txt_error_code = models.CharField(max_length=20, blank=True, null=True)
    txt_date_sent = models.DateTimeField(blank=True, null=True)
    # text_delivery_failed is a computed column in the database - not included in model
    existing_outreach_attempt = models.IntegerField(blank=True, null=True)
    existing_outreach_date = models.DateTimeField(blank=True, null=True)
    existing_call_outcome = models.CharField(max_length=100, blank=True, null=True)
    queue_status = models.CharField(max_length=20, blank=True, null=True)
    priority_score = models.IntegerField(blank=True, null=True)
    pulled_at = models.DateTimeField(blank=True, null=True)
    pulled_by = models.CharField(max_length=100, blank=True, null=True)
    total_call_attempts = models.IntegerField(default=0)
    successful_contact_made = models.BooleanField(default=False)
    final_outcome = models.CharField(max_length=50, blank=True, null=True)
    final_outcome_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = "patient_call_queue"
        ordering = ["-priority_score", "created_at"]


__all__ = [
    "PatientCallQueue",
    "PatientOutreach",
]
