from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import now
from datetime import timedelta

logger = get_task_logger(__name__)


@shared_task
def run():
    from fred.models import Rx

    logger.info("Looking for End-Of-Life prescriptions")

    rxs = Rx.objects.all()[:5]
    expiry_date = now() - timedelta(days=364)
    expired = Rx.objects.filter(effective__lt=expiry_date, status="ok")
    result_str = "\n".join([f"ID: {rx.id}, Raw ID: {rx.rxrawid}" for rx in expired])
    # result_str = "\n".join([str(rx) for rx in rxs])
    logger.info(result_str)
