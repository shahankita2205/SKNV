"""
Utilities for writing logs to the fred.logs table.
"""

import logging

from django.utils import timezone

from fred.models import Logs

logger = logging.getLogger(__name__)


def create_log(user_id, record_id, record_type, log_type, message, rx_id=None):
    try:
        Logs.objects.using("fred").create(
            userid=str(user_id) if user_id is not None else None,
            recordid=str(record_id) if record_id is not None else None,
            recordtype=record_type,
            msg=message,
            type=log_type,
            created=timezone.now(),
            rxid=rx_id,
        )
    except Exception as e:
        logger.error(f"Error saving log: {e}")
