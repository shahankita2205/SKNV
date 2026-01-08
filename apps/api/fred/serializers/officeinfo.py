"""
OfficeInfo Serializers and Services
"""

import logging
from typing import Optional, Dict, Any

from django.db import transaction
from rest_framework import serializers

from fred.models.office import (
    Officeinfo,
)

logger = logging.getLogger(__name__)


class OfficeInfoErrorCodes:
    ERROR_OFFICE_INFO_NOT_FOUND = 18001
    ERROR_UNABLE_CREATE_OFFICE_INFO = 18002
    ERROR_UNABLE_UPDATE_OFFICE_INFO = 18003


class OfficeInfoServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class OfficeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officeinfo
        fields = ["id", "officeid", "fax", "primaryphone", "reminderopt"]


class OfficeInfoCreateSerializer(serializers.Serializer):
    officeid = serializers.IntegerField(required=True)
    fax = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primaryphone = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    reminderopt = serializers.BooleanField(required=False, default=False)

    def create(self, validated_data):
        return OfficeInfoService.create(validated_data)


class OfficeInfoUpdateSerializer(serializers.Serializer):
    fax = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    primaryphone = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    reminderopt = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        return OfficeInfoService.update(instance, validated_data)


class OfficeInfoService:

    @staticmethod
    def get_one_by_office_id(office_id: int) -> Optional[Officeinfo]:
        try:
            return Officeinfo.objects.using("fred").get(officeid=office_id)
        except Officeinfo.DoesNotExist:
            return None

    @staticmethod
    def get_one_by_office_id_or_fail(office_id: int) -> Officeinfo:
        try:
            return Officeinfo.objects.using("fred").get(officeid=office_id)
        except Officeinfo.DoesNotExist:
            raise OfficeInfoServiceException(
                f"OfficeInfo for office #{office_id} not found",
                OfficeInfoErrorCodes.ERROR_OFFICE_INFO_NOT_FOUND,
            )

    @staticmethod
    def create(data: Dict[str, Any]) -> Officeinfo:
        try:
            with transaction.atomic(using="fred"):
                office_info = Officeinfo()
                if "officeid" in data:
                    office_info.officeid = data["officeid"]
                if "fax" in data:
                    office_info.fax = data["fax"]
                if "primaryphone" in data:
                    office_info.primaryphone = data["primaryphone"]
                if "reminderopt" in data:
                    office_info.reminderopt = data["reminderopt"]
                office_info.save(using="fred")
                logger.info(f"OfficeInfo #{office_info.id} created")
                return office_info
        except Exception as e:
            logger.error(f"Error creating office info: {e}")
            raise OfficeInfoServiceException(
                "Unable to create office info",
                OfficeInfoErrorCodes.ERROR_UNABLE_CREATE_OFFICE_INFO,
            )

    @staticmethod
    def update(office_info: Officeinfo, data: Dict[str, Any]) -> Officeinfo:
        try:
            with transaction.atomic(using="fred"):
                if "fax" in data:
                    office_info.fax = data["fax"]
                if "primaryphone" in data:
                    office_info.primaryphone = data["primaryphone"]
                if "reminderopt" in data:
                    office_info.reminderopt = data["reminderopt"]
                office_info.save(using="fred")
                logger.info(f"OfficeInfo #{office_info.id} updated")
                return office_info
        except Exception as e:
            logger.error(f"Error updating office info: {e}")
            raise OfficeInfoServiceException(
                "Unable to update office info",
                OfficeInfoErrorCodes.ERROR_UNABLE_UPDATE_OFFICE_INFO,
            )

    @staticmethod
    def create_or_update(office_id: int, data: Dict[str, Any]) -> Officeinfo:
        office_info = OfficeInfoService.get_one_by_office_id(office_id)
        if office_info:
            return OfficeInfoService.update(office_info, data)
        else:
            data["officeid"] = office_id
            return OfficeInfoService.create(data)


__all__ = [
    "OfficeInfoErrorCodes",
    "OfficeInfoServiceException",
    "OfficeInfoSerializer",
    "OfficeInfoCreateSerializer",
    "OfficeInfoUpdateSerializer",
    "OfficeInfoService",
]
