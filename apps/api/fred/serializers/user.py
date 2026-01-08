"""
User Serializers and Services
"""

import logging
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any

from django.db import transaction
from rest_framework import serializers

from fred.models.models import Users
from fred.models.doctor import Doctor

logger = logging.getLogger(__name__)


class UserErrorCodes:
    ERROR_USER_NOT_FOUND = 22001
    ERROR_UNABLE_CREATE_USER = 22002
    ERROR_UNABLE_UPDATE_USER = 22003
    ERROR_ALREADY_EXISTS = 22004
    ERROR_INVALID_ROLE = 22005


class UserServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


VALID_ROLES = [
    "admin",
    "manager",
    "sales",
    "sales-manager",
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
        ]
        extra_kwargs = {"pass_field": {"write_only": True}}


class UserListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ["id", "email", "name", "role", "status"]

    def get_name(self, obj):
        return f"{obj.first_name or ''} {obj.last_name or ''}".strip()


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    role = serializers.ChoiceField(choices=[(r, r) for r in VALID_ROLES], required=True)
    password = serializers.CharField(required=False, write_only=True)
    doctorid = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.CharField(required=False, default="active")

    def create(self, validated_data):
        return UserService.create_user(validated_data)


class UserService:

    @staticmethod
    def get_user(user_id: int) -> Users:
        try:
            return Users.objects.using("fred").get(pk=user_id)
        except Users.DoesNotExist:
            raise UserServiceException(
                f"User #{user_id} not found", UserErrorCodes.ERROR_USER_NOT_FOUND
            )

    @staticmethod
    def get_user_no_exception(user_id: int) -> Optional[Users]:
        try:
            return Users.objects.using("fred").get(pk=user_id)
        except Users.DoesNotExist:
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Users]:
        try:
            return Users.objects.using("fred").get(email__iexact=email.lower())
        except Users.DoesNotExist:
            return None

    @staticmethod
    def get_all_by_role(role: str):
        return Users.objects.using("fred").filter(role=role).order_by("first_name")

    @staticmethod
    def get_all_sales_users():
        return (
            Users.objects.using("fred")
            .filter(role__in=["sales", "sales-manager"])
            .order_by("first_name")
        )

    @staticmethod
    def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        role = user_data.get("role")

        if role not in VALID_ROLES:
            raise UserServiceException(
                f"Invalid user role: {role}", UserErrorCodes.ERROR_INVALID_ROLE
            )

        email = user_data.get("email", "").lower().strip()

        existing = UserService.get_user_by_email(email)
        if existing:
            raise UserServiceException(
                f"User with email {email} already exists",
                UserErrorCodes.ERROR_ALREADY_EXISTS,
            )

        password = user_data.get("password") or secrets.token_urlsafe(12)

        try:
            with transaction.atomic(using="fred"):
                user = Users()
                user.email = email
                user.first_name = user_data.get("first_name", "")
                user.last_name = user_data.get("last_name", "")
                user.role = role
                user.status = user_data.get("status", "active")
                user.created = datetime.now()
                user.pass_field = password

                if role == "doctor" and user_data.get("doctorid"):
                    user.doctorid = user_data["doctorid"]

                user.save(using="fred")
                logger.info(f"User #{user.id} ({email}) created with role {role}")

                return {
                    "user_id": user.id,
                    "email": user.email,
                    "temp_password": password,
                }
        except Exception as e:
            if hasattr(e, "args") and len(e.args) > 0:
                if "23505" in str(e.args[0]):
                    raise UserServiceException(
                        "User already exists", UserErrorCodes.ERROR_ALREADY_EXISTS
                    )
            logger.error(f"Error creating user: {e}")
            raise UserServiceException(
                "Unable to create user", UserErrorCodes.ERROR_UNABLE_CREATE_USER
            )

    @staticmethod
    def get_users_with_details(user_ids: List[int]) -> List[Dict[str, Any]]:
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
                        user_data["npi"] = doctor.npi
                        user_data["phone"] = doctor.phone
                        user_data["type"] = "doctor"
                        user_data["doctorId"] = doctor.id
                        user_data["doctorName"] = doctor.name
                    except Doctor.DoesNotExist:
                        pass

                users.append(user_data)
            except Users.DoesNotExist:
                continue
        return users

    @staticmethod
    def get_office_assigned_sales(office_sales_ids: List[int]) -> Dict[str, List]:
        all_sales = UserService.get_all_sales_users()

        assigned = []
        available = []

        for user in all_sales:
            user_data = {
                "id": user.id,
                "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                "email": user.email,
                "role": user.role,
            }

            if user.id in office_sales_ids:
                assigned.append(user_data)
            else:
                available.append(user_data)

        return {"assigned": assigned, "available": available}


__all__ = [
    "UserErrorCodes",
    "UserServiceException",
    "VALID_ROLES",
    "UserSerializer",
    "UserListSerializer",
    "UserCreateSerializer",
    "UserService",
]
