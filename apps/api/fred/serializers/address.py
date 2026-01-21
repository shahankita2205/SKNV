"""
Address Serializers and Services
"""

import logging
from typing import Optional, Dict, Any

from django.db import transaction
from rest_framework import serializers

from fred.models.models import Address2 as Address

logger = logging.getLogger(__name__)


class AddressErrorCodes:
    ERROR_ADDRESS_NOT_FOUND = 17001
    ERROR_UNABLE_CREATE_ADDRESS = 17002
    ERROR_UNABLE_UPDATE_ADDRESS = 17003


class AddressServiceException(Exception):
    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class AddressCreateSerializer(serializers.Serializer):
    address1 = serializers.CharField(required=True, max_length=255)
    address2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=True, max_length=100)
    state = serializers.CharField(required=True, max_length=50)
    zip = serializers.CharField(required=True, max_length=10)

    def create(self, validated_data):
        return AddressService.create(validated_data)


class AddressUpdateSerializer(serializers.Serializer):
    address1 = serializers.CharField(required=False, max_length=255)
    address2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, max_length=100)
    state = serializers.CharField(required=False, max_length=50)
    zip = serializers.CharField(required=False, max_length=10)

    def update(self, instance, validated_data):
        return AddressService.update(instance, validated_data)


class AddressService:

    @staticmethod
    def get_one(address_id: int) -> Optional[Address]:
        try:
            address = Address.objects.using("fred").get(pk=address_id)
            if address.zip:
                address.zip = address.zip[:5]
            return address
        except Address.DoesNotExist:
            return None

    @staticmethod
    def get_one_or_fail(address_id: int) -> Address:
        try:
            address = Address.objects.using("fred").get(pk=address_id)
            if address.zip:
                address.zip = address.zip[:5]
            return address
        except Address.DoesNotExist:
            raise AddressServiceException(
                f"Address #{address_id} not found",
                AddressErrorCodes.ERROR_ADDRESS_NOT_FOUND,
            )

    @staticmethod
    def create(data: Dict[str, Any]) -> Address:
        try:
            with transaction.atomic(using="fred"):
                address = Address.objects.using("fred").create(**data)
                logger.info(f"Address #{address.id} created")
                return address
        except Exception as e:
            logger.error(f"Error creating address: {e}")
            raise AddressServiceException(
                "Unable to create address",
                AddressErrorCodes.ERROR_UNABLE_CREATE_ADDRESS,
            )

    @staticmethod
    def update(address: Address, data: Dict[str, Any]) -> Address:
        try:
            with transaction.atomic(using="fred"):
                for key, value in data.items():
                    if hasattr(address, key):
                        setattr(address, key, value)
                address.save(using="fred")
                logger.info(f"Address #{address.id} updated")
                return address
        except Exception as e:
            logger.error(f"Error updating address #{address.id}: {e}")
            raise AddressServiceException(
                "Unable to update address",
                AddressErrorCodes.ERROR_UNABLE_UPDATE_ADDRESS,
            )


__all__ = [
    "AddressErrorCodes",
    "AddressServiceException",
    "AddressSerializer",
    "AddressCreateSerializer",
    "AddressUpdateSerializer",
    "AddressService",
]
