"""
Doctor Serializers

Contains all serializers for Doctor model operations.
Fully migrated from PHP DoctorController and DoctorService.

Serializers:
    - DoctorSerializer: Full model serialization
    - DoctorCreateSerializer: Create with validation + service logic
    - DoctorUpdateSerializer: Update with role-based access
    - DoctorListSerializer: List view (excludes sensitive fields)
    - DoctorFastListSerializer: Minimal for dropdowns
    - DoctorNPISerializer: For PCD workflows
    - DoctorRxStatsSerializer: Prescription statistics
    - DoctorProfileSerializer: Full profile
    - DoctorWithDetailsSerializer: Profile + stats + offices
    - DoctorPaginatedItemSerializer: DataTables format
    - DoctorPaginatedResponseSerializer: DataTables response
"""

import re
import logging
from datetime import datetime

from django.db import transaction, IntegrityError
from django.db.models import Count, Q
from rest_framework import serializers

from fred.models.doctor import Doctor
from fred.models import Rx, Office

logger = logging.getLogger(__name__)


# =============================================================================
# ERROR CODES (matching PHP DoctorService)
# =============================================================================


class DoctorErrorCodes:
    """Error codes matching PHP DoctorService"""

    ERROR_UNABLE_CREATE_DOCTOR = 17001
    ERROR_DOCTOR_NOT_FOUND = 17002
    ERROR_INCORRECT_DOCTOR = 17003
    ERROR_UNABLE_UPDATE_DOCTOR = 17004
    ERROR_UNABLE_DELETE_DOCTOR = 17005
    ERROR_ALREADY_EXISTS = 10001


class DoctorServiceException(Exception):
    """Exception for doctor service errors"""

    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


# =============================================================================
# BASE SERIALIZERS (Read Operations)
# =============================================================================


class DoctorSerializer(serializers.ModelSerializer):
    """
    Full Doctor serializer for detailed views.
    Includes computed properties.
    """

    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    has_valid_npi = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "dea",
            "npi",
            "spi",
            "created",
            "prefix",
            "firstname",
            "middlename",
            "lastname",
            "suffix",
            "pin",
            "pharmetikaid",
            "approval",
            "full_name",
            "display_name",
            "has_valid_npi",
        ]

    def get_full_name(self, obj) -> str:
        parts = [obj.prefix, obj.firstname, obj.middlename, obj.lastname, obj.suffix]
        return " ".join(filter(None, parts)) or obj.name or ""

    def get_display_name(self, obj) -> str:
        full = self.get_full_name(obj)
        return full if full else obj.name or ""

    def get_has_valid_npi(self, obj) -> bool:
        if not obj.npi:
            return False
        return bool(re.match(r"^\d{10}$", str(obj.npi)))


class DoctorListSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor list views.
    Excludes sensitive fields like pin.
    """

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "dea",
            "npi",
            "spi",
            "created",
            "prefix",
            "firstname",
            "middlename",
            "lastname",
            "suffix",
            "pharmetikaid",
            "approval",
        ]


class DoctorFastListSerializer(serializers.Serializer):
    """
    Minimal serializer for dropdowns/fast lists.
    Only includes id and name.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()


class DoctorNPISerializer(serializers.Serializer):
    """
    Serializer for NPI-related operations.
    Used in PCD workflows.
    Works with dict data from DoctorService.get_all_npis()
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    npi = serializers.CharField()
    spi = serializers.CharField(allow_null=True)


class DoctorRxStatsSerializer(serializers.Serializer):
    """Serializer for prescription statistics"""

    total = serializers.IntegerField()
    this_month = serializers.IntegerField()


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Full profile serializer for detailed lists"""

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "dea",
            "npi",
            "spi",
            "prefix",
            "firstname",
            "middlename",
            "lastname",
            "suffix",
            "pharmetikaid",
            "approval",
        ]


class DoctorWithDetailsSerializer(serializers.Serializer):
    """
    Serializer for doctor with rx stats and offices.
    Used in list endpoint.
    """

    profile = DoctorProfileSerializer()
    rxs = DoctorRxStatsSerializer()
    offices = serializers.ListField(child=serializers.IntegerField())


class DoctorPaginatedItemSerializer(serializers.Serializer):
    """
    Serializer for paginated list items.
    Matches DataTables format.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    npi = serializers.CharField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    email = serializers.CharField(allow_null=True)


class DoctorPaginatedResponseSerializer(serializers.Serializer):
    """
    Serializer for paginated response.
    Matches PHP DataTables format.
    """

    doctors = DoctorPaginatedItemSerializer(many=True)
    firstPage = serializers.IntegerField()
    currentPage = serializers.IntegerField()
    lastPage = serializers.IntegerField()
    recordsFiltered = serializers.IntegerField()
    nextPage = serializers.IntegerField(allow_null=True)
    previousPage = serializers.IntegerField(allow_null=True)
    recordsTotal = serializers.IntegerField()
    limit = serializers.IntegerField()


class DoctorFastListResponseSerializer(serializers.Serializer):
    """Wrapper for fast list response"""

    results = DoctorFastListSerializer(many=True)


# =============================================================================
# CREATE SERIALIZER (with service logic)
# =============================================================================


class DoctorCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new doctor.
    Includes validation and create logic.

    PHP Equivalent: DoctorService::create()
    """

    name = serializers.CharField(required=True, max_length=255)
    npi = serializers.CharField(required=True, max_length=10)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    email = serializers.EmailField(required=False, allow_blank=True)
    dea = serializers.CharField(required=False, allow_blank=True, max_length=50)
    spi = serializers.CharField(required=False, allow_blank=True, max_length=50)
    pin = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=50
    )
    prefix = serializers.CharField(required=False, allow_blank=True, max_length=20)
    firstname = serializers.CharField(required=False, allow_blank=True, max_length=100)
    middlename = serializers.CharField(required=False, allow_blank=True, max_length=100)
    lastname = serializers.CharField(required=False, allow_blank=True, max_length=100)
    suffix = serializers.CharField(required=False, allow_blank=True, max_length=20)

    def validate_npi(self, value):
        """Validate NPI is exactly 10 digits"""
        if value and not re.match(r"^\d{10}$", value):
            raise serializers.ValidationError("NPI must be exactly 10 digits")
        return value

    def validate_email(self, value):
        """Normalize email to lowercase"""
        if value:
            return value.lower().strip()
        return value

    def validate_name(self, value):
        """Ensure name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required")
        return value.strip()

    def create(self, validated_data):
        """
        Create a new doctor.

        PHP Equivalent: DoctorService::create()

        Returns:
            Doctor: Created doctor instance

        Raises:
            DoctorServiceException: If creation fails
        """
        try:
            with transaction.atomic(using="fred"):
                # Handle empty pin
                if validated_data.get("pin") == "":
                    validated_data["pin"] = None

                doctor = Doctor.objects.using("fred").create(**validated_data)
                logger.info(f"Doctor #{doctor.id} has been created")
                return doctor

        except IntegrityError as e:
            error_str = str(e)
            if "23505" in error_str or "duplicate" in error_str.lower():
                logger.error(f"Doctor already exists: {e}")
                raise DoctorServiceException(
                    "Doctor already exists", DoctorErrorCodes.ERROR_ALREADY_EXISTS
                )
            logger.error(f"Error creating doctor: {e}")
            raise DoctorServiceException(
                "Unable to create doctor", DoctorErrorCodes.ERROR_UNABLE_CREATE_DOCTOR
            )
        except Exception as e:
            logger.error(f"Error creating doctor: {e}")
            raise DoctorServiceException(
                "Unable to create doctor", DoctorErrorCodes.ERROR_UNABLE_CREATE_DOCTOR
            )


# =============================================================================
# UPDATE SERIALIZER (with service logic)
# =============================================================================


class DoctorUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating a doctor.
    Includes role-based field access.

    PHP Equivalent: DoctorService::update()

    Role-based access:
        - admin: Can update all fields
        - others: Can only update pin
    """

    name = serializers.CharField(required=False, max_length=255)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=50)
    email = serializers.EmailField(required=False, allow_blank=True)
    dea = serializers.CharField(required=False, allow_blank=True, max_length=50)
    npi = serializers.CharField(required=False, max_length=10)
    spi = serializers.CharField(required=False, allow_blank=True, max_length=50)
    pin = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=50
    )

    def validate_npi(self, value):
        """Validate NPI is exactly 10 digits"""
        if value and not re.match(r"^\d{10}$", value):
            raise serializers.ValidationError("NPI must be exactly 10 digits")
        return value

    def validate_email(self, value):
        """Normalize email to lowercase"""
        if value:
            return value.lower().strip()
        return value

    def update(self, instance, validated_data):
        """
        Update a doctor with role-based field access.

        PHP Equivalent: DoctorService::update()

        Args:
            instance: Doctor instance to update
            validated_data: Validated data from request

        Returns:
            Doctor: Updated doctor instance

        Raises:
            DoctorServiceException: If update fails
        """
        role = self.context.get("role", "admin")

        # Define which fields each role can update
        admin_fields = ["name", "email", "phone", "dea", "npi", "spi", "pin"]
        restricted_fields = ["pin"]  # For non-admin roles

        allowed_fields = admin_fields if role == "admin" else restricted_fields

        try:
            with transaction.atomic(using="fred"):
                for field in allowed_fields:
                    if field in validated_data:
                        value = validated_data[field]
                        # Handle empty pin as NULL
                        if field == "pin" and value == "":
                            value = None
                        setattr(instance, field, value)

                instance.save(using="fred")
                logger.info(f"Doctor #{instance.id} has been updated by role: {role}")
                return instance

        except Exception as e:
            logger.error(f"Error updating doctor #{instance.id}: {e}")
            raise DoctorServiceException(
                "Unable to update doctor", DoctorErrorCodes.ERROR_UNABLE_UPDATE_DOCTOR
            )


# =============================================================================
# DOCTOR SERVICE (Static methods for complex operations)
# =============================================================================


class DoctorService:
    """
    Service class for complex doctor operations.

    Contains static methods that don't fit into serializers,
    such as queries, lookups, and delete operations.

    PHP Equivalent: app/Services/DoctorService.php
    """

    @staticmethod
    def get_one(doctor_id: int) -> Doctor:
        """
        Get a single doctor by ID.

        PHP Equivalent: DoctorService::getOne()

        Args:
            doctor_id: Doctor primary key

        Returns:
            Doctor: Doctor instance

        Raises:
            DoctorServiceException: If doctor not found
        """
        try:
            return Doctor.objects.using("fred").get(pk=doctor_id)
        except Doctor.DoesNotExist:
            raise DoctorServiceException(
                "Doctor not found", DoctorErrorCodes.ERROR_DOCTOR_NOT_FOUND
            )

    @staticmethod
    def delete(doctor_id: int) -> bool:
        """
        Delete a doctor.

        PHP Equivalent: DoctorService::delete()

        Args:
            doctor_id: Doctor primary key

        Returns:
            bool: True if deleted

        Raises:
            DoctorServiceException: If delete fails
        """
        try:
            with transaction.atomic(using="fred"):
                doctor = Doctor.objects.using("fred").get(pk=doctor_id)
                doctor.delete()
                logger.info(f"Doctor #{doctor_id} has been deleted")
                return True
        except Doctor.DoesNotExist:
            raise DoctorServiceException(
                "Doctor not found", DoctorErrorCodes.ERROR_DOCTOR_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting doctor #{doctor_id}: {e}")
            raise DoctorServiceException(
                "Unable to delete doctor", DoctorErrorCodes.ERROR_UNABLE_DELETE_DOCTOR
            )

    @staticmethod
    def get_all():
        """
        Get all doctors.

        PHP Equivalent: DoctorService::getAll()

        Returns:
            QuerySet: All doctors
        """
        return Doctor.objects.using("fred").all()

    @staticmethod
    def get_one_by_email(email: str):
        """
        Get doctor by email (case-insensitive).

        PHP Equivalent: DoctorService::getOneByEmail()

        Args:
            email: Email address to search

        Returns:
            Doctor or None
        """
        try:
            return Doctor.objects.using("fred").get(email__iexact=email)
        except Doctor.DoesNotExist:
            return None

    @staticmethod
    def match_with_npi(npi: str):
        """
        Check if a doctor with given NPI exists.

        PHP Equivalent: DoctorService::matchWithNPI()

        Args:
            npi: NPI to check

        Returns:
            int or False: Doctor ID if found, False otherwise
        """
        doctor = Doctor.objects.using("fred").filter(npi=npi).first()
        return doctor.id if doctor else False

    @staticmethod
    def get_doctors_by_npi(npi: str):
        """
        Get all doctors with given NPI.

        PHP Equivalent: DoctorService::getDoctorsByNpi()

        Args:
            npi: NPI to search

        Returns:
            QuerySet: Doctors with matching NPI
        """
        return Doctor.objects.using("fred").filter(npi=npi)

    @staticmethod
    def get_other_doctors_by_npi_and_id(npi: str, doctor_id: int):
        """
        Get doctors with same NPI but different ID.
        Used for uniqueness validation.

        PHP Equivalent: DoctorService::getOtherDoctorsByNpiAndId()

        Args:
            npi: NPI to search
            doctor_id: Doctor ID to exclude

        Returns:
            QuerySet: Other doctors with same NPI
        """
        return Doctor.objects.using("fred").filter(npi=npi).exclude(pk=doctor_id)

    @staticmethod
    def get_all_npis() -> list:
        """
        Get all valid 10-digit NPIs.

        PHP Equivalent: DoctorService::getAllNPIs()

        Returns:
            list: List of dicts with name, npi, spi
        """
        doctors = (
            Doctor.objects.using("fred")
            .filter(npi__isnull=False)
            .exclude(npi="")
            .values("id", "name", "npi", "spi")
        )

        # Filter to only 10-digit NPIs
        result = []
        for doc in doctors:
            if doc["npi"] and re.match(r"^\d{10}$", str(doc["npi"])):
                result.append(
                    {
                        "id": doc["id"],
                        "name": doc["name"],
                        "npi": doc["npi"],
                        "spi": doc["spi"],
                    }
                )

        return result

    @staticmethod
    def get_fast_list() -> list:
        """
        Get minimal doctor list for dropdowns.

        PHP Equivalent: DoctorService::fastList()

        Returns:
            list: List of dicts with id and name
        """
        return list(Doctor.objects.using("fred").values("id", "name").order_by("name"))

    @staticmethod
    def get_list_with_details() -> list:
        """
        Get doctors with prescription counts and offices.

        OPTIMIZED version using efficient queries.
        """
        from django.db.models import Count, Q, OuterRef, Subquery
        from django.db.models.functions import Coalesce
        from datetime import datetime

        current_month = datetime.now().month
        current_year = datetime.now().year

        # Step 1: Get all rx counts grouped by doctor (single query)
        rx_stats = (
            Rx.objects.using("fred")
            .filter(doctorid__isnull=False)
            .values("doctorid")
            .annotate(
                total=Count("id"),
                this_month=Count(
                    "id",
                    filter=Q(created__month=current_month, created__year=current_year),
                ),
            )
        )

        # Convert to lookup dict
        rx_lookup = {
            item["doctorid"]: {"total": item["total"], "this_month": item["this_month"]}
            for item in rx_stats
        }

        # Step 2: Get all office associations (single query)
        office_data = (
            Rx.objects.using("fred")
            .filter(doctorid__isnull=False, officeid__isnull=False)
            .values_list("doctorid", "officeid")
            .distinct()
        )

        # Convert to lookup dict
        office_lookup = {}
        for doc_id, office_id in office_data:
            if doc_id not in office_lookup:
                office_lookup[doc_id] = []
            if office_id not in office_lookup[doc_id]:
                office_lookup[doc_id].append(office_id)

        # Step 3: Get all doctors (single query)
        doctors = Doctor.objects.using("fred").all()

        # Step 4: Build result
        result = []
        for doctor in doctors:
            rx_data = rx_lookup.get(doctor.id, {"total": 0, "this_month": 0})
            result.append(
                {
                    "profile": {
                        "id": doctor.id,
                        "name": doctor.name,
                        "phone": doctor.phone,
                        "email": doctor.email,
                        "dea": doctor.dea,
                        "npi": doctor.npi,
                        "spi": doctor.spi,
                        "prefix": doctor.prefix,
                        "firstname": doctor.firstname,
                        "middlename": doctor.middlename,
                        "lastname": doctor.lastname,
                        "suffix": doctor.suffix,
                        "pharmetikaid": doctor.pharmetikaid,
                        "approval": doctor.approval,
                    },
                    "rxs": rx_data,
                    "offices": office_lookup.get(doctor.id, []),
                }
            )

        return result

    @staticmethod
    def get_paginated(
        page: int = 1,
        limit: int = 10,
        search: str = None,
        order_column: int = 0,
        order_dir: str = "asc",
    ) -> dict:
        """
        Get paginated doctor list for DataTables.

        PHP Equivalent: DoctorService::listPaginated()

        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term
            order_column: Column index (0=id, 1=name)
            order_dir: Sort direction ('asc' or 'desc')

        Returns:
            dict: Paginated response matching DataTables format
        """
        queryset = Doctor.objects.using("fred").all()
        total_records = queryset.count()

        # Apply search filter
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) | Q(name__icontains=search)
            )

        filtered_records = queryset.count()

        # Apply ordering
        order_columns_map = {0: "id", 1: "name"}
        order_field = order_columns_map.get(order_column, "id")
        if order_dir == "desc":
            order_field = f"-{order_field}"
        queryset = queryset.order_by(order_field)

        # Apply pagination
        offset = (page - 1) * limit
        queryset = queryset[offset : offset + limit]

        # Calculate pagination info
        total_pages = (filtered_records + limit - 1) // limit if limit > 0 else 1

        doctors = []
        for doc in queryset:
            doctors.append(
                {
                    "id": doc.id,
                    "name": doc.name,
                    "npi": doc.npi,
                    "phone": doc.phone,
                    "email": doc.email,
                }
            )

        return {
            "doctors": doctors,
            "firstPage": 1,
            "currentPage": page,
            "lastPage": total_pages,
            "recordsFiltered": filtered_records,
            "nextPage": page + 1 if page < total_pages else None,
            "previousPage": page - 1 if page > 1 else None,
            "recordsTotal": total_records,
            "limit": limit,
        }


# =============================================================================
# RESPONSE SERIALIZERS
# =============================================================================


class DoctorCreateResponseSerializer(serializers.Serializer):
    """Response serializer for create endpoint"""

    id = serializers.IntegerField()


class DoctorUpdateResponseSerializer(serializers.Serializer):
    """Response serializer for update endpoint"""

    error = serializers.BooleanField()


class DoctorDeleteResponseSerializer(serializers.Serializer):
    """Response serializer for delete endpoint"""

    success = serializers.BooleanField()
