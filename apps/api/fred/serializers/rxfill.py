"""
RxFill Serializers and Services
"""

import logging
from typing import Optional, List, Dict, Any

from django.db import transaction
from rest_framework import serializers

from fred.models.models import Rx, Rxfill, Patient, Medication, Payment
from fred.models.doctor import Doctor

logger = logging.getLogger(__name__)


class RxFillErrorCodes:
    ERROR_FILL_NOT_FOUND = 21001
    ERROR_UNABLE_CREATE_FILL = 21002
    ERROR_UNABLE_UPDATE_FILL = 21003


class RxFillServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class RxFillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxfill
        fields = "__all__"


class RxFillListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxfill
        fields = [
            "id",
            "rxid",
            "status",
            "type",
            "paymentid",
            "shipmentid",
            "created",
            "modified",
        ]


class RxFillService:

    @staticmethod
    def get_one(fill_id: int) -> Rxfill:
        try:
            return Rxfill.objects.using("fred").get(pk=fill_id)
        except Rxfill.DoesNotExist:
            raise RxFillServiceException(
                f"Fill #{fill_id} not found", RxFillErrorCodes.ERROR_FILL_NOT_FOUND
            )

    @staticmethod
    def get_all_by_rx(rx_id: int):
        return Rxfill.objects.using("fred").filter(rxid=rx_id).order_by("-created")

    @staticmethod
    def get_unpaid_fills_by_office(
        office_id: int, include_hipaa: bool = False
    ) -> List[Dict[str, Any]]:
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid=office_id)
            .values_list("id", flat=True)
        )

        fills = Rxfill.objects.using("fred").filter(
            rxid__in=list(rx_ids), status="paymentHold", type="newrx"
        )

        results = []
        for fill in fills:
            try:
                rx = Rx.objects.using("fred").get(pk=fill.rxid)
            except Rx.DoesNotExist:
                continue

            fill_data = {
                "fill": RxFillListSerializer(fill).data,
                "rx": {
                    "id": rx.id,
                    "status": rx.status,
                    "qty": rx.qty,
                    "refills": rx.refills,
                    "medicationid": rx.medicationid,
                    "created": rx.created.isoformat() if rx.created else None,
                },
            }

            if include_hipaa and rx.patientid:
                try:
                    patient = Patient.objects.using("fred").get(pk=rx.patientid)
                    fill_data["patient"] = {
                        "id": patient.id,
                        "name": patient.name
                        or f"{patient.firstname or ''} {patient.lastname or ''}".strip(),
                        "phone": patient.phone,
                        "dob": patient.dob,
                    }
                except Patient.DoesNotExist:
                    pass

            results.append(fill_data)

        return results

    @staticmethod
    def get_pending_fills_by_office(office_id: int) -> List[Dict[str, Any]]:
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid=office_id)
            .values_list("id", flat=True)
        )

        pending_fills = (
            Rxfill.objects.using("fred")
            .filter(rxid__in=list(rx_ids), status__in=["pending", "paymentHold", "new"])
            .order_by("-created")
        )

        results = []
        for fill in pending_fills:
            try:
                rx = Rx.objects.using("fred").get(pk=fill.rxid)
            except Rx.DoesNotExist:
                continue

            fill_data = {
                "fillId": fill.id,
                "fillStatus": fill.status,
                "fillCreated": fill.created.isoformat() if fill.created else None,
                "fillType": fill.type,
                "rx": {
                    "id": rx.id,
                    "status": rx.status,
                    "qty": rx.qty,
                    "refills": rx.refills,
                    "medicationid": rx.medicationid,
                    "created": rx.created.isoformat() if rx.created else None,
                },
                "patient": None,
                "doctor": None,
                "medication": None,
            }

            if rx.patientid:
                try:
                    patient = Patient.objects.using("fred").get(pk=rx.patientid)
                    fill_data["patient"] = {
                        "id": patient.id,
                        "name": patient.name
                        or f"{patient.firstname or ''} {patient.lastname or ''}".strip(),
                        "phone": patient.phone,
                    }
                except Patient.DoesNotExist:
                    pass

            if rx.doctorid:
                try:
                    doctor = Doctor.objects.using("fred").get(pk=rx.doctorid)
                    fill_data["doctor"] = {
                        "id": doctor.id,
                        "name": doctor.name,
                        "npi": doctor.npi,
                    }
                except Doctor.DoesNotExist:
                    pass

            if rx.medicationid:
                try:
                    med = Medication.objects.using("fred").get(ndc=rx.medicationid)
                    fill_data["medication"] = {
                        "ndc": med.ndc,
                        "formula": med.formula,
                        "brand_name": med.brand_name,
                    }
                except Medication.DoesNotExist:
                    pass

            results.append(fill_data)

        return results

    @staticmethod
    def get_paid_fills_by_office(
        office_id: int, limit: int = 100
    ) -> List[Dict[str, Any]]:
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid=office_id)
            .values_list("id", flat=True)
        )

        paid_fills = (
            Rxfill.objects.using("fred")
            .filter(rxid__in=list(rx_ids), paymentid__isnull=False)
            .order_by("-created")[:limit]
        )

        results = []
        for fill in paid_fills:
            try:
                rx = Rx.objects.using("fred").get(pk=fill.rxid)
            except Rx.DoesNotExist:
                continue

            fill_data = {
                "fillId": fill.id,
                "fillStatus": fill.status,
                "fillCreated": fill.created.isoformat() if fill.created else None,
                "rx": {"id": rx.id, "status": rx.status, "qty": rx.qty},
                "patient": None,
                "medication": None,
                "payment": None,
            }

            if rx.patientid:
                try:
                    patient = Patient.objects.using("fred").get(pk=rx.patientid)
                    fill_data["patient"] = {
                        "id": patient.id,
                        "name": patient.name
                        or f"{patient.firstname or ''} {patient.lastname or ''}".strip(),
                    }
                except Patient.DoesNotExist:
                    pass

            if rx.medicationid:
                try:
                    med = Medication.objects.using("fred").get(ndc=rx.medicationid)
                    fill_data["medication"] = {
                        "ndc": med.ndc,
                        "formula": med.formula,
                        "brand_name": med.brand_name,
                    }
                except Medication.DoesNotExist:
                    pass

            if fill.paymentid:
                try:
                    payment = Payment.objects.using("fred").get(pk=fill.paymentid)
                    fill_data["payment"] = {
                        "id": payment.id,
                        "amount": payment.amount,
                        "status": payment.status,
                        "created": (
                            payment.created.isoformat() if payment.created else None
                        ),
                    }
                except Payment.DoesNotExist:
                    pass

            results.append(fill_data)

        return results

    @staticmethod
    def get_shipment_count_by_office(office_id: int) -> int:
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid=office_id)
            .values_list("id", flat=True)
        )
        return (
            Rxfill.objects.using("fred")
            .filter(rxid__in=list(rx_ids), shipmentid__isnull=False)
            .count()
        )


__all__ = [
    "RxFillErrorCodes",
    "RxFillServiceException",
    "RxFillSerializer",
    "RxFillListSerializer",
    "RxFillService",
]
