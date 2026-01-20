"""
Office Serializers and Services
"""

import json
import logging
from datetime import datetime, timedelta,time
from typing import Optional, List, Dict, Any, Union
from django.db.models import OuterRef, Subquery,Value
from django.db.models.functions import Upper
from django.db import connections
from django.db import transaction
from django.db.models import Q, Count, Sum
from rest_framework import serializers
from dateutil.relativedelta import relativedelta

from fred.models.office import (
    Office,
    Officetype,
)

# Import other models from models.py
from fred.models.models import (
    DioShipments,
    Users,
    Rx,
    Payment,
    Medication,
    Rxfill,
    DioItems,
    Skincarepairings,
    Shipment,
)
from fred.models.doctor import Doctor

# Import shared services
from fred.serializers.address import AddressService, AddressSerializer
from fred.serializers.officeinfo import OfficeInfoService, OfficeInfoSerializer
from fred.serializers.officehistory import OfficeHistoryService
from fred.serializers.payment import PaymentService
from fred.serializers.rx import RxService
from fred.serializers.rxfill import RxFillService
from fred.serializers.user import UserService

logger = logging.getLogger(__name__)


class OfficeErrorCodes:
    ERROR_UNABLE_CREATE_OFFICE = 16001
    ERROR_OFFICE_NOT_FOUND = 16002
    ERROR_INCORRECT_OFFICE = 16003
    ERROR_UNABLE_UPDATE_OFFICE = 16004
    ERROR_UNABLE_DELETE_OFFICE = 16005
    ERROR_ALREADY_EXISTS = 10001


class OfficeServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class OfficeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officetype
        fields = ["id", "type"]


class OfficeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = [
            "id",
            "addressid",
            "name",
            "created",
            "locationid",
            "sales",
            "altaddress",
            "users",
            "logo",
            "dhenabled",
            "allowmsgconsult",
            "allowvideoconsult",
            "allowmsgfreeform",
            "videoconsultfee",
            "msgconsultfee",
            "displayname",
            "netsuiteid",
            "allowchatconsult",
            "chatconsultfee",
            "email",
            "route",
            "officeemail",
            "primaryemail",
            "suppresssknvmessaging",
            "suppressrefills",
            "inofficedispense",
            "allownewpatientreqconsult",
            "officeslug",
            "vendorid",
            "modified",
            "synced",
            "dtcstates",
            "suppresspairings",
            "officetypeid",
            "officeagreementtypeid",
            "note",
            "virtualinventoryenabled",
            "vi_status",
            "replenishmentoptout",
            "parentid",
            "vifeeshippinghandling",
            "vifeeservice",
            "viproceedstype",
            "vivendorid",
            "vicontactid",
            "vicontracttoken",
            "dio2",
        ]


class OfficeDetailSerializer(serializers.ModelSerializer):
    address = serializers.SerializerMethodField()

    class Meta:
        model = Office
        fields = [
            "id",
            "addressid",
            "name",
            "created",
            "locationid",
            "sales",
            "altaddress",
            "users",
            "logo",
            "dhenabled",
            "allowmsgconsult",
            "allowvideoconsult",
            "allowmsgfreeform",
            "videoconsultfee",
            "msgconsultfee",
            "displayname",
            "netsuiteid",
            "allowchatconsult",
            "chatconsultfee",
            "email",
            "route",
            "officeemail",
            "primaryemail",
            "suppresssknvmessaging",
            "suppressrefills",
            "inofficedispense",
            "allownewpatientreqconsult",
            "officeslug",
            "vendorid",
            "modified",
            "synced",
            "dtcstates",
            "suppresspairings",
            "officetypeid",
            "officeagreementtypeid",
            "note",
            "virtualinventoryenabled",
            "vi_status",
            "replenishmentoptout",
            "parentid",
            "vifeeshippinghandling",
            "vifeeservice",
            "viproceedstype",
            "vivendorid",
            "vicontactid",
            "vicontracttoken",
            "dio2",
            "address",
        ]

    def get_address(self, obj) -> Optional[Dict]:
        if obj.addressid:
            address = AddressService.get_one(obj.addressid)
            if address:
                return AddressSerializer(address).data
        return None


class OfficeFastListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class OfficeCreateSerializer(serializers.Serializer):
    addressid = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True, max_length=255)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Office name is required")
        return value.strip()

    def validate_addressid(self, value):
        address = AddressService.get_one(value)
        if not address:
            raise serializers.ValidationError(f"Address with id {value} not found")
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic(using="fred"):
                office = Office.objects.using("fred").create(**validated_data)
                logger.info(f"Office #{office.id} ({office.name}) has been created")
                return office
        except Exception as e:
            logger.error(f"Error creating office: {e}")
            raise OfficeServiceException(
                "Unable to create office", OfficeErrorCodes.ERROR_UNABLE_CREATE_OFFICE
            )


class OfficeUpdateSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    addressid = serializers.IntegerField(required=False)
    altaddress = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    locationid = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    name = serializers.CharField(required=False, max_length=255)
    users = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    logo = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dhenabled = serializers.BooleanField(required=False)
    displayname = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    videoconsultfee = serializers.IntegerField(required=False)
    msgconsultfee = serializers.IntegerField(required=False)
    chatconsultfee = serializers.IntegerField(required=False)
    allowvideoconsult = serializers.BooleanField(required=False)
    allowmsgconsult = serializers.BooleanField(required=False)
    allowchatconsult = serializers.BooleanField(required=False)
    allowmsgfreeform = serializers.BooleanField(required=False)
    allownewpatientreqconsult = serializers.BooleanField(required=False)
    acct = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    route = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    officeemail = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    primaryemail = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    netsuiteid = serializers.IntegerField(required=False, allow_null=True)
    suppresssknvmessaging = serializers.BooleanField(required=False)
    inofficedispense = serializers.BooleanField(required=False)
    suppresspairings = serializers.BooleanField(required=False)
    officetypeid = serializers.IntegerField(required=False, allow_null=True)
    suppressrefills = serializers.BooleanField(required=False)
    officeagreementtypeid = serializers.IntegerField(required=False, allow_null=True)
    replenishmentoptout = serializers.BooleanField(required=False)
    parentid = serializers.IntegerField(required=False, allow_null=True)
    viproceedstype = serializers.IntegerField(required=False, allow_null=True)
    vivendorid = serializers.IntegerField(required=False, allow_null=True)
    vicontactid = serializers.IntegerField(required=False, allow_null=True)
    vicontracttoken = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    fax = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reminderopt = serializers.BooleanField(required=False, default=False)

    ADMIN_FIELDS = [
        "note",
        "addressid",
        "altaddress",
        "locationid",
        "name",
        "users",
        "logo",
        "dhenabled",
        "displayname",
        "videoconsultfee",
        "msgconsultfee",
        "chatconsultfee",
        "allowvideoconsult",
        "allowmsgconsult",
        "allowchatconsult",
        "allowmsgfreeform",
        "allownewpatientreqconsult",
        "acct",
        "route",
        "email",
        "officeemail",
        "primaryemail",
        "netsuiteid",
        "suppresssknvmessaging",
        "inofficedispense",
        "suppresspairings",
        "officetypeid",
        "suppressrefills",
        "officeagreementtypeid",
        "replenishmentoptout",
        "parentid",
        "viproceedstype",
        "vivendorid",
        "vicontactid",
        "vicontracttoken",
    ]

    MANAGER_SALES_FIELDS = [
        "inofficedispense",
        "email",
        "officeemail",
        "primaryemail",
        "dhenabled",
        "displayname",
        "videoconsultfee",
        "msgconsultfee",
        "chatconsultfee",
        "allowvideoconsult",
        "allowmsgconsult",
        "allowchatconsult",
        "allowmsgfreeform",
        "allownewpatientreqconsult",
        "name",
        "suppressrefills",
        "officeagreementtypeid",
        "replenishmentoptout",
        "parentid",
        "viproceedstype",
        "vivendorid",
        "vicontactid",
    ]

    SALES_MANAGER_FIELDS = MANAGER_SALES_FIELDS + ["netsuiteid", "logo"]
    OFFICE_DOCTOR_FIELDS = ["logo"]
    CS_PHARMACIST_FIELDS = ["note"]

    def get_allowed_fields(self, role: str) -> List[str]:
        role_fields = {
            "admin": self.ADMIN_FIELDS,
            "manager": self.MANAGER_SALES_FIELDS,
            "sales": self.MANAGER_SALES_FIELDS,
            "sales-manager": self.SALES_MANAGER_FIELDS,
            "office": self.OFFICE_DOCTOR_FIELDS,
            "doctor": self.OFFICE_DOCTOR_FIELDS,
            "customer-service": self.CS_PHARMACIST_FIELDS,
            "customer-service-manager": self.CS_PHARMACIST_FIELDS,
            "pharmacist": self.CS_PHARMACIST_FIELDS,
        }
        return role_fields.get(role, [])

    def update(self, instance, validated_data):
        role = self.context.get("role", "admin")
        allowed_fields = self.get_allowed_fields(role)

        office_info_fields = ["fax", "phone", "reminderopt"]
        office_info_data = {}
        for field in office_info_fields:
            if field in validated_data:
                if field == "phone":
                    office_info_data["primaryphone"] = validated_data.pop(field)
                else:
                    office_info_data[field] = validated_data.pop(field)

        if office_info_data:
            OfficeInfoService.create_or_update(instance.id, office_info_data)

        try:
            with transaction.atomic(using="fred"):
                for field in allowed_fields:
                    if field in validated_data:
                        value = validated_data[field]
                        if field == "parentid" and value == 0:
                            value = None
                        if field == "vivendorid" and value == 0:
                            value = None
                        if field == "netsuiteid":
                            if value == 0 or value == "0":
                                value = None
                            else:
                                existing = (
                                    Office.objects.using("fred")
                                    .filter(netsuiteid=value)
                                    .exclude(pk=instance.id)
                                    .first()
                                )
                                if existing:
                                    raise OfficeServiceException(
                                        f"NetSuite ID {value} already assigned to Office ID {existing.id}",
                                        OfficeErrorCodes.ERROR_UNABLE_UPDATE_OFFICE,
                                    )
                        setattr(instance, field, value)
                instance.save(using="fred")
                logger.info(f"Office #{instance.id} has been updated by role: {role}")
                return instance
        except OfficeServiceException:
            raise
        except Exception as e:
            logger.error(f"Error updating office #{instance.id}: {e}")
            raise OfficeServiceException(
                "Unable to update office", OfficeErrorCodes.ERROR_UNABLE_UPDATE_OFFICE
            )


class OfficeCreateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class OfficeFastListResponseSerializer(serializers.Serializer):
    results = OfficeFastListSerializer(many=True)


class OfficeService:

    @staticmethod
    def get_all():
        return Office.objects.using("fred").order_by("-id")

    @staticmethod
    def get_one(office_id: int) -> Office:
        try:
            return Office.objects.using("fred").get(pk=office_id)
        except Office.DoesNotExist:
            raise OfficeServiceException(
                f"Office #{office_id} not found",
                OfficeErrorCodes.ERROR_OFFICE_NOT_FOUND,
            )

    @staticmethod
    def get_one_no_exception(office_id: int) -> Optional[Office]:
        try:
            return Office.objects.using("fred").get(pk=office_id)
        except Office.DoesNotExist:
            return None

    @staticmethod
    def get_one_with_address(
        office_id: int, role: str = None, user_id: int = None
    ) -> Dict[str, Any]:
        try:
            office = OfficeService.get_one(office_id)
        except OfficeServiceException:
            return {"error": True}

        access = True
        if role in ["doctor", "office"] and user_id:
            access = False
            users = OfficeService._parse_json_array(office.users)
            if user_id in users:
                access = True

        if not access:
            return {"error": True}

        result = OfficeDetailSerializer(office).data
        return result

    @staticmethod
    def delete(office_id: int) -> bool:
        try:
            with transaction.atomic(using="fred"):
                office = Office.objects.using("fred").get(pk=office_id)
                office.delete()
                logger.info(f"Office #{office_id} has been deleted")
                return True
        except Office.DoesNotExist:
            raise OfficeServiceException(
                f"Office #{office_id} not found",
                OfficeErrorCodes.ERROR_OFFICE_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error deleting office #{office_id}: {e}")
            raise OfficeServiceException(
                "Unable to delete office", OfficeErrorCodes.ERROR_UNABLE_DELETE_OFFICE
            )

    @staticmethod
    def get_fast_list() -> List[Dict[str, Any]]:
        offices = Office.objects.using("fred").values("id", "name").order_by("name")
        return list(offices)

    @staticmethod
    def get_users(office_id: int) -> List[Dict[str, Any]]:
        """Get users for an office using UserService."""
        office = OfficeService.get_one(office_id)
        user_ids = OfficeService._parse_json_array(office.users)
        return UserService.get_users_with_details(user_ids)

    @staticmethod
    def get_sales(office_id: int, list_available: bool = True) -> Dict[str, List]:
        """Get sales users for an office using UserService."""
        office = OfficeService.get_one(office_id)
        sales_ids = OfficeService._parse_json_array(office.sales)

        if not list_available:
            # Only return assigned sales
            users = UserService.get_users_with_details(sales_ids)
            return {"assigned": users, "available": []}

        return UserService.get_office_assigned_sales(sales_ids)

    @staticmethod
    def get_all_by_user_id(user_id: int) -> List[int]:
        offices = Office.objects.using("fred").all()
        office_ids = []
        for office in offices:
            users = OfficeService._parse_json_array(office.users)
            if user_id in users:
                office_ids.append(office.id)
        return office_ids if office_ids else []

    @staticmethod
    def check_same(old_data: Dict, new_data: Dict) -> bool:
        for key, value in old_data.items():
            if key in ["modified", "synced"]:
                continue
            if new_data.get(key) != value:
                return False
        return True

    @staticmethod
    def _parse_json_array(value: str) -> List[int]:
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [int(x) for x in parsed]
            return []
        except (json.JSONDecodeError, ValueError):
            return []

    @staticmethod
    def set_users(office_id: int, user_ids: List[int]) -> Office:
        office = OfficeService.get_one(office_id)
        office.users = json.dumps(user_ids)
        office.save(using="fred")
        logger.info(f"Office #{office_id} users set to: {user_ids}")
        return office

    @staticmethod
    def set_sales(office_id: int, sales_ids: List[int]) -> Office:
        office = OfficeService.get_one(office_id)
        office.sales = json.dumps(sales_ids)
        office.save(using="fred")
        logger.info(f"Office #{office_id} sales set to: {sales_ids}")
        return office

    @staticmethod
    def add_office_user(office_id: int, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a user to an office using UserService."""
        office = OfficeService.get_one(office_id)

        # Use UserService to create the user
        result = UserService.create_user(user_data)

        # Add user to office
        with transaction.atomic(using="fred"):
            current_users = OfficeService._parse_json_array(office.users)
            if result["user_id"] not in current_users:
                current_users.append(result["user_id"])
                office.users = json.dumps(current_users)
                office.save(using="fred")

            logger.info(f"User #{result['user_id']} added to office #{office_id}")

        return result

    @staticmethod
    def get_office_view(office_id: int) -> Dict[str, Any]:
        """Get office view using shared services."""
        office = OfficeService.get_one(office_id)

        # Use AddressService
        address = None
        if office.addressid:
            address = AddressService.get_one(office.addressid)

        # Use OfficeInfoService
        office_info = OfficeInfoService.get_one_by_office_id(office_id)

        # OfficeType
        office_type = None
        if office.officetypeid:
            try:
                office_type_obj = Officetype.objects.using("fred").get(
                    id=office.officetypeid
                )
                office_type = OfficeTypeSerializer(office_type_obj).data
            except Officetype.DoesNotExist:
                office_type = None

        patient_ids = (
            Rx.objects.using("fred")
            .filter(officeid=office_id)
            .values_list("patientid", flat=True)
            .distinct()
        )

        return {
            "officeInfo": (
                OfficeInfoSerializer(office_info).data if office_info else None
            ),
            "officeType": office_type,
            "office": OfficeListSerializer(office).data,
            "address": AddressSerializer(address).data if address else None,
        }

    @staticmethod
    def get_performance(office_id: int) -> List[List[Any]]:
        start_date = datetime(2020, 3, 1)
        end_date = datetime.now()

        results = []
        current = start_date

        while current <= end_date:
            month_start = current.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

            month_label = month_start.strftime("%Y-%m")

            new_rx = OfficeService.get_rx_count_by_office(
                office_id, month_start, month_end, "newrx"
            )
            refill_rx = OfficeService.get_rx_count_by_office(
                office_id, month_start, month_end, "refill"
            )
            corrector_rx = OfficeService.get_rx_count_by_office(
                office_id, month_start, month_end, "corrector"
            )

            shipment_count = OfficeService.get_rx_count_by_office(
                office_id, month_start, month_end, "shipment"
            )

            shipment_count = OfficeService.get_shipment_count_by_office(
                office_id, month_start, month_end
            )

            pos_payment = OfficeService.get_payment_count_by_office(
                office_id, month_start, month_end, "pos"
            )
            rxportal_payment = OfficeService.get_payment_count_by_office(
                office_id, month_start, month_end, "rxportal"
            )
            self_payment = OfficeService.get_payment_count_by_office(
                office_id, month_start, month_end, "self"
            )

            results.append(
                [
                    month_label,
                    new_rx,
                    refill_rx,
                    corrector_rx,
                    shipment_count,
                    pos_payment,
                    rxportal_payment,
                    self_payment,
                ]
            )

            current += relativedelta(months=1)

        return results

    @staticmethod
    def get_payment_count_by_office(
        oid: Union[int, List[int]],
        start: datetime = None,
        end: datetime = None,
        payment_type: str = None,
    ) -> int:
        """
        Python equivalent of PHP getPaymentCountByOffice()
        """

        # Ensure office IDs are always a list
        offices = oid if isinstance(oid, list) else [oid]

        qs = Payment.objects.using("fred").filter(officeid__in=offices)

        if payment_type:
            qs = qs.filter(type=payment_type)

        if start:
            qs = qs.filter(created__gt=start)

        if end:
            qs = qs.filter(created__lt=end)

        return qs.count()

    @staticmethod
    def get_contacts(office_id: int) -> List[Dict[str, Any]]:
        """Get office contacts using UserService."""
        office = OfficeService.get_one(office_id)
        user_ids = OfficeService._parse_json_array(office.users)
        return UserService.get_users_with_details(user_ids)

    @staticmethod
    def get_medications(
        office_id: int,
        start: datetime = None,
        end: datetime = None,
    ):
        OfficeService.get_one(office_id)
        return RxService.get_medications_by_office(office_id, start, end)

    @staticmethod
    def get_prescribers(office_id: int) -> List[Dict[str, Any]]:
        """Get prescribers for an office using RxService."""
        OfficeService.get_one(office_id)
        return RxService.get_prescribers_by_office(office_id)

    @staticmethod
    def get_patients(office_id: int) -> List[Dict[str, Any]]:
        """Get patients for an office using RxService."""
        OfficeService.get_one(office_id)
        return RxService.get_patients_by_office(office_id)

    @staticmethod
    def get_rx_action(office_id, role, start=None, end=None):
        no_drilldown = role in {"sales", "sales-manager", "office", "doctor"}

        rxs = RxService.get_rx_by_office(office_id, start, end, kind="rx")
        payments = RxService.get_rx_by_office(office_id, start, end, kind="payment")
        shipments = RxService.get_rx_by_office(office_id, start, end, kind="shipment")

        return RxService.build_rx_response(
            rxs=rxs,
            payments=payments,
            shipments=shipments,
            role=role,
            no_drilldown=no_drilldown,
        )

    @staticmethod
    def get_pending_rx(office_id: int) -> List[Dict[str, Any]]:
        """Get pending prescriptions using RxFillService."""
        OfficeService.get_one(office_id)
        return RxFillService.get_pending_fills_by_office(office_id)

    @staticmethod
    def get_pending_payments(office_id: int) -> List[Dict[str, Any]]:
        """Get pending payments using PaymentService."""
        OfficeService.get_one(office_id)
        return PaymentService.get_pending_by_office(office_id)

    @staticmethod
    def get_paid_rxs(office_id: int) -> List[Dict[str, Any]]:
        """Get paid prescriptions using RxFillService."""
        OfficeService.get_one(office_id)
        return RxFillService.get_paid_fills_by_office(office_id)

    @staticmethod
    def move_payment(
        payment_id: int, from_office_id: int, to_office_id: int
    ) -> Dict[str, Any]:
        """Move payment between offices using PaymentService."""
        OfficeService.get_one(from_office_id)
        OfficeService.get_one(to_office_id)
        return PaymentService.move_payment(payment_id, from_office_id, to_office_id)

    @staticmethod
    def get_paginated(
        page: int = 1,
        limit: int = 25,
        search: str = None,
        order_column: int = 0,
        order_dir: str = "asc",
        office_ids=None,
    ) -> Dict[str, Any]:

        offset = (page - 1) * limit
        params = []

        base_sql = """
            FROM office o
            INNER JOIN address a ON a.id = o.addressid
            INNER JOIN officetype ot ON ot.id = o.officetypeid
            LEFT JOIN users u
              ON u.id = CAST(
                    REGEXP_REPLACE(COALESCE(o.sales, '0'), '\\[|\\]', '', 'g')
                    AS INTEGER
                 )
            WHERE 1=1
        """

        # ---- SEARCH ----
        if search:
            base_sql += """
                AND (
                    CAST(o.id AS TEXT) ILIKE %s
                    OR o.name ILIKE %s
                    OR CONCAT(a.city, ', ', a.state) ILIKE %s
                    OR CONCAT(u.first_name, ' ', u.last_name) ILIKE %s
                )
            """
            params.extend([f"%{search}%"] * 4)

        # ---- OFFICE IDS FILTER ----
        if office_ids:
            base_sql += " AND o.id = ANY(%s)"
            params.append(office_ids)

        # ---- TOTAL COUNTS ----
        count_sql = f"SELECT COUNT(*) {base_sql}"

        with connections["fred"].cursor() as cursor:
            cursor.execute(count_sql, params)
            records_filtered = cursor.fetchone()[0]

        # ---- ORDERING ----
        order_columns = {
            0: "o.id",
            1: "o.name",
            2: "a.city",
            3: "ot.type",
            4: "u.first_name",
        }
        order_field = order_columns.get(order_column, "o.id")
        order_dir = "DESC" if order_dir.lower() == "desc" else "ASC"

        # ---- DATA QUERY ----
        data_sql = f"""
            SELECT
                o.id,
                o.name,
                CONCAT(a.city, ', ', a.state) AS location,
                ot.type AS officetype,
                CONCAT(u.first_name, ' ', u.last_name) AS sales
            {base_sql}
            ORDER BY {order_field} {order_dir}
            LIMIT %s OFFSET %s
        """

        data_params = params + [limit, offset]

        with connections["fred"].cursor() as cursor:
            cursor.execute(data_sql, data_params)
            cols = [c[0] for c in cursor.description]
            rows = cursor.fetchall()

        offices = [dict(zip(cols, row)) for row in rows]

        last_page = (records_filtered + limit - 1) // limit if limit else 1

        return {
            "offices": offices,
            "firstPage": 1,
            "currentPage": page,
            "lastPage": last_page,
            "recordsFiltered": records_filtered,
            "nextPage": page + 1 if page < last_page else None,
            "previousPage": max(page - 1, 1),
            "recordsTotal": records_filtered,
            "limit": limit,
        }

    @staticmethod
    def update_vendor_id(office_id: int, vendor_id: int) -> Office:
        office = OfficeService.get_one(office_id)
        with transaction.atomic(using="fred"):
            office.vendorid = vendor_id
            office.save(using="fred")
            logger.info(f"Office #{office_id} vendor ID updated to {vendor_id}")
        return office

    @staticmethod
    def get_by_netsuite_id(netsuite_id: int) -> Office:
        try:
            return Office.objects.using("fred").get(netsuiteid=netsuite_id)
        except Office.DoesNotExist:
            raise OfficeServiceException(
                f"Office with NetSuite ID {netsuite_id} not found",
                OfficeErrorCodes.ERROR_OFFICE_NOT_FOUND,
            )

    @staticmethod
    def get_list(include_inactive: bool = False) -> List[Dict[str, Any]]:
        queryset = Office.objects.using("fred").all()

        if not include_inactive:
            queryset = queryset.exclude(name__contains="(x)")

        offices = []
        for office in queryset.order_by("name"):
            offices.append(
                {
                    "id": office.id,
                    "name": office.name,
                    "netsuiteid": office.netsuiteid,
                    "created": office.created.isoformat() if office.created else None,
                    "inofficedispense": office.inofficedispense,
                }
            )

        return offices

    @staticmethod
    def get_new_offices(days: int = 30) -> List[Dict[str, Any]]:
        cutoff_date = datetime.now() - timedelta(days=days)

        queryset = (
            Office.objects.using("fred")
            .filter(created__gte=cutoff_date)
            .order_by("-created")
        )

        offices = []
        for office in queryset:
            offices.append(
                {
                    "id": office.id,
                    "name": office.name,
                    "netsuiteid": office.netsuiteid,
                    "created": office.created.isoformat() if office.created else None,
                }
            )

        return offices

    @staticmethod
    def get_updated_offices(days: int = 30) -> List[Dict[str, Any]]:
        cutoff_date = datetime.now() - timedelta(days=days)

        queryset = (
            Office.objects.using("fred")
            .filter(modified__gte=cutoff_date)
            .order_by("-modified")
        )

        offices = []
        for office in queryset:
            offices.append(
                {
                    "id": office.id,
                    "name": office.name,
                    "netsuiteid": office.netsuiteid,
                    "created": office.created.isoformat() if office.created else None,
                    "modified": (
                        office.modified.isoformat() if office.modified else None
                    ),
                }
            )

        return offices

    @staticmethod
    def get_unassigned_paginated(
        page: int = 1, limit: int = 10, search: str = None
    ) -> Dict[str, Any]:
        queryset = Office.objects.using("fred").filter(
            Q(sales__isnull=True) | Q(sales="") | Q(sales="[]")
        )

        total_records = queryset.count()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )

        filtered_records = queryset.count()

        offset = (page - 1) * limit
        queryset = queryset.order_by("name")[offset : offset + limit]

        total_pages = (filtered_records + limit - 1) // limit if limit > 0 else 1

        offices = []
        for office in queryset:
            offices.append(
                {
                    "id": office.id,
                    "name": office.name,
                    "netsuiteid": office.netsuiteid,
                    "email": office.email,
                    "created": office.created.isoformat() if office.created else None,
                }
            )

        return {
            "offices": offices,
            "currentPage": page,
            "lastPage": total_pages,
            "recordsFiltered": filtered_records,
            "recordsTotal": total_records,
            "limit": limit,
        }

    @staticmethod
    def get_list_with_address() -> List[Dict[str, Any]]:
        """Get list of offices with addresses using AddressService."""
        queryset = (
            Office.objects.using("fred").exclude(name__contains="(x)").order_by("name")
        )

        offices = []
        for office in queryset:
            office_data = {
                "id": office.id,
                "name": office.name,
                "netsuiteid": office.netsuiteid,
                "address": None,
            }

            if office.addressid:
                address = AddressService.get_one(office.addressid)
                if address:
                    office_data["address"] = {
                        "id": address.id,
                        "address1": address.address1,
                        "address2": address.address2,
                        "city": address.city,
                        "state": address.state,
                        "zip": address.zip,
                    }

            offices.append(office_data)

        return offices

    @staticmethod
    def can_prescribe(office_id: int) -> Dict[str, Any]:
        office = OfficeService.get_one(office_id)
        user_ids = OfficeService._parse_json_array(office.users)

        can_prescribe = False
        active_doctors = []

        for uid in user_ids:
            try:
                user = Users.objects.using("fred").get(pk=uid)
                if user.role == "doctor" and user.doctorid and user.status == "active":
                    try:
                        doctor = Doctor.objects.using("fred").get(pk=user.doctorid)
                        if doctor.npi:
                            can_prescribe = True
                            active_doctors.append(
                                {
                                    "userId": user.id,
                                    "doctorId": doctor.id,
                                    "name": doctor.name,
                                    "npi": doctor.npi,
                                }
                            )
                    except Doctor.DoesNotExist:
                        pass
            except Users.DoesNotExist:
                continue

        return {
            "officeId": office_id,
            "canPrescribe": can_prescribe,
            "activeDoctors": active_doctors,
            "doctorCount": len(active_doctors),
        }

    @staticmethod
    def get_leaflet(office_id: int) -> Dict[str, Any]:
        """Get office leaflet using shared services."""
        office = OfficeService.get_one(office_id)
        office_info = OfficeInfoService.get_one_by_office_id(office_id)

        address = None
        if office.addressid:
            address = AddressService.get_one(office.addressid)

        leaflet_data = {
            "officeId": office.id,
            "name": office.displayname or office.name,
            "logo": office.logo,
            "address": None,
            "phone": None,
            "fax": None,
            "email": office.officeemail or office.email,
        }

        if address:
            leaflet_data["address"] = {
                "address1": address.address1,
                "address2": address.address2,
                "city": address.city,
                "state": address.state,
                "zip": address.zip,
            }

        if office_info:
            leaflet_data["phone"] = office_info.primaryphone
            leaflet_data["fax"] = office_info.fax

        return leaflet_data

    @staticmethod
    def get_qr_code(office_id: int) -> Dict[str, Any]:
        office = OfficeService.get_one(office_id)

        base_url = "https://skinvera.com/office"
        slug = office.officeslug if office.officeslug else str(office.id)
        qr_url = f"{base_url}/{slug}"

        return {
            "officeId": office.id,
            "name": office.name,
            "slug": office.officeslug,
            "qrUrl": qr_url,
            "qrData": qr_url,
        }

    @staticmethod
    def get_reports() -> List[Dict[str, Any]]:
        return [
            {
                "id": "summary",
                "name": "Summary Report",
                "description": "Overview of office activity",
            },
            {
                "id": "inventory",
                "name": "Inventory Report",
                "description": "Current inventory status",
            },
            {
                "id": "escrow",
                "name": "Escrow Report",
                "description": "Escrow account details",
            },
            {
                "id": "rx",
                "name": "Prescription Report",
                "description": "Prescription history",
            },
            {
                "id": "payment",
                "name": "Payment Report",
                "description": "Payment history",
            },
        ]

    @staticmethod
    def merge_offices(
        source_office_id: int, target_office_id: int, user_id: int = None
    ) -> Dict[str, Any]:
        """Merge offices using OfficeHistoryService for logging."""
        source_office = OfficeService.get_one(source_office_id)
        target_office = OfficeService.get_one(target_office_id)

        if source_office_id == target_office_id:
            raise OfficeServiceException(
                "Cannot merge office into itself",
                OfficeErrorCodes.ERROR_INCORRECT_OFFICE,
            )

        with transaction.atomic(using="fred"):
            rx_count = (
                Rx.objects.using("fred")
                .filter(officeid=source_office_id)
                .update(officeid=target_office_id)
            )

            payment_count = (
                Payment.objects.using("fred")
                .filter(officeid=source_office_id)
                .update(officeid=target_office_id)
            )

            source_users = OfficeService._parse_json_array(source_office.users)
            target_users = OfficeService._parse_json_array(target_office.users)
            merged_users = list(set(target_users + source_users))
            target_office.users = json.dumps(merged_users)

            source_sales = OfficeService._parse_json_array(source_office.sales)
            target_sales = OfficeService._parse_json_array(target_office.sales)
            merged_sales = list(set(target_sales + source_sales))
            target_office.sales = json.dumps(merged_sales)

            target_office.save(using="fred")

            if "(x)" not in source_office.name:
                source_office.name = f"{source_office.name} (x)"
                source_office.save(using="fred")

            # Use OfficeHistoryService for logging
            OfficeHistoryService.log(
                office_id=target_office_id,
                user_id=user_id or 0,
                triggered_action="mergeAction",
                old_data=json.dumps({"sourceOfficeId": source_office_id}),
                new_data=json.dumps(
                    {
                        "rxMoved": rx_count,
                        "paymentsMoved": payment_count,
                        "usersMerged": len(source_users),
                    }
                ),
            )

            logger.info(f"Merged office #{source_office_id} into #{target_office_id}")

        return {
            "success": True,
            "sourceOfficeId": source_office_id,
            "targetOfficeId": target_office_id,
            "rxMoved": rx_count,
            "paymentsMoved": payment_count,
            "usersMerged": len(source_users),
            "salesMerged": len(source_sales),
        }

    @staticmethod
    def get_leaflet_sample() -> Dict[str, Any]:
        return {
            "template": "default",
            "sections": [
                {"id": "header", "name": "Header", "required": True},
                {"id": "about", "name": "About Us", "required": False},
                {"id": "services", "name": "Services", "required": False},
                {"id": "contact", "name": "Contact Info", "required": True},
                {"id": "footer", "name": "Footer", "required": True},
            ],
            "sampleData": {
                "name": "Sample Medical Office",
                "displayname": "Sample Medical",
                "logo": "https://example.com/sample-logo.png",
                "aboutHtml": "<p>Welcome to our practice.</p>",
                "address": {
                    "address1": "123 Medical Way",
                    "city": "Healthcare City",
                    "state": "CA",
                    "zip": "90210",
                },
                "phone": "555-123-4567",
                "fax": "555-123-4568",
                "email": "info@sampleoffice.com",
            },
        }

    @staticmethod
    def get_summary_report_data(
        office_id: int, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """
        Get summary report data matching PHP getSummaryReportData.
        Date format expected: DD/MM/YYYY
        """
        try:
            summary_sql = """
                WITH
                all_active_skus AS (
                    SELECT DISTINCT sku FROM vi_items WHERE officeid = %(office_id)s
                    UNION
                    SELECT DISTINCT med.formulacode as sku 
                    FROM vi_proceeds vp
                    JOIN rx ON vp.rxid = rx.id
                    JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s
                ),
                office_info AS (
                    SELECT DISTINCT o.name as office_name
                    FROM office o 
                    WHERE o.id = %(office_id)s
                ),
                proceeds_by_sku AS (
                    SELECT
                        med.formulacode AS sku,
                        SUM(vp.qty) AS total_qty,
                        SUM(vp.proceeds) AS total_proceeds,
                        SUM(vp.shippingandhandlingfee) AS total_sh_fees,
                        SUM((vp.viprice * vp.qty) - vp.discounttotal) AS viprice
                    FROM vi_proceeds vp
                    JOIN rx ON vp.rxid = rx.id
                    JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY med.formulacode
                ),
                proceeds_by_sku_old AS (
                    SELECT
                        med.formulacode AS sku,
                        SUM(vp.qty) AS total_qty
                    FROM vi_proceeds vp
                    JOIN rx ON vp.rxid = rx.id
                    JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created < TO_DATE(%(start_date)s, 'DD/MM/YYYY')
                    GROUP BY med.formulacode
                ),
                beginning_inventory_by_sku AS (
                    SELECT
                        vi_items.sku,
                        COALESCE(SUM(vi_items.qty), 0) - COALESCE(pb.total_qty, 0) AS beginning_inventory
                    FROM vi_items
                    LEFT JOIN proceeds_by_sku_old pb ON pb.sku = vi_items.sku
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate < TO_DATE(%(start_date)s, 'DD/MM/YYYY')
                    GROUP BY vi_items.sku, pb.total_qty
                ),
                auto_replenishment_by_sku AS (
                    SELECT
                        vi_items.sku,
                        COALESCE(SUM(vi_items.qty), 0) AS auto_replenishment_qty,
                        COALESCE(SUM(vi_items.itemtotalamount), 0) AS auto_replenishment_cost
                    FROM vi_items
                    LEFT JOIN vi_orders vo ON vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    AND vo.ordersequencetype = 'AUTO'
                    GROUP BY vi_items.sku
                ),
                all_inventory_by_sku AS (
                    SELECT
                        vi_items.sku,
                        COALESCE(SUM(vi_items.qty), 0) AS total_inventory_change
                    FROM vi_items
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                first_stock_dates AS (
                    SELECT
                        vi_items.sku,
                        vo.transactiondate AS date_of_first_stock
                    FROM vi_items
                    JOIN vi_orders vo ON vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND vo.ordersequencetype = 'FIRST'
                ),
                last_replenish_dates AS (
                    SELECT
                        vi_items.sku,
                        MAX(vo.transactiondate) AS date_of_last_replenish
                    FROM vi_items
                    JOIN vi_orders vo ON vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND (vo.ordersequencetype = 'AUTO' or vo.ordersequencetype = 'MANUAL')
                    AND vo.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                average_purchase_cost_by_sku AS (
                    SELECT
                        vi_items.sku,
                        AVG(vi_items.vicost) AS avg_purchase_cost
                    FROM vi_items
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    AND vi_items.vicost IS NOT NULL
                    GROUP BY vi_items.sku
                ),
                value_per_sku AS (
                    SELECT 
                        vi_items.sku, 
                        SUM(vi_items.itemtotalamount::NUMERIC) / SUM(vi_items.qty) AS average_price_per_sku
                    FROM vi_items
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                units_dispensed_by_sku AS (
                    SELECT
                        med.formulacode AS sku,
                        SUM(vp.qty::NUMERIC) AS dispensed_qty,
                        SUM(vp.qty::NUMERIC) * vps.average_price_per_sku AS dispensed_value
                    FROM vi_proceeds vp
                    INNER JOIN rx ON rx.id = vp.rxid
                    INNER JOIN medication med ON med.ndc = rx.medicationid
                    INNER JOIN value_per_sku vps ON vps.sku = med.formulacode
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY med.formulacode, vps.average_price_per_sku
                ),
                initial_purchases_by_sku AS (
                    SELECT
                        vi_items.sku,
                        COALESCE(SUM(vi_items.qty), 0) AS initial_purchase_qty,
                        COALESCE(SUM(vi_items.itemtotalamount::NUMERIC), 0) AS initial_purchase_amount
                    FROM vi_items
                    INNER JOIN vi_orders ON vi_orders.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    AND vi_orders.ordersequencetype = 'FIRST'
                    GROUP BY vi_items.sku
                ),
                midmonth_replenishments_by_sku AS (
                    SELECT
                        vi_items.sku,
                        COALESCE(SUM(vi_items.qty), 0) AS midmonth_replenish_qty,
                        COALESCE(SUM(vi_items.itemtotalamount::NUMERIC), 0) AS midmonth_replenish_amount
                    FROM vi_items
                    INNER JOIN vi_orders ON vi_orders.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    AND (vi_orders.ordersequencetype = 'AUTO' OR vi_orders.ordersequencetype = 'MANUAL')
                    GROUP BY vi_items.sku
                ),
                eom_replenishments_by_sku AS (
                    SELECT
                        vi_items.sku,
                        COALESCE(SUM(vi_items.qty), 0) AS eom_replenish_qty,
                        COALESCE(SUM(vi_items.itemtotalamount::NUMERIC), 0) AS eom_replenish_amount
                    FROM vi_items
                    INNER JOIN vi_orders ON vi_orders.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    AND vi_orders.ordersequencetype = 'EOM'
                    GROUP BY vi_items.sku
                ),
                summary_by_sku AS (
                    SELECT
                        sku.sku AS product,
                        oi.office_name,
                        COALESCE(bi.beginning_inventory, 0) AS beginning_inventory,
                        COALESCE(pb.total_qty, 0) AS dispensed_units,
                        COALESCE(pb.viprice, 0) AS viprice,
                        COALESCE(pb.total_proceeds, 0) AS dispensed_payment,
                        COALESCE(pb.total_sh_fees, 0) AS sh_fees,
                        COALESCE(ar.auto_replenishment_qty, 0) AS inventory_replenishment,
                        COALESCE(ar.auto_replenishment_cost, 0) AS replenishment_cost,
                        (COALESCE(bi.beginning_inventory, 0) + COALESCE(ai.total_inventory_change, 0) - COALESCE(ud.dispensed_qty, 0)) AS ending_inventory,
                        (COALESCE(pb.total_proceeds, 0) - COALESCE(ar.auto_replenishment_cost, 0) - COALESCE(er.eom_replenish_amount, 0)) AS balance_owed,
                        (COALESCE(pb.viprice, 0) - COALESCE(ar.auto_replenishment_cost, 0) - COALESCE(er.eom_replenish_amount, 0)) AS net_Proceeds_before_sh,
                        fs.date_of_first_stock,
                        lr.date_of_last_replenish,
                        CAST(ROUND(CAST((COALESCE(bi.beginning_inventory, 0) + COALESCE(ai.total_inventory_change, 0) - COALESCE(ud.dispensed_qty, 0)) * COALESCE(apc.avg_purchase_cost, 0) AS NUMERIC), 2) AS NUMERIC(15,2)) AS value_of_ending_inventory,
                        COALESCE(ip.initial_purchase_qty, 0) AS initial_purchase_qty,
                        COALESCE(ip.initial_purchase_amount, 0) AS initial_purchase_amount,
                        COALESCE(mr.midmonth_replenish_qty, 0) AS midmonth_replenish_qty,
                        COALESCE(mr.midmonth_replenish_amount, 0) AS midmonth_replenish_amount,
                        COALESCE(er.eom_replenish_qty, 0) AS eom_replenish_qty,
                        COALESCE(er.eom_replenish_amount, 0) AS eom_replenish_amount,
                        COALESCE(ud.dispensed_value, 0) AS dispensed_value
                    FROM all_active_skus sku
                    CROSS JOIN office_info oi
                    LEFT JOIN proceeds_by_sku pb ON sku.sku = pb.sku
                    LEFT JOIN units_dispensed_by_sku ud ON sku.sku = ud.sku
                    LEFT JOIN auto_replenishment_by_sku ar ON sku.sku = ar.sku
                    LEFT JOIN all_inventory_by_sku ai ON sku.sku = ai.sku
                    LEFT JOIN beginning_inventory_by_sku bi ON sku.sku = bi.sku
                    LEFT JOIN first_stock_dates fs ON sku.sku = fs.sku
                    LEFT JOIN last_replenish_dates lr ON sku.sku = lr.sku
                    LEFT JOIN average_purchase_cost_by_sku apc ON sku.sku = apc.sku
                    LEFT JOIN initial_purchases_by_sku ip ON sku.sku = ip.sku
                    LEFT JOIN midmonth_replenishments_by_sku mr ON sku.sku = mr.sku
                    LEFT JOIN eom_replenishments_by_sku er ON sku.sku = er.sku
                )
                SELECT * FROM summary_by_sku ORDER BY product
            """

            profit_sql = """
                WITH proceeds_by_doctor_sku AS (
                    SELECT
                        med.formulacode AS sku,
                        vp.doctorid,
                        SUM(vp.qty) AS doctor_qty,
                        SUM(vp.proceeds) AS gross_proceeds,
                        SUM(COALESCE(vp.discounttotal, 0)) AS total_discount,
                        SUM(vp.proceeds) AS doctor_proceeds,
                        SUM(vp.shippingandhandlingfee) AS total_sh_fees
                    FROM vi_proceeds vp
                    JOIN rx ON vp.rxid = rx.id
                    JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY med.formulacode, vp.doctorid
                ),
                total_dispensed_by_sku AS (
                    SELECT
                        sku,
                        SUM(doctor_qty) AS total_qty,
                        SUM(doctor_proceeds) AS total_doctor_proceeds
                    FROM proceeds_by_doctor_sku
                    GROUP BY sku
                ),
                replenishment_cost_by_sku AS (
                    SELECT
                        vi_items.sku,
                        SUM(vi_items.itemtotalamount) AS total_replenishment_cost
                    FROM vi_items
                    LEFT JOIN vi_orders vo on vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    AND vo.ordersequencetype = 'AUTO'
                    GROUP BY vi_items.sku
                ),
                eom_replenishment_cost_by_sku AS (
                    SELECT
                        vi_items.sku,
                        SUM(vi_items.itemtotalamount) AS total_eom_replenishment_cost
                    FROM vi_items
                    LEFT JOIN vi_orders vo on vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    AND vo.ordersequencetype = 'EOM'
                    GROUP BY vi_items.sku
                ),
                doctor_profit_calculation AS (
                    SELECT
                        pds.sku,
                        pds.doctorid,
                        pds.doctor_qty,
                        pds.doctor_proceeds,
                        tds.total_qty,
                        tds.total_doctor_proceeds,
                        COALESCE(rcs.total_replenishment_cost, 0) AS total_replenishment_cost,
                        COALESCE(ercs.total_eom_replenishment_cost, 0) AS total_eom_replenishment_cost,
                        (COALESCE(rcs.total_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty) AS allocated_auto_cost,
                        (COALESCE(ercs.total_eom_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty) AS allocated_eom_cost,
                        (pds.doctor_proceeds - 
                        (COALESCE(rcs.total_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty) -
                        (COALESCE(ercs.total_eom_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty)
                        ) AS doctor_profit
                    FROM proceeds_by_doctor_sku pds
                    JOIN total_dispensed_by_sku tds ON pds.sku = tds.sku
                    LEFT JOIN replenishment_cost_by_sku rcs ON pds.sku = rcs.sku
                    LEFT JOIN eom_replenishment_cost_by_sku ercs ON pds.sku = ercs.sku
                ),
                doctor_info AS (
                    SELECT
                        doc.id as doctorid,
                        doc.npi,
                        doc.name
                    FROM doctor doc
                ),
                office_info AS (
                    SELECT id AS officeid, viproceedstype
                    FROM office
                    WHERE id = %(office_id)s
                ),
                doctor_split AS (
                    SELECT id, splitpercent, npi, officeid, vendorid
                    FROM vi_doctor
                    WHERE officeid = %(office_id)s
                ),
                doctor_shares AS (
                    SELECT
                        dpc.doctorid,
                        dpc.sku,
                        dpc.doctor_qty,
                        di.name,
                        di.npi,
                        dpc.doctor_proceeds,
                        dpc.allocated_auto_cost,
                        dpc.allocated_eom_cost,
                        dpc.doctor_profit,
                        oi.viproceedstype,
                        CASE 
                            WHEN oi.viproceedstype = 1 THEN 0
                            WHEN oi.viproceedstype = 2 THEN 100
                            WHEN oi.viproceedstype = 3 THEN COALESCE(ds.splitpercent, 0)
                            ELSE 0
                        END AS splitpercent,
                        CASE 
                            WHEN ds.vendorid IS NULL THEN true
                            ELSE false
                        END AS isescrowheld
                    FROM doctor_profit_calculation dpc
                    JOIN doctor_info di ON dpc.doctorid = di.doctorid
                    CROSS JOIN office_info oi
                    LEFT JOIN doctor_split ds ON di.npi = ds.npi AND ds.officeid = %(office_id)s
                ),
                final_shares AS (
                    SELECT
                        doctorid,
                        name,
                        npi,
                        doctor_profit,
                        viproceedstype,
                        splitpercent,
                        isescrowheld,
                        CASE 
                            WHEN viproceedstype IS NULL OR viproceedstype = 1 THEN 0
                            WHEN viproceedstype = 2 THEN doctor_profit
                            WHEN viproceedstype = 3 THEN doctor_profit * COALESCE(splitpercent, 0) / 100.0
                            ELSE 0
                        END AS doctor_share,
                        CASE 
                            WHEN viproceedstype IS NULL OR viproceedstype = 1 THEN doctor_profit
                            WHEN viproceedstype = 2 THEN 0
                            WHEN viproceedstype = 3 THEN doctor_profit * (100.0 - COALESCE(splitpercent, 0)) / 100.0
                            ELSE doctor_profit
                        END AS office_share
                    FROM doctor_shares
                )
                SELECT
                    doctorid,
                    name,
                    splitpercent,
                    SUM(doctor_share) AS doctor_share,
                    SUM(office_share) AS office_share,
                    BOOL_OR(isescrowheld) AS isescrowheld
                FROM final_shares
                GROUP BY doctorid, splitpercent, name
                ORDER BY doctorid
            """

            params = {
                "office_id": office_id,
                "start_date": start_date,
                "end_date": end_date,
            }

            with connections["fred"].cursor() as cursor:
                cursor.execute(summary_sql, params)
                summary_columns = [col[0] for col in cursor.description]
                summary_rows = cursor.fetchall()
                summary_result = [
                    dict(zip(summary_columns, row)) for row in summary_rows
                ]

                cursor.execute(profit_sql, params)
                profit_columns = [col[0] for col in cursor.description]
                profit_rows = cursor.fetchall()
                profit_result = [dict(zip(profit_columns, row)) for row in profit_rows]

            return {
                "summary": summary_result,
                "profitShare": profit_result,
            }

        except Exception as e:
            logger.error(f"Error in get_summary_report_data: {e}")
            return {
                "error": True,
                "message": "Failed to generate report. Please check logs.",
            }

    @staticmethod
    def get_inventory_report_data(
        office_id: int, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """
        Get inventory report data matching PHP getInventoryReportData.
        Date format expected: DD/MM/YYYY
        """
        try:
            query = """
                WITH
                proceeds AS (
                    SELECT
                        o.name AS officename,
                        med.formulacode AS sku,
                        vp.qty,
                        vp.proceeds,
                        vp.doctorid,
                        doc.npi,
                        doc.name,
                        vp.created,
                        vp.servicefee + vp.shippingandhandlingfee as feesperagreement,
                        vp.discounttotal,
                        vp.viprice
                    FROM vi_proceeds vp
                    JOIN rx ON vp.rxid = rx.id
                    JOIN medication med ON rx.medicationid = med.ndc
                    JOIN doctor doc ON vp.doctorid = doc.id
                    JOIN office o ON vp.officeid = o.id
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                ),

                combined_transactions AS (
                    SELECT
                        o.name AS office_name,
                        vo.transactiondate AS date,
                        vi.sku AS product,
                        vo.ordersequencetype AS order_type,
                        vi.vicost AS unit_cost,
                        vi.qty AS purchased_units,
                        0 AS dispensed_units,
                        0 AS dispensed_payment,
                        0 AS discount,
                        vi.expirationdate AS product_exp_date,
                        0 AS fees_per_agreement,
                        0 as proceeds,
                        NULL AS doctor_name,
                        0 as doctorid,
                        'IN' AS record_type
                    FROM vi_orders vo
                    JOIN office o ON vo.officeid = o.id
                    JOIN vi_items vi ON vi.officeid = vo.officeid AND vo.id = vi.orderid
                    WHERE vo.officeid = %(office_id)s
                    AND vo.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND

                    UNION ALL

                    SELECT
                        p.officename AS office_name,
                        p.created AS date,
                        p.sku AS product,
                        NULL AS order_type,
                        NULL AS unit_cost,
                        0 AS purchased_units,
                        p.qty AS dispensed_units,
                        p.viprice AS dispensed_payment,
                        p.discounttotal AS discount,
                        NULL AS product_exp_date,
                        p.feesperagreement AS fees_per_agreement,
                        p.proceeds as proceeds,
                        p.name AS doctor_name,
                        p.doctorid as doctorid,
                        'OUT' AS record_type
                    FROM proceeds p
                )

                SELECT 
                    office_name,
                    date,
                    product,
                    order_type,
                    unit_cost,
                    purchased_units,
                    dispensed_units,
                    dispensed_units * dispensed_payment as dispensed_payment,
                    discount,
                    SUM(purchased_units - dispensed_units) OVER (
                        PARTITION BY product 
                        ORDER BY date ASC, record_type DESC 
                        ROWS UNBOUNDED PRECEDING
                    ) AS balanced_units,
                    product_exp_date,
                    fees_per_agreement,
                    proceeds,
                    doctor_name,
                    doctorid,
                    record_type
                FROM combined_transactions
            """

            params = {
                "office_id": office_id,
                "start_date": start_date,
                "end_date": end_date,
            }

            with connections["fred"].cursor() as cursor:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]

            return {
                "success": True,
                "result": result,
                "count": len(result),
            }

        except Exception as e:
            logger.error(f"Error in get_inventory_report_data: {e}")
            return {
                "error": True,
                "message": "Failed to generate inventory report. Please check logs.",
                "debug": str(e),
            }

    @staticmethod
    def get_escrow_report_data(
        office_id: int, start_date: str, end_date: str
    ) -> Dict[str, Any]:
        """
        Get escrow report data matching PHP getEscrowReportData.
        Date format expected: DD/MM/YYYY
        """
        try:
            query = """
                SELECT
                    o.name AS office_name,
                    p.created AS dispensed_date,
                    m.formulacode AS sku,
                    p.qty AS dispensed_unit,
                    p.qty * p.viprice AS dispensed_amount,
                    r.patientid AS patientid,
                    d.name AS doctor_name,
                    r.id AS fredid,
                    vid.vendorid AS vendorid
                FROM vi_profits_report vpr
                JOIN LATERAL jsonb_array_elements(vpr.payload::jsonb -> 'escrowHeld') AS escrow(entry) ON TRUE
                JOIN LATERAL jsonb_array_elements_text(escrow.entry -> 'proceedIdList') AS pid(proceed_id) ON TRUE
                JOIN vi_proceeds p ON p.id = pid.proceed_id::int
                JOIN rx r ON r.id = p.rxid
                JOIN office o ON vpr.officeid = o.id::int
                JOIN medication m ON m.ndc = r.medicationid
                JOIN doctor d ON d.npi = (escrow.entry ->> 'fredDoctorNPI')
                JOIN vi_doctor vid ON vid.npi = (escrow.entry ->> 'fredDoctorNPI')
                WHERE vpr.officeid = %(office_id)s
                AND vpr.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
            """

            params = {
                "office_id": office_id,
                "start_date": start_date,
                "end_date": end_date,
            }

            with connections["fred"].cursor() as cursor:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]

            return {
                "success": True,
                "result": result,
                "count": len(result),
            }

        except Exception as e:
            logger.error(f"Error in get_escrow_report_data : {e}")
            return {
                "error": True,
                "message": "Failed to generate escrow report. Please check logs.",
                "debug": str(e),
            }

    @staticmethod
    def get_skincare_pairings(office_id: int) -> List[Dict[str, Any]]:
        OfficeService.get_one(office_id)

        pairings = (
            Skincarepairings.objects.using("fred")
            .filter(fredofficeid=str(office_id))
            .order_by("-date_created")
        )

        results = []
        for pairing in pairings:
            results.append(
                {
                    "id": pairing.id,
                    "sku": pairing.sku,
                    "productName": pairing.product_name,
                    "orderId": pairing.order_id,
                    "orderStatus": pairing.order_status,
                    "productNetRevenue": pairing.product_net_revenue,
                    "dateCreated": (
                        pairing.date_created.isoformat()
                        if pairing.date_created
                        else None
                    ),
                    "prescriberNpi": pairing.prescribernpi,
                }
            )

        return results

    # @staticmethod
    # def get_provider_skincare_pairings(office_id: int) -> List[Dict[str, Any]]:
    #     OfficeService.get_one(office_id)

    #     pairings = (
    #         Skincarepairings.objects.using("fred")
    #         .filter(fredofficeid=str(office_id))
    #         .values("prescribernpi")
    #         .annotate(
    #             total_revenue=Sum("product_net_revenue"),
    #             order_count=Count("order_id", distinct=True),
    #             product_count=Count("id"),
    #         )
    #     )

    #     results = []
    #     for pairing in pairings:
    #         npi = pairing["prescribernpi"]
    #         provider_data = {
    #             "npi": npi,
    #             "doctorName": None,
    #             "totalRevenue": pairing["total_revenue"] or 0,
    #             "orderCount": pairing["order_count"],
    #             "productCount": pairing["product_count"],
    #         }

    #         if npi:
    #             try:
    #                 doctor = Doctor.objects.using("fred").filter(npi=npi).first()
    #                 if doctor:
    #                     provider_data["doctorName"] = doctor.name
    #             except:
    #                 pass

    #         results.append(provider_data)

    #     return results

    # @staticmethod
    # def get_provider_skincare_pairings(user, start_date: str, end_date: str):
    #     # PHP equivalent of getOfficeIdsOfSalesAndManagers()
    #     office_ids = OfficeService.get_office_ids_of_sales_and_managers(user)

    #     start_dt = datetime.combine(
    #         datetime.strptime(start_date, "%Y-%m-%d").date(), time.min
    #     )
    #     end_dt = datetime.combine(
    #         datetime.strptime(end_date, "%Y-%m-%d").date(), time.max
    #     )

    #     queryset = (
    #         Skincarepairings.objects.using("fred")
    #         .filter(
    #             fredofficeid__in=office_ids,
    #             created__range=(start_dt, end_dt),
    #         )
    #         .values("fredofficeid", "prescribernpi")
    #         .annotate(
    #             total_revenue=Sum("product_net_revenue"),
    #             order_count=Count("order_id", distinct=True),
    #             product_count=Count("id"),
    #         )
    #     )

    #     result = {}

    #     for row in queryset:
    #         office_id = row["fredofficeid"]
    #         npi = row["prescribernpi"]

    #         doctor = (
    #             Doctor.objects.using("fred")
    #             .filter(npi=npi)
    #             .values("name")
    #             .first()
    #         )

    #         result.setdefault(office_id, []).append({
    #             "npi": npi,
    #             "doctorName": doctor["name"] if doctor else None,
    #             "totalRevenue": row["total_revenue"] or 0,
    #             "orderCount": row["order_count"],
    #             "productCount": row["product_count"],
    #         })

    #     return result

    @staticmethod
    def get_provider_skincare_pairings(user, start_date: str, end_date: str):
        office_ids = OfficeService.get_office_ids_of_sales_and_managers(user)

        start_dt = datetime.combine(
            datetime.strptime(start_date, "%Y-%m-%d").date(), time.min
        )
        end_dt = datetime.combine(
            datetime.strptime(end_date, "%Y-%m-%d").date(), time.max
        )

        queryset = (
            Skincarepairings.objects.using("fred")
            .filter(
                fredofficeid__in=office_ids,
                date_created__range=(start_dt, end_dt),  # ✅ FIXED
            )
            .values("fredofficeid", "prescribernpi")
            .annotate(
                total_revenue=Sum("product_net_revenue"),
                order_count=Count("order_id", distinct=True),
                product_count=Count("id"),
            )
        )

        result = {}

        for row in queryset:
            office_id = row["fredofficeid"]
            npi = row["prescribernpi"]

            doctor = (
                Doctor.objects.using("fred")
                .filter(npi=npi)
                .values("name")
                .first()
            )

            result.setdefault(office_id, []).append({
                "npi": npi,
                "doctorName": doctor["name"] if doctor else None,
                "totalRevenue": row["total_revenue"] or 0,
                "orderCount": row["order_count"],
                "productCount": row["product_count"],
            })

        return result

    @staticmethod
    def get_office_ids_of_sales_and_managers(user) -> List[int]:
        """
        Python equivalent of PHP getOfficeIdsOfSalesAndManagers()
        """

        # Normalize roles
        roles = []

        if hasattr(user, "roles"):
            try:
                # ManyToMany (most likely)
                roles = list(user.roles.values_list("name", flat=True))
            except Exception:
                # List / tuple fallback
                roles = list(user.roles)

        # Admin → all offices
        if user.is_superuser or "admin" in roles:
            return list(
                Office.objects.using("fred")
                .values_list("id", flat=True)
            )

        # Sales / Sales Manager
        if "sales" in roles or "sales-manager" in roles:
            return list(
                Office.objects.using("fred")
                .filter(sales_rep_id=user.id)  # adjust if column differs
                .values_list("id", flat=True)
            )

        return []

    @staticmethod
    def get_dio_by_sku(office_id: int, sku: str = None) -> Dict[str, Any]:
        office = OfficeService.get_one(office_id)

        if not office.dio2:
            return {"success": True, "result": [], "count": 0}

        # Latest medication per formulacode (ROW_NUMBER equivalent)
        latest_med = (
            Medication.objects.using("fred")
            .filter(formulacode=OuterRef("formulacode"))
            .order_by("-created")
        )

        queryset = (
            DioItems.objects.using("fred")
            .filter(
                officeid=office_id,
                formulacode__in=Medication.objects.using("fred")
                .values("formulacode")
            )
            .annotate(
                office_name=Subquery(
                    Office.objects.filter(id=OuterRef("officeid")).values("name")[:1]
                ),
                ndc=Subquery(latest_med.values("ndc")[:1]),
                brand_name=Subquery(latest_med.values("brand_name")[:1]),
                formula=Subquery(latest_med.values("formula")[:1]),
                upper=Upper(Subquery(latest_med.values("indication")[:1])),
            )
        )

        if sku:
            queryset = queryset.filter(formulacode__icontains=sku)

        # IMPORTANT: rename fields here, NOT in annotate
        result = [
            {
                "dio_id": item.id,            # dio_items.id
                "id": item.officeid,          # office.id
                "name": item.office_name,     # office.name
                "formulacode": item.formulacode,
                "ndc": item.ndc,
                "brand_name": item.brand_name,
                "formula": item.formula,
                "upper": item.upper,
                "active": item.active,
            }
            for item in queryset
        ]

        return {
            "success": True,
            "result": result,
            "count": len(result),
        }


    @staticmethod
    def update_skus(office_id: int, skus: List[Dict[str, Any]]) -> Dict[str, Any]:
        OfficeService.get_one(office_id)

        added = 0
        updated = 0
        deactivated = 0

        with transaction.atomic(using="fred"):
            for sku_data in skus:
                formulacode = sku_data.get("formulacode")
                active = sku_data.get("active", True)

                if not formulacode:
                    continue

                existing = (
                    DioItems.objects.using("fred")
                    .filter(officeid=office_id, formulacode=formulacode)
                    .first()
                )

                if existing:
                    if existing.active != active:
                        existing.active = active
                        existing.save(using="fred")
                        if active:
                            updated += 1
                        else:
                            deactivated += 1
                else:
                    DioItems.objects.using("fred").create(
                        officeid=office_id, formulacode=formulacode, active=active
                    )
                    added += 1

            logger.info(
                f"Updated SKUs for office #{office_id}: added={added}, updated={updated}, deactivated={deactivated}"
            )

        return {
            "officeId": office_id,
            "added": added,
            "updated": updated,
            "deactivated": deactivated,
            "success": True,
        }

    # @staticmethod
    # def load_dio(office_id: int = None) -> Dict[str, Any]:
    #     if office_id:
    #         offices = [OfficeService.get_one(office_id)]
    #     else:
    #         offices = (
    #             Office.objects.using("fred")
    #             .filter(dio2=True)
    #             .exclude(name__contains="(x)")
    #         )

    #     dio_data = []
    #     for office in offices:
    #         items = DioItems.objects.using("fred").filter(
    #             officeid=office.id, active=True
    #         )

    #         office_items = []
    #         for item in items:
    #             item_data = {
    #                 "id": item.id,
    #                 "formulacode": item.formulacode,
    #                 "active": item.active,
    #             }

    #             try:
    #                 med = Medication.objects.using("fred").get(
    #                     formulacode=item.formulacode
    #                 )
    #                 item_data["medication"] = {
    #                     "ndc": med.ndc,
    #                     "formula": med.formula,
    #                     "brand_name": med.brand_name,
    #                     "dosage": med.dosage,
    #                     "size": med.size,
    #                 }
    #             except Medication.DoesNotExist:
    #                 item_data["medication"] = None

    #             office_items.append(item_data)

    #         dio_data.append(
    #             {
    #                 "officeId": office.id,
    #                 "officeName": office.name,
    #                 "dio2Enabled": office.dio2,
    #                 "virtualInventoryEnabled": office.virtualinventoryenabled,
    #                 "viStatus": office.vi_status,
    #                 "replenishmentOptout": office.replenishmentoptout,
    #                 "itemCount": len(office_items),
    #                 "items": office_items,
    #             }
    #         )

    #     return {"officeCount": len(dio_data), "offices": dio_data}

    # @staticmethod
    # def load_dio(office_id: int = None) -> Dict[str, Any]:
    #     if office_id:
    #         offices = [OfficeService.get_one(office_id)]
    #     else:
    #         offices = (
    #             Office.objects.using("fred")
    #             .filter(dio2=True)
    #             .exclude(name__contains="(x)")
    #         )

    #     dio_data = []

    #     for office in offices:
    #         items = DioItems.objects.using("fred").filter(
    #             officeid=office.id, active=True
    #         )

    #         office_items = []

    #         for item in items:
    #             item_data = {
    #                 "id": item.id,
    #                 "formulacode": item.formulacode,
    #                 "active": item.active,
    #             }

    #             # ✅ SAFE: latest medication only
    #             med = (
    #                 Medication.objects.using("fred")
    #                 .filter(formulacode=item.formulacode)
    #                 .order_by("-date_created")  # IMPORTANT
    #                 .first()
    #             )

    #             if med:
    #                 item_data["medication"] = {
    #                     "ndc": med.ndc,
    #                     "formula": med.formula,
    #                     "brand_name": med.brand_name,
    #                     "dosage": med.dosage,
    #                     "size": med.size,
    #                 }
    #             else:
    #                 item_data["medication"] = None

    #             office_items.append(item_data)

    #         dio_data.append(
    #             {
    #                 "officeId": office.id,
    #                 "officeName": office.name,
    #                 "dio2Enabled": office.dio2,
    #                 "virtualInventoryEnabled": office.virtualinventoryenabled,
    #                 "viStatus": office.vi_status,
    #                 "replenishmentOptout": office.replenishmentoptout,
    #                 "itemCount": len(office_items),
    #                 "items": office_items,
    #             }
    #         )

    #     return {"officeCount": len(dio_data), "offices": dio_data}

    @staticmethod
    def load_dio_item(office_id: int, netsuiteid: int, sku: str):
        try:
            if not office_id or not sku:
                return {
                    "error": True,
                    "message": "officeid and sku are required",
                }

            # PHP: if strlen($sku) < 6 → prepend 0
            sku = str(sku)
            if len(sku) < 6:
                sku = sku.zfill(6)

            # PHP: getDIOItemByOfficeIdAndFormulaCodeIgnoreActive
            exists = DioItems.objects.using("fred").filter(
                officeid=office_id,
                formulacode=sku,
            ).exists()

            if not exists:
                new_item = DioItems.objects.using("fred").create(
                    officeid=office_id,
                    netsuiteid=netsuiteid,
                    formulacode=sku,
                    active=True,
                )

                return {
                    "error": False,
                    "message": new_item.id,
                }

            return {
                "error": True,
                "message": "DIO Item already exists for office",
            }

        except Exception as e:
            return {
                "error": True,
                "message": str(e),
            }


    @staticmethod
    def save_dio_shipment(
        office_id: int, shipment_data: Dict[str, Any], user_id: int = None
    ) -> Dict[str, Any]:
        """Save DIO shipment using OfficeHistoryService for logging."""
        OfficeService.get_one(office_id)

        items = shipment_data.get("items", [])
        tracking = shipment_data.get("tracking")
        carrier = shipment_data.get("carrier")
        notes = shipment_data.get("notes")

        processed_items = []

        with transaction.atomic(using="fred"):
            for item in items:
                formulacode = item.get("formulacode")
                qty = item.get("qty", 0)
                lot = item.get("lot")
                expiration = item.get("expiration")

                if not formulacode:
                    continue

                dio_item, created = DioItems.objects.using("fred").get_or_create(
                    officeid=office_id,
                    formulacode=formulacode,
                    defaults={"active": True},
                )

                processed_items.append(
                    {
                        "formulacode": formulacode,
                        "qty": qty,
                        "lot": lot,
                        "expiration": expiration,
                        "dioItemId": dio_item.id,
                        "created": created,
                    }
                )

            # Use OfficeHistoryService for logging
            OfficeHistoryService.log(
                office_id=office_id,
                user_id=user_id or 0,
                triggered_action="saveDioShipmentAction",
                old_data=None,
                new_data=json.dumps(
                    {
                        "tracking": tracking,
                        "carrier": carrier,
                        "itemCount": len(processed_items),
                    }
                ),
            )

            logger.info(
                f"Saved DIO shipment for office #{office_id}: {len(processed_items)} items"
            )

        return {
            "success": True,
            "officeId": office_id,
            "tracking": tracking,
            "carrier": carrier,
            "notes": notes,
            "itemsProcessed": len(processed_items),
            "items": processed_items,
        }
    
    @staticmethod
    def shipment_exists(sonumber, ifnumber, sku, netsuiteid, lotnumber):
        return DioShipments.objects.using("fred").filter(
            sonumber=sonumber,
            ifnumber=ifnumber,
            sku=sku,
            netsuiteid=netsuiteid,
            lotnumber=lotnumber,
        ).exists()

    @staticmethod
    def dio_opt_out(office_id: int, user_id: int = None) -> Dict[str, Any]:
        """Opt out of DIO using OfficeHistoryService for logging."""
        office = OfficeService.get_one(office_id)

        with transaction.atomic(using="fred"):
            old_value = office.replenishmentoptout
            office.replenishmentoptout = True
            office.save(using="fred")

            # Use OfficeHistoryService for logging
            OfficeHistoryService.log(
                office_id=office_id,
                user_id=user_id or 0,
                triggered_action="dioOptoutAction",
                old_data=json.dumps({"replenishmentoptout": old_value}),
                new_data=json.dumps({"replenishmentoptout": True}),
            )

            logger.info(f"Office #{office_id} opted out of DIO replenishment")

        return {
            "success": True,
            "officeId": office_id,
            "replenishmentOptout": True,
            "message": "Office has been opted out of DIO replenishment",
        }

    @staticmethod
    def dio_opt_in(office_id: int, user_id: int = None) -> Dict[str, Any]:
        """Opt in to DIO using OfficeHistoryService for logging."""
        office = OfficeService.get_one(office_id)

        with transaction.atomic(using="fred"):
            old_value = office.replenishmentoptout
            office.replenishmentoptout = False
            office.save(using="fred")

            # Use OfficeHistoryService for logging
            OfficeHistoryService.log(
                office_id=office_id,
                user_id=user_id or 0,
                triggered_action="dioOptinAction",
                old_data=json.dumps({"replenishmentoptout": old_value}),
                new_data=json.dumps({"replenishmentoptout": False}),
            )

            logger.info(f"Office #{office_id} opted back in to DIO replenishment")

        return {
            "success": True,
            "officeId": office_id,
            "replenishmentOptout": False,
            "message": "Office has been opted back in to DIO replenishment",
        }

    @staticmethod
    def get_dio_opt_out_status(office_id: int) -> Dict[str, Any]:
        office = OfficeService.get_one(office_id)

        return {
            "officeId": office_id,
            "officeName": office.name,
            "replenishmentOptout": office.replenishmentoptout,
            "dio2Enabled": office.dio2,
            "virtualInventoryEnabled": office.virtualinventoryenabled,
            "viStatus": office.vi_status,
        }

    @staticmethod
    def get_rx_count_by_office(
        oid,
        start=None,
        end=None,
        rx_type="newrx",
    ):
        offices = oid if isinstance(oid, list) else [oid]

        # STEP 1: Get Rx IDs for office(s)
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid__in=offices)
            .values_list("id", flat=True)
        )

        # STEP 2: Count RxFill rows linked to those Rx IDs
        qs = Rxfill.objects.using("fred").filter(
            rxid__in=rx_ids,
            type=rx_type,
        )

        if start:
            qs = qs.filter(created__gt=start)

        if end:
            qs = qs.filter(created__lt=end)

        return qs.count()

    @staticmethod
    def get_shipment_count_by_office(
        oid: Union[int, List[int]],
        start: datetime = None,
        end: datetime = None,
    ) -> int:

        offices = oid if isinstance(oid, list) else [oid]

        # Step 1: RX ids for office(s)
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid__in=offices)
            .values_list("id", flat=True)
        )

        # Step 2: Shipment ids from RxFill
        shipment_ids = (
            Rxfill.objects.using("fred")
            .filter(rxid__in=rx_ids, shipmentid__isnull=False)
            .values_list("shipmentid", flat=True)
        )

        # Step 3: Filter Shipments by created date
        shipments = Shipment.objects.using("fred").filter(id__in=shipment_ids)

        if start:
            shipments = shipments.filter(created__gt=start)

        if end:
            shipments = shipments.filter(created__lt=end)

        return shipments.count()


__all__ = [
    "OfficeErrorCodes",
    "OfficeServiceException",
    "OfficeTypeSerializer",
    "OfficeListSerializer",
    "OfficeDetailSerializer",
    "OfficeFastListSerializer",
    "OfficeCreateSerializer",
    "OfficeUpdateSerializer",
    "OfficeCreateResponseSerializer",
    "OfficeFastListResponseSerializer",
    "OfficeService",
]
