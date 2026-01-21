import time

from celery import shared_task
from celery.utils.log import get_task_logger
from prometheus_client import Gauge

from .prometheus_remote_write import push_sample_to_amp


logger = get_task_logger(__name__)

celery_heartbeat_gauge = Gauge(
    "celery_heartbeat",
    "Timestamp of the most recent Celery heartbeat.",
    ["env"],
)


@shared_task
def create_task(task_type):
    time.sleep(int(task_type) * 10)
    return True


@shared_task
def betterstack_heartbeat():
    from django.conf import settings
    import requests

    heartbeat_url = settings.CELERY_BETTERSTACK_HEARTBEAT_URL
    if not heartbeat_url:
        logger.warning("CELERY_BETTERSTACK_HEARTBEAT_URL is not configured")
        return

    try:
        response = requests.get(heartbeat_url)
        response.raise_for_status()
        logger.info(f"Betterstack heartbeat request successful: {response.status_code}")
    except requests.exceptions.RequestException as exc:
        logger.error(f"Betterstack heartbeat request failed: {exc}")


@shared_task
def prometheus_heartbeat():
    from django.conf import settings

    env_value = getattr(settings, "ENVIRONMENT", "unknown")
    metric_value = time.time()
    celery_heartbeat_gauge.labels(env=env_value).set(metric_value)

    remote_write_url = getattr(settings, "PROMETHEUS_REMOTE_WRITE_URL", "")
    remote_write_region = getattr(settings, "PROMETHEUS_REMOTE_WRITE_REGION", None)
    remote_write_timeout = getattr(settings, "PROMETHEUS_REMOTE_WRITE_TIMEOUT", 5)

    success = push_sample_to_amp(
        metric_name="celery_heartbeat",
        value=metric_value,
        labels={"env": env_value},
        remote_write_url=remote_write_url,
        region=remote_write_region,
        timeout_seconds=remote_write_timeout,
    )

    if success:
        logger.info("Prometheus heartbeat emitted", extra={"env": env_value})
    else:
        logger.warning(
            "Prometheus heartbeat failed to push to AMP",
            extra={
                "env": env_value,
                "remote_write_url_configured": bool(remote_write_url),
            },
        )


@shared_task
def refresh_secrets():
    import os

    if os.path.exists("/var/app/current/refresh_secrets.sh"):
        os.system("/var/app/current/refresh_secrets.sh")
        logger.info("Successfully refreshed secrets")
        return True

    logger.warning("refresh_secrets.sh script not found")
    return False
