"""
OfficeHistory Serializers and Services
"""

import logging
from datetime import datetime
from typing import Optional

from django.db import transaction
from rest_framework import serializers

from fred.models.office import (
    Officehistory,
)

logger = logging.getLogger(__name__)


class OfficeHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Officehistory
        fields = "__all__"


class OfficeHistoryService:

    @staticmethod
    def log(
        office_id: int,
        user_id: int,
        triggered_action: str,
        old_data: Optional[str] = None,
        new_data: Optional[str] = None,
    ) -> Officehistory:
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
            logger.info(
                f"Logged office history: office={office_id}, action={triggered_action}"
            )
            return history

    @staticmethod
    def get_by_office(office_id: int, limit: int = 100):
        return (
            Officehistory.objects.using("fred")
            .filter(officeid=office_id)
            .order_by("-datelogged")[:limit]
        )

    @staticmethod
    def get_by_user(user_id: int, limit: int = 100):
        return (
            Officehistory.objects.using("fred")
            .filter(userid=user_id)
            .order_by("-datelogged")[:limit]
        )


__all__ = [
    "OfficeHistorySerializer",
    "OfficeHistoryService",
]
