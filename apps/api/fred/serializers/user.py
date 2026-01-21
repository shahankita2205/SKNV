"""
User Serializers
"""

import hashlib
import logging
import secrets
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import serializers

from fred.models.models import Users

logger = logging.getLogger(__name__)


def _format_utc_datetime(value):
    if not value:
        return None
    if timezone.is_naive(value):
        value = timezone.make_aware(value, dt_timezone.utc)
    value = timezone.localtime(value, dt_timezone.utc)
    formatted = value.isoformat(sep=" ", timespec="microseconds")
    if formatted.endswith("+00:00"):
        return formatted[:-3]
    return formatted


def _hash_password(value):
    salt = getattr(settings, "FRED_PASSWORD_SALT", "")
    return hashlib.sha256(f"{value}{salt}".encode("utf-8")).hexdigest()


class UserErrorCodes:
    ERROR_USER_NOT_FOUND = 22001
    ERROR_UNABLE_CREATE_USER = 22002
    ERROR_UNABLE_UPDATE_USER = 22003
    ERROR_ALREADY_EXISTS = 22004
    ERROR_INVALID_ROLE = 22005
    ERROR_UNABLE_DELETE_USER = 22006


class UserServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


VALID_ROLES = [
    "admin",
    "manager",
    "finance",
    "finance-assistant",
    "tech-support",
    "sales",
    "sales-manager",
    "patient",
    "planner",
    "office",
    "doctor",
    "customer-service",
    "customer-service-manager",
    "pharmacist",
    "pharmacy-manager",
    "warehouse",
    "warehouse-manager",
]


class UserSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    modified = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "status",
            "doctorid",
            "created",
            "modified",
            "patientid",
            "salesid",
            "managerid",
            "pharmacylist",
            "cslist",
        ]
        extra_kwargs = {"pass_field": {"write_only": True}}

    def get_created(self, obj):
        return _format_utc_datetime(getattr(obj, "created", None))

    def get_modified(self, obj):
        return _format_utc_datetime(getattr(obj, "modified", None))


class UserListSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "created",
            "role",
            "status",
            "patientid",
            "salesid",
            "managerid",
            "doctorid",
            "pharmacylist",
            "cslist",
        ]

    def get_created(self, obj):
        return _format_utc_datetime(obj.created)


class UserAddSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    role = serializers.CharField(required=True)
    status = serializers.CharField(required=False, allow_blank=True, default="active")
    doctorid = serializers.IntegerField(required=False, allow_null=True)

    def get_fields(self):
        fields = super().get_fields()
        fields["pass"] = serializers.CharField(write_only=True, required=True)
        return fields

    def validate_email(self, value):
        email = value.strip().lower()
        if Users.objects.using("fred").filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "User already exists", code="already_exists"
            )
        return email

    def validate_role(self, value):
        if value not in VALID_ROLES:
            raise serializers.ValidationError("Invalid user role", code="invalid_role")
        return value

    def create(self, validated_data):
        password = validated_data.pop("pass")
        role = validated_data.get("role")
        doctorid = validated_data.get("doctorid") if role == "doctor" else None

        try:
            user = Users()
            user.email = validated_data.get("email")
            user.pass_field = _hash_password(password)
            user.first_name = validated_data.get("first_name", "")
            user.last_name = validated_data.get("last_name", "")
            user.role = role
            user.status = validated_data.get("status", "active")
            user.created = timezone.now()
            user.doctorid = doctorid
            user.save(using="fred")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise serializers.ValidationError(
                "Unable to create user", code="unable_create"
            )


class UserUpdateSerializer(serializers.Serializer):
    status = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(required=False, allow_blank=True)
    pharmacylist = serializers.BooleanField(required=False, allow_null=True)
    cslist = serializers.BooleanField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, write_only=True
    )

    def validate_email(self, value):
        if value in (None, ""):
            return value
        email = value.strip().lower()
        existing = (
            Users.objects.using("fred")
            .filter(email__iexact=email)
            .exclude(pk=getattr(self.instance, "pk", None))
            .exists()
        )
        if existing:
            raise serializers.ValidationError("User already exists", code="already_exists")
        return email

    def update(self, instance, validated_data):
        for field in ("status", "role", "pharmacylist", "cslist"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        if "email" in validated_data:
            email = (validated_data.get("email") or "").strip().lower()
            if email:
                instance.email = email
        if "first_name" in validated_data:
            first_name = (validated_data.get("first_name") or "").strip()
            if first_name:
                instance.first_name = first_name
        if "last_name" in validated_data:
            last_name = (validated_data.get("last_name") or "").strip()
            if last_name:
                instance.last_name = last_name
        if "password" in validated_data:
            password = (validated_data.get("password") or "").strip()
            if password:
                instance.pass_field = _hash_password(password)
        instance.save(using="fred")
        return instance


class SalesManagerAssignSerializer(serializers.Serializer):
    sales = serializers.IntegerField(required=True)
    manager = serializers.IntegerField(required=True, allow_null=True)

    def validate_manager(self, value):
        if value == 0:
            return None
        return value


class SalesPerformanceQuerySerializer(serializers.Serializer):
    start = serializers.CharField(required=False, allow_blank=True)
    end = serializers.CharField(required=False, allow_blank=True)

    def _parse_datetime(self, value, field_name):
        if not value:
            return None

        parsed = parse_datetime(value)
        if parsed is None:
            parsed_date = parse_date(value)
            if parsed_date:
                parsed = datetime.combine(parsed_date, datetime.min.time())

        if parsed is None:
            raise serializers.ValidationError(f"Invalid {field_name} datetime")

        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed, dt_timezone.utc)
        return parsed

    def validate_start(self, value):
        return self._parse_datetime(value, "start")

    def validate_end(self, value):
        return self._parse_datetime(value, "end")


__all__ = [
    "UserErrorCodes",
    "UserServiceException",
    "VALID_ROLES",
    "UserSerializer",
    "UserListSerializer",
    "UserAddSerializer",
    "UserUpdateSerializer",
    "SalesManagerAssignSerializer",
    "SalesPerformanceQuerySerializer",
    "_hash_password",
]
