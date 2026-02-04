"""
Office Serializers Module

Contains serializers related to office management.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from rest_framework import serializers
from django.db import connections, transaction
from django.db.models import Q

from fred.models.office import Office, Officetype, Officehistory, Officeinfo
from fred.models.models import Users, Dio2OptOut
from fred.models.doctor import Doctor
from fred.serializers import reference as reference_serializer

logger = logging.getLogger(__name__)

__all__ = [
    "OfficeListSerializer",
    "OfficeModelSerializer",
    "OfficeDetailSerializer",
    "OfficeCreateSerializer",
    "OfficeUpdateSerializer",
    "OfficeMergeSerializer",
    "OfficePaginationQuerySerializer",
    "OfficeHistorySerializer",
    "OfficeInfoSerializer",
    "OfficeTypeSerializer",
    "OfficeErrorCodes",
    "OfficeInfoErrorCodes",
]


# =============================================================================
# ERROR CODES
# =============================================================================


class OfficeErrorCodes:
    ERROR_UNABLE_CREATE_OFFICE = 16001
    ERROR_OFFICE_NOT_FOUND = 16002
    ERROR_INCORRECT_OFFICE = 16003
    ERROR_UNABLE_UPDATE_OFFICE = 16004
    ERROR_UNABLE_DELETE_OFFICE = 16005
    ERROR_ALREADY_EXISTS = 10001


class OfficeInfoErrorCodes:
    ERROR_OFFICE_INFO_NOT_FOUND = 18001
    ERROR_UNABLE_CREATE_OFFICE_INFO = 18002
    ERROR_UNABLE_UPDATE_OFFICE_INFO = 18003


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def parse_json_array(value: str) -> List[int]:
    """Parse JSON array string to list of integers."""
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return [int(x) for x in parsed] if isinstance(parsed, list) else []
    except (json.JSONDecodeError, ValueError):
        return []


def log_office_history(
    office_id: int,
    user_id: int,
    triggered_action: str,
    old_data: Optional[str] = None,
    new_data: Optional[str] = None,
) -> Officehistory:
    """Log office history entry."""
    with transaction.atomic(using="fred"):
        history = Officehistory(
            officeid=office_id,
            userid=user_id,
            triggeredaction=triggered_action,
            olddata=old_data,
            newdata=new_data,
            datelogged=datetime.now(),
        )
        history.save(using="fred")
    logger.info(f"Logged office history: office={office_id}, action={triggered_action}")
    return history


def get_office_info(office_id: int) -> Optional[Officeinfo]:
    """Get office info by office ID."""
    try:
        return Officeinfo.objects.using("fred").get(officeid=office_id)
    except Officeinfo.DoesNotExist:
        return None


def update_office_info(office_id: int, data: Dict[str, Any]) -> Officeinfo:
    """Create or update office info."""
    office_info = get_office_info(office_id)
    with transaction.atomic(using="fred"):
        if office_info:
            for field, value in data.items():
                setattr(office_info, field, value)
            office_info.save(using="fred")
        else:
            data["officeid"] = office_id
            office_info = Officeinfo.objects.using("fred").create(**data)
        return office_info


def get_users_with_details(user_ids: List[int]) -> List[Dict[str, Any]]:
    """Get users with doctor details if applicable."""
    users = []
    for uid in user_ids:
        try:
            user = Users.objects.using("fred").get(pk=uid)
            user_data = {
                "id": user.id,
                "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "email": user.email,
                "role": user.role,
                "status": user.status,
                "type": "user",
            }

            if user.role == "doctor" and user.doctorid:
                try:
                    doctor = Doctor.objects.using("fred").get(pk=user.doctorid)
                    user_data.update(
                        {
                            "npi": doctor.npi,
                            "phone": doctor.phone,
                            "type": "doctor",
                            "doctorId": doctor.id,
                            "doctorName": doctor.name,
                        }
                    )
                except Doctor.DoesNotExist:
                    pass

            users.append(user_data)
        except Users.DoesNotExist:
            continue
    return users


# =============================================================================
# SERIALIZERS
# =============================================================================


class OfficeListSerializer(serializers.ModelSerializer):
    """Full office serializer for list responses."""

    class Meta:
        model = Office
        fields = [
            "id",
            "addressid",
            "name",
            "created",
            "dio2enabled",
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
            "acct",
            "route",
            "officeemail",
            "primaryemail",
            "delivermode",
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


class OfficeModelSerializer(serializers.ModelSerializer):
    """
    Serializer for Fred Offices with address.
    """

    address = reference_serializer.AddressModelSerializer(
        source="addressid", read_only=True
    )

    class Meta:
        model = Office
        fields = "__all__"


class Dio2OptOutSerializer(serializers.ModelSerializer):
    """
    Serializer for Dio2OptOut records (NPI-level opt-outs).
    """

    class Meta:
        model = Dio2OptOut
        fields = "__all__"

    def list_paginated(self, **options):
        """Get paginated office list with search and ordering."""
        limit = options.get("limit", 25)
        page = options.get("page", 1)
        order = options.get("order", 0)
        order_dir = options.get("orderDir", "asc")
        search = options.get("search", "")
        office_ids = options.get("office_ids", None)

        offset = (page - 1) * limit
        params = []

        base_sql = """
            FROM office o
            INNER JOIN address a ON a.id = o.addressid
            INNER JOIN officetype ot ON ot.id = o.officetypeid
            LEFT JOIN users u ON u.id = CAST(
                REGEXP_REPLACE(COALESCE(o.sales, '0'), '\\[|\\]', '', 'g') AS INTEGER
            )
            WHERE 1=1
        """

        if search:
            base_sql += """
                AND (CAST(o.id AS TEXT) ILIKE %s OR o.name ILIKE %s
                     OR CONCAT(a.city, ', ', a.state) ILIKE %s
                     OR CONCAT(u.first_name, ' ', u.last_name) ILIKE %s)
            """
            params.extend([f"%{search}%"] * 4)

        if office_ids:
            base_sql += " AND o.id = ANY(%s)"
            params.append(office_ids)

        with connections["fred"].cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) {base_sql}", params)
            records_filtered = cursor.fetchone()[0]

        order_columns = {
            0: "o.id",
            1: "o.name",
            2: "a.city",
            3: "ot.type",
            4: "u.first_name",
        }
        order_field = order_columns.get(order, "o.id")
        order_direction = "DESC" if order_dir.lower() == "desc" else "ASC"

        data_sql = f"""
            SELECT o.id, o.name, CONCAT(a.city, ', ', a.state) AS location,
                   ot.type AS officetype, CONCAT(u.first_name, ' ', u.last_name) AS sales
            {base_sql}
            ORDER BY {order_field} {order_direction}
            LIMIT %s OFFSET %s
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(data_sql, params + [limit, offset])
            cols = [c[0] for c in cursor.description]
            offices = [dict(zip(cols, row)) for row in cursor.fetchall()]

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


class OfficeDetailSerializer(serializers.ModelSerializer):
    """Office serializer with nested address for detail views."""

    address = serializers.SerializerMethodField()

    class Meta:
        model = Office
        fields = "__all__"

    def get_address(self, obj) -> Optional[Dict]:
        if obj.addressid:
            return reference_serializer.AddressModelSerializer.get_address_by_id(
                obj.addressid
            )
        return None


class OfficeCreateSerializer(serializers.Serializer):
    """Validates and creates offices."""

    addressid = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True, max_length=255)

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Office name is required")
        return value.strip()

    def validate_addressid(self, value):
        address = reference_serializer.AddressModelSerializer.get_address_by_id(value)
        if not address:
            raise serializers.ValidationError(f"Address with id {value} not found")
        return value

    def create(self, validated_data):
        # The model field is 'address', not 'addressid' (addressid is a read-only property)
        # Use address_id to set the ForeignKey by ID
        address_id = validated_data.pop("addressid")

        with transaction.atomic(using="fred"):
            office = Office.objects.using("fred").create(
                address_id=address_id,  # Django's automatic _id suffix for ForeignKey
                **validated_data,
            )
            logger.info(f"Office #{office.id} ({office.name}) created")
            return office


class OfficeUpdateSerializer(serializers.Serializer):
    """Validates and updates offices with role-based field permissions."""

    # Declare all updatable fields
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
    # OfficeInfo fields
    fax = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    reminderopt = serializers.BooleanField(required=False, default=False)

    # Role-based field permissions
    ROLE_FIELDS = {
        "admin": [
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
        ],
        "manager": [
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
        ],
        "sales-manager": [
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
            "netsuiteid",
            "logo",
        ],
        "office": ["logo"],
        "doctor": ["logo"],
        "customer-service": ["note"],
        "customer-service-manager": ["note"],
        "pharmacist": ["note"],
    }

    def get_allowed_fields(self, role: str) -> List[str]:
        if role == "sales":
            role = "manager"
        return self.ROLE_FIELDS.get(role, [])

    def update(self, instance, validated_data):
        role = self.context.get("role", "admin")
        allowed_fields = self.get_allowed_fields(role)

        # Handle OfficeInfo fields separately
        office_info_data = {}
        for field in ["fax", "phone", "reminderopt"]:
            if field in validated_data:
                key = "primaryphone" if field == "phone" else field
                office_info_data[key] = validated_data.pop(field)

        if office_info_data:
            update_office_info(instance.id, office_info_data)

        with transaction.atomic(using="fred"):
            for field in allowed_fields:
                if field not in validated_data:
                    continue

                value = validated_data[field]

                # Handle special cases
                if field in ("parentid", "vivendorid") and value == 0:
                    value = None
                elif field == "netsuiteid":
                    if value in (0, "0"):
                        value = None
                    elif value:
                        existing = (
                            Office.objects.using("fred")
                            .filter(netsuiteid=value)
                            .exclude(pk=instance.id)
                            .first()
                        )
                        if existing:
                            raise serializers.ValidationError(
                                f"NetSuite ID {value} already assigned to Office ID {existing.id}"
                            )

                setattr(instance, field, value)

            instance.save(using="fred")
            logger.info(f"Office #{instance.id} updated by role: {role}")
            return instance


class OfficeMergeSerializer(serializers.Serializer):
    """Serializer for office merge operations."""

    sourceOfficeId = serializers.IntegerField(required=True)
    targetOfficeId = serializers.IntegerField(required=True)

    def validate(self, data):
        if data["sourceOfficeId"] == data["targetOfficeId"]:
            raise serializers.ValidationError("Cannot merge office into itself")

        if not Office.objects.using("fred").filter(id=data["sourceOfficeId"]).exists():
            raise serializers.ValidationError(
                f"Source office with id {data['sourceOfficeId']} does not exist"
            )

        if not Office.objects.using("fred").filter(id=data["targetOfficeId"]).exists():
            raise serializers.ValidationError(
                f"Target office with id {data['targetOfficeId']} does not exist"
            )

        return data


class OfficePaginationQuerySerializer(serializers.Serializer):
    """Query parameters for paginated office list."""

    page = serializers.IntegerField(default=1, min_value=1, required=False)
    limit = serializers.IntegerField(
        default=25, min_value=1, max_value=100, required=False
    )
    search = serializers.CharField(
        required=False, allow_blank=True, trim_whitespace=True
    )
    order = serializers.IntegerField(default=0, required=False)
    orderDir = serializers.CharField(default="asc", required=False)

    def validate_page(self, value):
        return max(value, 1) if value else 1

    def validate_limit(self, value):
        return min(max(value, 1), 100) if value else 25

    def validate_orderDir(self, value):
        return value.lower() if value and value.lower() in ["asc", "desc"] else "asc"


class OfficeHistorySerializer(serializers.ModelSerializer):
    """Serializer for office history records."""

    class Meta:
        model = Officehistory
        fields = "__all__"


class OfficeInfoSerializer(serializers.ModelSerializer):
    """Serializer for office info records."""

    class Meta:
        model = Officeinfo
        fields = "__all__"


class OfficeTypeSerializer(serializers.ModelSerializer):
    """Serializer for office types."""

    class Meta:
        model = Officetype
        fields = ["id", "type"]
