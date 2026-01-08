"""
Rx (Prescription) Serializers and Services
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from django.db import connections
from django.db.models import Count
from rest_framework import serializers

from fred.models.models import Rx, Medication
from fred.models.doctor import Doctor
from django.forms.models import model_to_dict

logger = logging.getLogger(__name__)


class RxErrorCodes:
    ERROR_RX_NOT_FOUND = 20001
    ERROR_UNABLE_CREATE_RX = 20002
    ERROR_UNABLE_UPDATE_RX = 20003


class RxServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class RxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rx
        fields = "__all__"


class RxListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rx
        fields = [
            "id",
            "officeid",
            "patientid",
            "doctorid",
            "medicationid",
            "status",
            "qty",
            "refills",
            "sig",
            "notes",
            "created",
            "received",
        ]


class RxDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    qty = serializers.IntegerField()
    refills = serializers.IntegerField()
    sig = serializers.CharField()
    notes = serializers.CharField()
    created = serializers.DateTimeField()
    received = serializers.DateTimeField()
    medicationid = serializers.CharField()
    patient = serializers.DictField(required=False, allow_null=True)
    doctor = serializers.DictField(required=False, allow_null=True)
    medication = serializers.DictField(required=False, allow_null=True)


class RxService:

    @staticmethod
    def get_one(rx_id: int) -> Rx:
        try:
            return Rx.objects.using("fred").get(pk=rx_id)
        except Rx.DoesNotExist:
            raise RxServiceException(
                f"Prescription #{rx_id} not found", RxErrorCodes.ERROR_RX_NOT_FOUND
            )

    @staticmethod
    def get_one_no_exception(rx_id: int) -> Optional[Rx]:
        try:
            return Rx.objects.using("fred").get(pk=rx_id)
        except Rx.DoesNotExist:
            return None

    @staticmethod
    def get_all_by_office(office_id: int, current_month_only: bool = False):
        queryset = Rx.objects.using("fred").filter(officeid=office_id)

        if current_month_only:
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(received__gte=month_start)

        return queryset

    @staticmethod
    def get_rx_by_office(office_id, start=None, end=None, kind=None):
        sql = """
            SELECT
                rx.id              AS rx_id,
                rx.created         AS rx_created,
                rx.qty             AS rx_qty,
                rx.status          AS rx_status,

                fill.type          AS fill_type,
                fill.status        AS fill_status,
                fill.paymentid     AS paymentid,
                fill.shipmentid    AS shipmentid,

                med.formulacode    AS formulacode,

                doc.name           AS doctor_name,

                patient.firstname  AS firstname,
                patient.lastname   AS lastname,
                patient.dob        AS dob,
                patient.phone      AS phone,

                pay.amount         AS payment_amount,
                pay.created        AS payment_created,

                ship.tracking      AS tracking,
                ship.created       AS shipment_created,

                raw.payload        AS raw_payload
            FROM rx
            LEFT JOIN rxfill fill ON rx.id = fill.rxid
            LEFT JOIN medication med ON med.ndc = rx.medicationid
            LEFT JOIN doctor doc ON doc.id = rx.doctorid
            LEFT JOIN payment pay ON pay.id = fill.paymentid
            LEFT JOIN shipment ship ON ship.id = fill.shipmentid
            LEFT JOIN patient patient ON patient.id = rx.patientid
            LEFT JOIN rxraw raw ON rx.rxrawid = raw.id
            WHERE rx.officeid = %s
        """

        params = [office_id]

        if start:
            if kind == "rx":
                sql += " AND fill.created > %s"
            elif kind == "payment":
                sql += " AND pay.created > %s"
            elif kind == "shipment":
                sql += " AND ship.created > %s"
            params.append(start)

        if end:
            if kind == "rx":
                sql += " AND fill.created < %s"
            elif kind == "payment":
                sql += " AND pay.created < %s"
            elif kind == "shipment":
                sql += " AND ship.created < %s"
            params.append(end)

        sql += " ORDER BY rx.id ASC"

        with connections["fred"].cursor() as cursor:
            cursor.execute(sql, params)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()

        return [dict(zip(cols, r)) for r in rows]

    @staticmethod
    def patient_initials(first, last):
        return f"{first[0]}. {last[0]}." if first and last else ""

    @staticmethod
    def format_phone(phone):
        if phone and len(phone) == 10:
            return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
        return phone

    @staticmethod
    def format_dob(dob):
        # PHP returns MM/DD/YYYY
        if dob and len(dob) == 8:  # YYYYMMDD
            return f"{dob[4:6]}/{dob[6:]}/{dob[:4]}"
        return dob

    @staticmethod
    def map_fill_type(fill_type):
        return {
            "newrx": "New",
            "refill": "Refill",
            "corrector": "Corrector",
        }.get(fill_type, "")

    @staticmethod
    def map_fill_status(status):
        return {
            "paymentHold": "Unpaid",
            "medNotFound": "RPh review",
            "toFill": "To be filled",
            "inFill": "Dispensing",
            "shipped": "Shipped",
            "verifyInOfficeDispenseNoOffice": "DIO No Office",
            "dispensedInOffice": "DIO",
            "verifyQty": "Verify Qty",
            "needsApproval": "Bulk Approval",
            "cancelled": "Cancelled",
            "other": "Other",
        }.get(status, status)

    @staticmethod
    def build_rx_response(rxs, payments, shipments, role, no_drilldown):
        result = {
            "rxs": [],
            "payments": [],
            "shipments": [],
            "med": [],
        }

        # ---------------- RX TABLE ----------------
        last_rx = None
        temp = None

        for row in rxs:
            rx_id = row["rx_id"]
            created = row["rx_created"]

            unix = int(created.timestamp())
            date_col = (
                f"<span class='d-none'>{unix}</span>" f"{created.strftime('%m/%d/%Y')}"
            )

            rx_link = (
                rx_id
                if no_drilldown
                else f'<a href="/rx/view?id={rx_id}" target="_blank">{rx_id}</a>'
            )

            pat_init = RxService.patient_initials(row["firstname"], row["lastname"])

            phone = RxService.format_phone(row["phone"])
            dob = RxService.format_dob(row["dob"])

            medication = f"{row['rx_qty']} x {row['formulacode']}"

            paid = (
                "<span class='green'>Yes</span>"
                if row["paymentid"]
                else "<span class='red'>No</span>"
            )
            shipped = (
                "<span class='green'>Yes</span>"
                if row["shipmentid"]
                else "<span class='red'>No</span>"
            )

            fill_type = RxService.map_fill_type(row["fill_type"])
            status = RxService.map_fill_status(row["fill_status"])

            details_btn = (
                f'<button type="button" class="btn btn-sm btn-secondary" '
                f'onClick="showRxDetails({rx_id})">Details</button>'
            )

            if rx_id != last_rx:
                if temp:
                    result["rxs"].append(temp)

                temp = [
                    date_col,  # 0
                    rx_link,  # 1
                    pat_init,  # 2
                    dob,  # 3
                    phone,  # 4
                    row["doctor_name"],  # 5
                    medication,  # 6
                    fill_type,  # 7
                    paid,  # 8
                    shipped,  # 9
                    status,  # 10
                    details_btn,  # 11
                ]

                last_rx = rx_id
            else:
                temp[7] += "<br>" + fill_type
                temp[8] += "<br>" + paid
                temp[9] += "<br>" + shipped
                temp[10] += "<br>" + status

        if temp:
            result["rxs"].append(temp)

        # ---------------- PAYMENTS TABLE ----------------
        seen_payments = set()

        for row in payments:
            pay_id = row.get("paymentid")
            if not pay_id or pay_id in seen_payments:
                continue

            seen_payments.add(pay_id)

            created = row["payment_created"]
            unix = int(created.timestamp())

            date_col = (
                f"<span class='d-none'>{unix}</span>"
                f'<a href="/payments/view?id={pay_id}" target="_blank">'
                f"{created.strftime('%m/%d/%Y')}</a>"
            )

            result["payments"].append(
                [
                    date_col,
                    "",
                    f"${row.get('payment_amount', '0.00')}",
                    RxService.patient_initials(row["firstname"], row["lastname"]),
                    RxService.format_dob(row["dob"]),
                    RxService.format_phone(row["phone"]),
                    f'<a href="/rx/view?id={row["rx_id"]}" target="_blank">{row["rx_id"]}</a>',
                    row["doctor_name"],
                    f'{row["rx_qty"]} x {row["formulacode"]}',
                    f'<button type="button" class="btn btn-sm btn-secondary" '
                    f'onClick="showRxDetails({row["rx_id"]})">Details</button>',
                ]
            )

        # ---------------- SHIPMENTS (OPTIONAL / EMPTY FOR NOW) ----------------
        # Can be added exactly like PHP when needed

        return result

    @staticmethod
    def get_medications_by_office(
        office_id: int,
        start=None,
        end=None,
    ):
        qs = Rx.objects.using("fred").filter(
            officeid=office_id,
            medicationid__isnull=False,
        )

        if start:
            qs = qs.filter(created__gt=start)
        if end:
            qs = qs.filter(created__lt=end)

        meds = qs.values("medicationid").annotate(qty=Count("id"))

        response = []

        for row in meds:
            ndc = row["medicationid"]

            med = Medication.objects.using("fred").filter(ndc=ndc).first()

            if med:
                label = (
                    f"{med.ndc}: {med.brand_name}"
                    f"<br><small>"
                    f"{med.formulacode} "
                    f"{med.formula} "
                    f"{med.size} "
                    f"{med.dosage}"
                    f"</small>"
                )
            else:
                label = f"{ndc}: <br><small></small>"

            response.append([row["qty"], label])

        return response

    @staticmethod
    def get_prescribers_by_office(office_id: int) -> List[Dict[str, Any]]:
        doctor_stats = (
            Rx.objects.using("fred")
            .filter(officeid=office_id, doctorid__isnull=False)
            .values("doctorid")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        prescribers = []
        for stat in doctor_stats:
            try:
                doctor = Doctor.objects.using("fred").get(pk=stat["doctorid"])
                prescribers.append(
                    {
                        stat["count"],
                        doctor.name,
                    }
                )
            except Doctor.DoesNotExist:
                continue

        return prescribers

    @staticmethod
    def get_patients_by_office(office_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                p.id           AS p_id,
                p.addressid    AS p_addressid,
                p.name         AS p_name,
                p.dob          AS p_dob,
                p.gender       AS p_gender,
                p.phone        AS p_phone,
                p.email        AS p_email,
                p.allergies    AS p_allergies,
                p.otherdrugs   AS p_otherdrugs,
                p.otherinfo    AS p_otherinfo,
                p.created      AS p_created,
                p.pregnant     AS p_pregnant,
                p.prefix       AS p_prefix,
                p.firstname    AS p_firstname,
                p.middlename   AS p_middlename,
                p.lastname     AS p_lastname,
                p.suffix       AS p_suffix,
                p.userid       AS p_userid,
                p.pharmetikaid AS p_pharmetikaid,

                address.id         AS a_id,
                address.address1  AS a_address1,
                address.address2  AS a_address2,
                address.city      AS a_city,
                address.state     AS a_state,
                address.zip       AS a_zip,
                address.created   AS a_created,
                address.type      AS a_type,
                address.zip4      AS a_zip4,
                address.latlong   AS a_latlong
            FROM patient p
            LEFT JOIN rx ON rx.patientid = p.id
            LEFT JOIN address ON p.addressid = address.id
            WHERE rx.officeid = %s
            GROUP BY p.id, address.id
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(sql, [office_id])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        results = []
        for row in rows:
            data = dict(zip(columns, row))

            results.append(
                {
                    "p": {
                        "id": data["p_id"],
                        "addressid": data["p_addressid"],
                        "name": data["p_name"],
                        "dob": data["p_dob"],
                        "gender": data["p_gender"],
                        "phone": data["p_phone"],
                        "email": data["p_email"],
                        "allergies": data["p_allergies"],
                        "otherdrugs": data["p_otherdrugs"],
                        "otherinfo": data["p_otherinfo"],
                        "created": data["p_created"],
                        "pregnant": data["p_pregnant"],
                        "prefix": data["p_prefix"],
                        "firstname": data["p_firstname"],
                        "middlename": data["p_middlename"],
                        "lastname": data["p_lastname"],
                        "suffix": data["p_suffix"],
                        "userid": data["p_userid"],
                        "pharmetikaid": data["p_pharmetikaid"],
                    },
                    "address": {
                        "id": data["a_id"],
                        "address1": data["a_address1"],
                        "address2": data["a_address2"],
                        "city": data["a_city"],
                        "state": data["a_state"],
                        "zip": data["a_zip"],
                        "created": data["a_created"],
                        "type": data["a_type"],
                        "zip4": data["a_zip4"],
                        "latlong": data["a_latlong"],
                    },
                }
            )

        return results


__all__ = [
    "RxErrorCodes",
    "RxServiceException",
    "RxSerializer",
    "RxListSerializer",
    "RxDetailSerializer",
    "RxService",
]
