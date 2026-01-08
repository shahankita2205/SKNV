"""
Payment Serializers and Services
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from django.db import transaction
from rest_framework import serializers

from fred.models.models import Payment, Patientmeta, Patient

logger = logging.getLogger(__name__)


class PaymentErrorCodes:
    ERROR_PAYMENT_NOT_FOUND = 19001
    ERROR_UNABLE_CREATE_PAYMENT = 19002
    ERROR_UNABLE_UPDATE_PAYMENT = 19003
    ERROR_PATIENT_META_NOT_FOUND = 19004


class PaymentServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "officeid",
            "patientid",
            "amount",
            "status",
            "type",
            "txid",
            "created",
            "modified",
        ]


class PatientMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patientmeta
        fields = "__all__"


class PaymentService:

    @staticmethod
    def get_one(payment_id: int) -> Payment:
        try:
            return Payment.objects.using("fred").get(pk=payment_id)
        except Payment.DoesNotExist:
            raise PaymentServiceException(
                f"Payment #{payment_id} not found",
                PaymentErrorCodes.ERROR_PAYMENT_NOT_FOUND,
            )

    @staticmethod
    def get_one_no_exception(payment_id: int) -> Optional[Payment]:
        try:
            return Payment.objects.using("fred").get(pk=payment_id)
        except Payment.DoesNotExist:
            return None

    @staticmethod
    def get_all_by_office(office_id: int, current_month_only: bool = False):
        queryset = (
            Payment.objects.using("fred")
            .filter(officeid=office_id)
            .exclude(status="refunded")
        )

        if current_month_only:
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(created__gte=month_start)

        return queryset

    @staticmethod
    def get_one_patient_meta_by_payment(payment_id: int) -> Patientmeta:
        try:
            return Patientmeta.objects.using("fred").get(paymentid=payment_id)
        except Patientmeta.DoesNotExist:
            raise PaymentServiceException(
                f"Patient Meta for Payment #{payment_id} not found",
                PaymentErrorCodes.ERROR_PATIENT_META_NOT_FOUND,
            )

    @staticmethod
    def get_one_patient_meta_by_payment_no_exception(
        payment_id: int,
    ) -> Optional[Patientmeta]:
        try:
            return Patientmeta.objects.using("fred").get(paymentid=payment_id)
        except Patientmeta.DoesNotExist:
            return None

    @staticmethod
    def get_pending_by_office(office_id: int) -> List[Dict[str, Any]]:
        pending_payments = (
            Payment.objects.using("fred")
            .filter(officeid=office_id, status__in=["pending", "hold", "processing"])
            .order_by("-created")
        )

        results = []
        for payment in pending_payments:
            payment_data = {
                "id": payment.id,
                "amount": payment.amount,
                "status": payment.status,
                "type": payment.type,
                "txid": payment.txid,
                "created": payment.created.isoformat() if payment.created else None,
                "patient": None,
                "patientMeta": None,
            }

            if payment.patientid:
                try:
                    patient = Patient.objects.using("fred").get(pk=payment.patientid)
                    payment_data["patient"] = {
                        "id": patient.id,
                        "name": patient.name
                        or f"{patient.firstname or ''} {patient.lastname or ''}".strip(),
                        "phone": patient.phone,
                        "email": patient.email,
                    }
                except Patient.DoesNotExist:
                    pass

            patient_meta = PaymentService.get_one_patient_meta_by_payment_no_exception(
                payment.id
            )
            if patient_meta:
                payment_data["patientMeta"] = {
                    "id": patient_meta.id,
                    "qty": patient_meta.qty,
                    "dob": patient_meta.dob,
                    "phone": patient_meta.phone,
                }

            results.append(payment_data)

        return results

    @staticmethod
    def move_payment(
        payment_id: int, from_office_id: int, to_office_id: int
    ) -> Dict[str, Any]:
        payment = PaymentService.get_one(payment_id)

        if payment.officeid != from_office_id:
            raise PaymentServiceException(
                f"Payment #{payment_id} does not belong to office #{from_office_id}",
                PaymentErrorCodes.ERROR_PAYMENT_NOT_FOUND,
            )

        with transaction.atomic(using="fred"):
            payment.officeid = to_office_id
            payment.save(using="fred")
            logger.info(
                f"Payment #{payment_id} moved from office #{from_office_id} to #{to_office_id}"
            )

        return {
            "paymentId": payment_id,
            "fromOfficeId": from_office_id,
            "toOfficeId": to_office_id,
            "success": True,
        }

    @staticmethod
    def calculate_total_revenue(office_id: int) -> float:
        payments = (
            Payment.objects.using("fred")
            .filter(officeid=office_id)
            .exclude(status="refunded")
            .values_list("amount", flat=True)
        )

        total = 0.0
        for amt in payments:
            try:
                if amt:
                    total += float(amt)
            except (ValueError, TypeError):
                pass

        return total


__all__ = [
    "PaymentErrorCodes",
    "PaymentServiceException",
    "PaymentSerializer",
    "PaymentListSerializer",
    "PatientMetaSerializer",
    "PaymentService",
]
