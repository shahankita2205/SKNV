"""
Gen AI Calling Serializers Module

Contains serializers related to gen ai calling domain.
"""

from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from fred.models import PatientCallQueue, PatientOutreach


class CallListSerializer(serializers.Serializer):
    """Serializer for call list data from multiple tables"""

    patient_firstname = serializers.CharField(max_length=255, allow_null=True)
    patient_lastname = serializers.CharField(max_length=255, allow_null=True)
    phonenumber = serializers.CharField(max_length=255, allow_null=True)
    prescriber_name = serializers.CharField(max_length=255, allow_null=True)
    rx_name = serializers.CharField(max_length=255, allow_null=True)
    rx_number = serializers.IntegerField()
    rx_fillid = serializers.IntegerField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    remaining_refills = serializers.IntegerField()
    address1 = serializers.CharField(max_length=255, allow_null=True)
    address2 = serializers.CharField(max_length=255, allow_null=True)
    city = serializers.CharField(max_length=255, allow_null=True)
    state = serializers.CharField(max_length=255, allow_null=True)
    zip = serializers.CharField(max_length=255, allow_null=True)
    timezone = serializers.CharField(max_length=255, allow_null=True)
    patient_dob = serializers.CharField(max_length=255, allow_null=True)
    outreach_attempt = serializers.IntegerField()
    outreach_attempt_date = serializers.DateTimeField(allow_null=True)
    call_outcome = serializers.CharField(max_length=255, allow_null=True)


class FredPatientOutreachSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientOutreach
        fields = "__all__"


class PatientOutreachCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating patient outreach records
    rxid will be provided via URL, not in request body
    """

    class Meta:
        model = PatientOutreach
        fields = [
            "patient_id",
            "patient_firstname",
            "patient_lastname",
            "phonenumber",
            "prescriber_name",
            "rx_name",
            "rx_fillid",
            "payment_amount",
            "remaining_refills",
            "address1",
            "address2",
            "city",
            "state",
            "zip",
            "timezone",
            "patient_dob",
            "call_outcome",
            "outreach_attempt",
            "request_id",
            "shipping_fee",
            "call_summary",
            "call_back",
        ]

    def validate_outreach_attempt(self, value):
        """Validate that outreach_attempt is a positive integer"""
        if value < 1:
            raise serializers.ValidationError("Outreach attempt must be greater than 0")
        return value

    def validate_payment_amount(self, value):
        """Validate payment amount if provided"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Payment amount cannot be negative")
        return value


class PatientOutreachStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating status and processed fields (for cronjob use)
    """

    class Meta:
        model = PatientOutreach
        fields = ["status", "processed"]

    def validate_status(self, value):
        """Validate status against allowed choices"""
        valid_statuses = [choice[0] for choice in PatientOutreach.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value


class PatientCallQueueSerializer(serializers.ModelSerializer):
    """Serializer for patient call queue data"""

    # Map outstanding_balance to cost for API response
    cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="outstanding_balance"
    )
    outreach_attempt = serializers.IntegerField(
        allow_null=True, required=False, source="existing_outreach_attempt"
    )
    outreach_attempt_date = serializers.DateTimeField(
        allow_null=True, required=False, source="existing_outreach_date"
    )
    call_outcome = serializers.CharField(
        max_length=100, allow_null=True, required=False, source="existing_call_outcome"
    )

    class Meta:
        model = PatientCallQueue
        fields = [
            "patient_id",
            "cybersource_customerid",
            "patient_firstname",
            "patient_lastname",
            "prescriber_name",
            "prescriber_npi",
            "phonenumber",
            "rx_name",
            "rx_number",
            "rx_fillid",
            "cost",
            "remaining_refills",
            "address1",
            "address2",
            "city",
            "state",
            "zip",
            "timezone",
            "patient_dob",
            "outreach_attempt",
            "outreach_attempt_date",
            "call_outcome",
            "queue_status",
            "priority_score",
            "pulled_at",
            "pulled_by",
        ]


class UpdatePatientCallQueueSerializer(serializers.Serializer):
    """Serializer for updating patient call queue data"""

    patient_id = serializers.IntegerField(required=False)
    cybersource_customerid = serializers.CharField(max_length=255, required=False)
    patient_firstname = serializers.CharField(max_length=255, required=False)
    patient_lastname = serializers.CharField(max_length=255, required=False)
    patient_dob = serializers.CharField(max_length=255, required=False)
    phonenumber = serializers.CharField(max_length=255, required=False)
    address1 = serializers.CharField(max_length=255, required=False)
    address2 = serializers.CharField(max_length=255, required=False)
    city = serializers.CharField(max_length=255, required=False)
    state = serializers.CharField(max_length=255, required=False)
    zip = serializers.CharField(max_length=255, required=False)
    timezone = serializers.CharField(max_length=255, required=False)
    rx_number = serializers.IntegerField(required=False)
    rx_fillid = serializers.IntegerField()
    outstanding_balance = serializers.IntegerField(required=False)
    remaining_refills = serializers.IntegerField(required=False)
    balance_date = serializers.DateTimeField(required=False)
    prescriber_name = serializers.CharField(max_length=255, required=False)
    prescriber_npi = serializers.CharField(max_length=255, required=False)
    txt_message = serializers.CharField(max_length=255, required=False)
    txt_error_message = serializers.CharField(max_length=255, required=False)
    txt_error_code = serializers.CharField(max_length=255, required=False)
    txt_date_sent = serializers.DateTimeField(required=False)
    text_delivery_failed = serializers.BooleanField(required=False)
    existing_outreach_attempt = serializers.IntegerField(required=False)
    existing_outreach_date = serializers.DateTimeField(required=False)
    existing_call_outcome = serializers.CharField(max_length=255, required=False)
    queue_status = serializers.CharField(max_length=255, required=False)
    priority_score = serializers.IntegerField(required=False)
    pulled_at = serializers.DateTimeField(required=False)
    pulled_by = serializers.CharField(max_length=255, required=False)
    total_call_attempts = serializers.IntegerField(required=False)
    successful_contact_made = serializers.BooleanField(required=False)
    final_outcome = serializers.CharField(max_length=255, required=False)
    final_outcome_notes = serializers.CharField(max_length=255, required=False)
    created_at = serializers.DateTimeField(required=False)
    updated_at = serializers.DateTimeField(required=False)

    def validate_rx_fillid(self, value):
        if not PatientCallQueue.objects.filter(rx_fillid__exact=value).exists():
            raise serializers.ValidationError(
                "rx_fillid does not exist in PatientCallQueue table"
            )
        return value


__all__ = [
    "CallListSerializer",
    "FredPatientOutreachSerializer",
    "PatientOutreachCreateSerializer",
    "PatientOutreachStatusUpdateSerializer",
    "PatientCallQueueSerializer",
    "UpdatePatientCallQueueSerializer",
]
