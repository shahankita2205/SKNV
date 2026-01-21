"""
Rx (Prescription) Serializers and Services
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from django.db import connections
from django.db.models import Count
from rest_framework import serializers

from fred.models.doctor import Doctor
from fred.models.models import (
    Ihflogs,
    Patient2,
    Payment,
    Prepaid,
    Rx,
    Rxfill,
    Rxraw,
    Shipment,
    Substatus,
    Token,
)
from fred.models.office import Office, Officeinfo
from fred.models.medication import Fee, Medication
from fred.serializers import reference as reference_serializer


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


# Mapping constants
FILL_TYPE_MAP = {"newrx": "New", "refill": "Refill", "corrector": "Corrector"}

FILL_STATUS_MAP = {
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
}


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
                rx.id AS rx_id, rx.created AS rx_created, rx.qty AS rx_qty, rx.status AS rx_status,
                fill.type AS fill_type, fill.status AS fill_status, fill.paymentid, fill.shipmentid,
                med.formulacode, doc.name AS doctor_name,
                patient.firstname, patient.lastname, patient.dob, patient.phone,
                pay.amount AS payment_amount, pay.created AS payment_created,
                ship.tracking, ship.created AS shipment_created, raw.payload AS raw_payload
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
        date_field_map = {
            "rx": "fill.created",
            "payment": "pay.created",
            "shipment": "ship.created",
        }
        date_field = date_field_map.get(kind)

        if start and date_field:
            sql += f" AND {date_field} > %s"
            params.append(start)
        if end and date_field:
            sql += f" AND {date_field} < %s"
            params.append(end)

        sql += " ORDER BY rx.id ASC"

        with connections["fred"].cursor() as cursor:
            cursor.execute(sql, params)
            cols = [c[0] for c in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]

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
        if dob and len(dob) == 8:
            return f"{dob[4:6]}/{dob[6:]}/{dob[:4]}"
        return dob

    @staticmethod
    def map_fill_type(fill_type):
        return FILL_TYPE_MAP.get(fill_type, "")

    @staticmethod
    def map_fill_status(status):
        return FILL_STATUS_MAP.get(status, status)

    @staticmethod
    def build_rx_response(rxs, payments, shipments, role, no_drilldown):
        result = {"rxs": [], "payments": [], "shipments": [], "med": []}
        last_rx, temp = None, None

        for row in rxs:
            rx_id, created = row["rx_id"], row["rx_created"]
            unix = int(created.timestamp())
            date_col = (
                f"<span class='d-none'>{unix}</span>{created.strftime('%m/%d/%Y')}"
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
            details_btn = f'<button type="button" class="btn btn-sm btn-secondary" onClick="showRxDetails({rx_id})">Details</button>'

            if rx_id != last_rx:
                if temp:
                    result["rxs"].append(temp)
                temp = [
                    date_col,
                    rx_link,
                    pat_init,
                    dob,
                    phone,
                    row["doctor_name"],
                    medication,
                    fill_type,
                    paid,
                    shipped,
                    status,
                    details_btn,
                ]
                last_rx = rx_id
            else:
                temp[7] += "<br>" + fill_type
                temp[8] += "<br>" + paid
                temp[9] += "<br>" + shipped
                temp[10] += "<br>" + status

        if temp:
            result["rxs"].append(temp)

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
                f'<a href="/payments/view?id={pay_id}" target="_blank">{created.strftime("%m/%d/%Y")}</a>'
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
                    f'<button type="button" class="btn btn-sm btn-secondary" onClick="showRxDetails({row["rx_id"]})">Details</button>',
                ]
            )
        return result

    @staticmethod
    def get_medications_by_office(office_id: int, start=None, end=None):
        qs = Rx.objects.using("fred").filter(
            officeid=office_id, medicationid__isnull=False
        )
        if start:
            qs = qs.filter(created__gt=start)
        if end:
            qs = qs.filter(created__lt=end)

        response = []
        for row in qs.values("medicationid").annotate(qty=Count("id")):
            ndc = row["medicationid"]
            med = Medication.objects.using("fred").filter(ndc=ndc).first()
            if med:
                label = f"{med.ndc}: {med.brand_name}<br><small>{med.formulacode} {med.formula} {med.size} {med.dosage}</small>"
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
                prescribers.append({"count": stat["count"], "name": doctor.name})
            except Doctor.DoesNotExist:
                continue
        return prescribers

    @staticmethod
    def get_patients_by_office(office_id: int) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                p.id AS p_id, p.addressid AS p_addressid, p.name AS p_name, p.dob AS p_dob,
                p.gender AS p_gender, p.phone AS p_phone, p.email AS p_email,
                p.allergies AS p_allergies, p.otherdrugs AS p_otherdrugs, p.otherinfo AS p_otherinfo,
                p.created AS p_created, p.pregnant AS p_pregnant, p.prefix AS p_prefix,
                p.firstname AS p_firstname, p.middlename AS p_middlename, p.lastname AS p_lastname,
                p.suffix AS p_suffix, p.userid AS p_userid, p.pharmetikaid AS p_pharmetikaid,
                address.id AS a_id, address.address1 AS a_address1, address.address2 AS a_address2,
                address.city AS a_city, address.state AS a_state, address.zip AS a_zip,
                address.created AS a_created, address.type AS a_type, address.zip4 AS a_zip4,
                address.latlong AS a_latlong
            FROM patient p
            LEFT JOIN rx ON rx.patientid = p.id
            LEFT JOIN address ON p.addressid = address.id
            WHERE rx.officeid = %s
            GROUP BY p.id, address.id
        """
        with connections["fred"].cursor() as cursor:
            cursor.execute(sql, [office_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        results = []
        for row in rows:
            data = dict(zip(columns, row))
            results.append(
                {
                    "p": {k[2:]: data[k] for k in columns if k.startswith("p_")},
                    "address": {k[2:]: data[k] for k in columns if k.startswith("a_")},
                }
            )
        return results

    @staticmethod
    def get_fills_fulfillment_partner(rxfill_id: int) -> str:
        """Get fulfillment partner for a fill."""
        try:
            log = (
                Ihflogs.objects.using("fred")
                .filter(fillid_id=rxfill_id)
                .order_by("-ihfid")
                .first()
            )
            return log.fpid.name if log and log.fpid else "HWH"
        except Exception as e:
            logger.debug(f"Error getting fulfillment partner: {e}")
            return "HWH"

    @staticmethod
    def get_sub_status_by_status(status: str):
        """Get SubStatus by status field."""
        try:
            return Substatus.objects.using("fred").filter(status=status).first()
        except Exception:
            return None

    @staticmethod
    def format_phone_display(phone):
        """Format phone number: (XXX) XXX-XXXX"""
        if phone:
            p = (
                str(phone)
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
                .replace(" ", "")
            )
            if len(p) == 10:
                return f"({p[:3]}) {p[3:6]}-{p[6:]}"
        return phone

    @staticmethod
    def format_phone_dashes(phone):
        """Format phone number: XXX-XXX-XXXX"""
        if phone:
            p = (
                str(phone)
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
                .replace(" ", "")
            )
            if len(p) == 10:
                return f"{p[:3]}-{p[3:6]}-{p[6:]}"
        return phone

    @staticmethod
    def format_dob_display(dob):
        """Format DOB: MM/DD/YYYY from YYYYMMDD"""
        if dob:
            d = str(dob).replace("-", "")
            if len(d) == 8:
                return f"{d[4:6]}/{d[6:8]}/{d[:4]}"
        return dob

    @staticmethod
    def format_datetime_space(dt):
        """Format datetime: YYYY-MM-DD HH:MM:SS"""
        if dt is None:
            return None
        if hasattr(dt, "strftime"):
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return str(dt).replace("T", " ").replace("Z", "").split("+")[0].split(".")[0]

    @staticmethod
    def model_to_array(obj, exclude=None):
        """Convert a Django model instance to dictionary."""
        if obj is None:
            return None

        exclude = exclude or []
        data = {}

        for field in obj._meta.fields:
            if field.name in exclude:
                continue
            try:
                if field.is_relation:
                    key = field.db_column if field.db_column else field.name
                    data[key] = getattr(obj, field.attname, None)
                else:
                    value = getattr(obj, field.name, None)
                    if value is not None and hasattr(value, "isoformat"):
                        value = value.strftime("%Y-%m-%dT%H:%M:%SZ")
                    elif type(value).__name__ == "Decimal":
                        value = float(value)
                    data[field.name] = value
            except Exception:
                data[field.name] = None
        return data

    @staticmethod
    def _get_safe_attr(obj, attr, default=None):
        """Safely get attribute with default."""
        return getattr(obj, attr, default) or default

    @staticmethod
    def view_q(
        rx_id: int, hipaa: bool = False, status: str = None, sales: bool = False
    ) -> Union[Dict[str, Any], bool]:
        """Get detailed Rx view with all related data."""
        from fred.serializers.office import parse_json_array
        from fred.models.models import Users

        try:
            rx = Rx.objects.using("fred").get(pk=rx_id)
        except Rx.DoesNotExist:
            return {}

        # Initialize data immediately
        data = RxService.model_to_array(rx)

        # Medication and fee
        medication, fee_value = None, 50
        if rx.medicationid:
            try:
                medication = Medication.objects.using("fred").get(ndc=rx.medicationid)
                try:
                    fee_value = Fee.objects.using("fred").get(ndc=rx.medicationid).fee
                except Fee.DoesNotExist:
                    pass
            except Medication.DoesNotExist:
                pass
        data["medication"] = (
            RxService.model_to_array(medication) if medication else None
        )
        data["fee"] = fee_value

        # Office, office_info, office_address
        office, office_info, office_address = None, None, None
        if rx.officeid:
            try:
                office = Office.objects.using("fred").get(pk=rx.officeid)
                office_info = (
                    Officeinfo.objects.using("fred")
                    .filter(officeid_id=rx.officeid)
                    .first()
                )
                office_address = (
                    reference_serializer.AddressModelSerializer.get_address_by_id(
                        office.addressid
                    )
                    if office and office.addressid
                    else None
                )
            except Office.DoesNotExist:
                office = None
                office_info = None
                office_address = None

        if office:
            data["office"] = RxService.model_to_array(office)
            data["office"]["address"] = office_address
            data["office"]["modified"] = (
                RxService.format_datetime_space(office.modified)
                if hasattr(office, "modified") and office.modified
                else None
            )
            data["office"]["synced"] = (
                f"{RxService.format_datetime_space(office.synced)}+00"
                if hasattr(office, "synced") and office.synced
                else None
            )
            for key in ["vifeeshippinghandling", "vifeeservice"]:
                if data["office"].get(key) is not None:
                    data["office"][key] = str(int(data["office"][key]))
            data["office"]["dio2enabled"] = getattr(office, "dio2enabled", None)

            # Sales data
            try:
                sales_ids = parse_json_array(office.sales)
                assigned_users = []
                for uid in sales_ids:
                    try:
                        user = Users.objects.using("fred").get(pk=uid)
                        assigned_users.append(
                            {
                                "id": user.id,
                                "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                                "email": user.email,
                                "role": user.role,
                            }
                        )
                    except Users.DoesNotExist:
                        continue
                data["office"]["sales"] = {"assigned": assigned_users, "available": []}
            except Exception:
                data["office"]["sales"] = None
        else:
            data["office"] = None

        # Officeinfo
        if office_info:
            data["officeinfo"] = RxService.model_to_array(office_info)
        else:
            data["officeinfo"] = {
                k: None
                for k in [
                    "id",
                    "officeid",
                    "featuredskincare",
                    "abouthtml",
                    "herobackground",
                    "avatartoshow",
                    "officeimage",
                    "created",
                    "modified",
                    "fax",
                    "primaryphone",
                    "reminderopt",
                ]
            }

        # Doctor
        doctor = None
        if rx.doctorid:
            try:
                doctor = Doctor.objects.using("fred").get(pk=rx.doctorid)
            except Doctor.DoesNotExist:
                pass
        if doctor:
            data["doctor"] = RxService.model_to_array(doctor)
            data["doctor"]["phone"] = RxService.format_phone_display(doctor.phone)
            data["doctor"]["fax"] = getattr(doctor, "fax", None)
        else:
            data["doctor"] = None

        # Rxraw
        rxraw = None
        if rx.rxrawid:
            try:
                rxraw = Rxraw.objects.using("fred").get(pk=rx.rxrawid)
            except Rxraw.DoesNotExist:
                pass
        if rxraw:
            data["rxraw"] = RxService.model_to_array(rxraw)
        else:
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
            data["rxraw"] = {
                "id": None,
                "payload": None,
                "msgid": None,
                "msg": None,
                "edi": None,
                "sent": now_iso,
                "received": now_iso,
                "status": None,
                "format": None,
                "rxsource": None,
            }

        # Prepaid
        prepaid = Prepaid.objects.using("fred").filter(rxid=rx_id).first()
        data["prepaidQty"] = prepaid.qty if prepaid and prepaid.qty else 0

        # Additional safe attributes
        for attr, default in [
            ("virx", False),
            ("viprice", None),
            ("fax", None),
            ("isverbal", False),
            ("verbalprescriptionby", None),
            ("createdby", None),
            ("dio2", False),
        ]:
            data[attr] = RxService._get_safe_attr(rx, attr, default)

        # Patient (HIPAA)
        if hipaa and rx.patientid:
            try:
                patient = Patient2.objects.using("fred").get(pk=rx.patientid)
                data["patient"] = RxService.model_to_array(patient)
                data["patient"]["dob"] = RxService.format_dob_display(patient.dob)
                data["patient"]["phone"] = RxService.format_phone_dashes(patient.phone)
                data["patient"]["address"] = (
                    reference_serializer.AddressModelSerializer.get_address_by_id(
                        patient.addressid
                    )
                    if patient.addressid
                    else None
                )
            except Patient2.DoesNotExist:
                data["patient"] = None

        # Fills
        fills_qs = Rxfill.objects.using("fred").filter(rxid=rx_id).order_by("id")
        seen_fill_ids, void = set(), True
        data["fills"] = []
        for fill in fills_qs:
            add = True
            if status:
                if fill.status == status:
                    void = False
                else:
                    add = False

            if add and fill.id not in seen_fill_ids and fill.id is not None:
                seen_fill_ids.add(fill.id)
                fulfillment_partner = RxService.get_fills_fulfillment_partner(fill.id)
                sub_status_obj = None
                fp_status_value = getattr(fill, "fp_status", None)
                if fp_status_value is not None:
                    sub_status_obj = RxService.get_sub_status_by_status(fp_status_value)
                sub_status = (
                    sub_status_obj.formattedstatus
                    if sub_status_obj
                    else fp_status_value
                )

                fill_data = RxService.model_to_array(fill)
                fill_data["bulkcanceldate"] = getattr(fill, "bulkcanceldate", None)
                fill_data["fulfillmentPartner"] = fulfillment_partner
                fill_data["subStatus"] = sub_status

                # Payment
                if fill.paymentid:
                    try:
                        payment = Payment.objects.using("fred").get(pk=fill.paymentid)
                        if payment.id is not None:
                            fill_data["payment"] = RxService.model_to_array(payment)
                    except Payment.DoesNotExist:
                        pass

                # Shipment
                if fill.shipmentid:
                    try:
                        shipment = Shipment.objects.using("fred").get(
                            pk=fill.shipmentid
                        )
                        if shipment.id is not None:
                            fill_data["shipment"] = RxService.model_to_array(shipment)
                    except Shipment.DoesNotExist:
                        pass

                # Token
                token = Token.objects.using("fred").filter(recordid=fill.id).first()
                if token and token.id is not None:
                    fill_data["token"] = RxService.model_to_array(token)

                data["fills"].append(fill_data)

        return False if status and void else data


__all__ = [
    "RxErrorCodes",
    "RxServiceException",
    "RxSerializer",
    "RxListSerializer",
    "RxDetailSerializer",
    "RxService",
]
