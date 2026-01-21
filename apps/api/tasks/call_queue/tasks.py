# tasks.py
import logging
import time
from django.db import connections, transaction
from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import Retry
from django.utils import timezone
from twilio.rest import Client
from rest_framework.test import APIClient
from django.urls import reverse
import secrets
import json

from prometheus_client import Counter, Gauge, Histogram
from ..prometheus_remote_write import push_sample_to_amp

from fred.models import (
    PatientOutreach,
    PatientCallQueue,
    Rxfill,
    Rx,
    Patient2,
    Medication,
    Fee,
    Office,
    Token,
    Textsent,
)

from fred.serializers import UpdatePatientCallQueueSerializer

logger = get_task_logger(__name__)

# Prometheus Metrics Definitions
call_queue_processed_counter = Counter(
    "call_queue_records_processed_total",
    "Total number of call queue records processed",
    ["task_name", "status", "env"],
)

call_queue_duration_histogram = Histogram(
    "call_queue_task_duration_seconds",
    "Duration of call queue tasks in seconds",
    ["task_name", "env"],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600],
)

call_queue_errors_counter = Counter(
    "call_queue_task_errors_total",
    "Total number of call queue task errors",
    ["task_name", "error_type", "env"],
)

call_queue_records_gauge = Gauge(
    "call_queue_records_current",
    "Current count of call queue records by status",
    ["status", "env"],
)

outreach_processed_counter = Counter(
    "patient_outreach_processed_total",
    "Total number of patient outreach records processed",
    ["recipe", "status", "env"],
)


def push_metrics_to_amp(metric_name, value, labels):
    """Helper function to push metrics to Amazon Managed Prometheus"""
    remote_write_url = getattr(settings, "PROMETHEUS_REMOTE_WRITE_URL", "")
    remote_write_region = getattr(settings, "PROMETHEUS_REMOTE_WRITE_REGION", None)
    remote_write_timeout = getattr(settings, "PROMETHEUS_REMOTE_WRITE_TIMEOUT", 5)

    if not remote_write_url:
        logger.debug("Prometheus remote write URL not configured, skipping metric push")
        return False

    success = push_sample_to_amp(
        metric_name=metric_name,
        value=value,
        labels=labels,
        remote_write_url=remote_write_url,
        region=remote_write_region,
        timeout_seconds=remote_write_timeout,
    )

    if not success:
        logger.warning(
            f"Failed to push metric {metric_name} to AMP",
            extra={"labels": labels, "value": value},
        )

    return success


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def populate_patient_call_queue(self):
    """
    Celery task to populate the patient_call_queue table with eligible patients
    for outreach calls based on payment hold status and other criteria.

    This task should be run daily to keep the call queue updated.
    """
    env_value = getattr(settings, "ENVIRONMENT", "unknown")
    start_time = time.time()

    sql_query = """
    INSERT INTO patient_call_queue (
        patient_id,
        cybersource_customerid,
        patient_firstname,
        patient_lastname,
        patient_dob,
        phonenumber,
        address1,
        address2,
        city,
        state,
        zip,
        timezone,
        rx_name,
        rx_number,
        rx_fillid,
        outstanding_balance,
        remaining_refills,
        balance_date,
        prescriber_name,
        prescriber_npi,
        txt_msg,
        txt_error_message,
        txt_error_code,
        txt_date_sent,
        existing_outreach_attempt,
        existing_outreach_date,
        existing_call_outcome,
        priority_score
    )
    SELECT
        p.id AS patient_id,
        cs.sqrcid AS cybersource_customerid,
        p.firstname AS patient_firstname,
        p.lastname AS patient_lastname,
        p.dob AS patient_dob,
        p.phone AS phonenumber,
        a.address1,
        a.address2,
        a.city,
        a.state,
        a.zip,
        zc.regional_names AS timezone,
        RTRIM(TRIM(m.brand_name), '[]') AS rx_name,
        r.id AS rx_number,
        rf.id AS rx_fillid,
        f.fee / 100 AS outstanding_balance,
        r.refills - COALESCE((
            SELECT SUM(rf2.qty)
            FROM rxfill rf2
            WHERE rf2.rxid = r.id
            AND rf2.paymentid IS NOT NULL
        ), 0) + 1 AS remaining_refills,
        CURRENT_DATE AS balance_date,
        SPLIT_PART(RTRIM(TRIM(d.name), ','), ',', 1) AS prescriber_name,
        d.npi AS prescriber_npi,
        tw.body AS txt_msg,
        tw.error_message AS txt_error_message,
        tw.error_code AS txt_error_code,
        tw.date_sent AS txt_date_sent,
        rf.outreach_attempt AS existing_outreach_attempt,
        rf.outreach_attempt_date AS existing_outreach_date,
        rf.call_outcome AS existing_call_outcome,
        CASE
            WHEN tw.error_code IS NOT NULL AND tw.error_code != 0
            THEN 1000000 + (CURRENT_DATE - rf.created::date)
            ELSE (CURRENT_DATE - rf.created::date)
        END AS priority_score
    FROM
        patient p
    JOIN rx r ON r.patientid = p.id
    JOIN doctor d ON r.doctorid = d.id
    JOIN rxfill rf ON rf.rxid = r.id
    JOIN medication m ON m.ndc = r.medicationid
    JOIN fee f ON f.ndc = m.ndc
    JOIN address a ON a.id = p.addressid
    JOIN zip_codes zc ON left(a.zip, 5) = LPAD(zc.zip::TEXT, 5, '0')
    LEFT JOIN (
        SELECT DISTINCT ON (patientid) sqrcid, patientid
        FROM payment
        WHERE provider = 'cybersource'
        AND sqrcid IS NOT NULL
        ORDER BY patientid, created DESC
    ) cs ON cs.patientid = p.id
    LEFT JOIN (
        SELECT DISTINCT ON (to_number) body, REGEXP_REPLACE(to_number, '^\+1', '') AS phone,
        error_code, error_message, date_sent
        FROM twilio_error_messages
        WHERE (to_number <> '+1' OR to_number <> '+10')
        AND direction = 'outbound-api'
        ORDER BY to_number, created_at DESC
    ) tw ON p.phone = tw.phone
    WHERE
        rf.status = 'paymentHold'
        AND rf.created >= (CURRENT_TIMESTAMP - interval '334 days')
        AND rf.created <= (CURRENT_TIMESTAMP - interval '5 days')
        AND r.virx IS false
        AND NOT EXISTS (
		select 1 
		from patient_call_queue pcq 
		where pcq.rx_fillid = rf.id)
    ON CONFLICT (rx_fillid) DO NOTHING;
    """

    try:
        logger.info(f"Starting patient_call_queue population task at {timezone.now()}")

        # Use the fred database connection as seen in your models
        with connections["fred"].cursor() as cursor:
            with transaction.atomic(using="fred"):
                # Execute the main query
                cursor.execute(sql_query)
                rows_inserted = cursor.rowcount

                logger.info(
                    f"Successfully inserted {rows_inserted} new records into patient_call_queue"
                )

        # Track successful insertions
        call_queue_processed_counter.labels(
            task_name="populate_patient_call_queue", status="created", env=env_value
        ).inc(rows_inserted)

        push_metrics_to_amp(
            "call_queue_records_processed_total",
            rows_inserted,
            {
                "task_name": "populate_patient_call_queue",
                "status": "created",
                "env": env_value,
            },
        )

        # Log summary
        summary = {
            "task_id": self.request.id,
            "execution_time": timezone.now(),
            "rows_inserted": rows_inserted,
            "status": "success",
        }

        logger.info(f"Task completed successfully: {summary}")
        return summary

    except Exception as exc:
        logger.error(f"Error in populate_patient_call_queue task: {exc}", exc_info=True)

        # Track error
        call_queue_errors_counter.labels(
            task_name="populate_patient_call_queue",
            error_type=type(exc).__name__,
            env=env_value,
        ).inc()

        push_metrics_to_amp(
            "call_queue_task_errors_total",
            1,
            {
                "task_name": "populate_patient_call_queue",
                "error_type": type(exc).__name__,
                "env": env_value,
            },
        )

        # Retry the task if it's a temporary error
        if self.request.retries < self.max_retries:
            logger.info(
                f"Retrying task in {self.default_retry_delay} seconds (attempt {self.request.retries + 1}/{self.max_retries})"
            )
            raise self.retry(exc=exc, countdown=self.default_retry_delay)

        # If max retries reached, log final failure
        logger.error(f"Task failed permanently after {self.max_retries} retries")
        raise exc

    finally:
        # Track duration
        duration = time.time() - start_time
        call_queue_duration_histogram.labels(
            task_name="populate_patient_call_queue", env=env_value
        ).observe(duration)

        push_metrics_to_amp(
            "call_queue_task_duration_seconds",
            duration,
            {"task_name": "populate_patient_call_queue", "env": env_value},
        )


@shared_task
def cleanup_expired_call_queue_records():
    """
    Task to mark patient_call_queue records as expired.

    Marks pending records as 'expired' if the associated rxfill is older than 334 days
    and has no patient_outreach records. This prevents outreach on prescriptions that
    are nearly a year old.
    """
    env_value = getattr(settings, "ENVIRONMENT", "unknown")
    start_time = time.time()

    try:
        logger.info("Starting cleanup of expired call queue records")

        expiration_query = """
        UPDATE patient_call_queue 
        SET queue_status = 'expired', updated_at = NOW()
        where queue_status in ('pending','on_hold')
        and rx_number in (
        select r.id from rx r where
        r.created <= (CURRENT_TIMESTAMP - interval '334 days')
        or r.status <> 'ok')
        and not exists (
        select 1 from patient_outreach po where po.rx_fillid = patient_call_queue.rx_fillid
        and po.status  = 'pending')
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(expiration_query)
            expired_count = cursor.rowcount

        # Track expired records
        call_queue_processed_counter.labels(
            task_name="cleanup_expired_call_queue_records",
            status="expired",
            env=env_value,
        ).inc(expired_count)

        push_metrics_to_amp(
            "call_queue_records_processed_total",
            expired_count,
            {
                "task_name": "cleanup_expired_call_queue_records",
                "status": "expired",
                "env": env_value,
            },
        )

        logger.info(f"Cleanup completed. Records expired: {expired_count}")
        return {"records_expired": expired_count, "status": "success"}

    except Exception as exc:
        logger.error(
            f"Error in cleanup_expired_call_queue_records task: {exc}", exc_info=True
        )

        # Track error
        call_queue_errors_counter.labels(
            task_name="cleanup_expired_call_queue_records",
            error_type=type(exc).__name__,
            env=env_value,
        ).inc()

        push_metrics_to_amp(
            "call_queue_task_errors_total",
            1,
            {
                "task_name": "cleanup_expired_call_queue_records",
                "error_type": type(exc).__name__,
                "env": env_value,
            },
        )

        raise exc

    finally:
        # Track duration
        duration = time.time() - start_time
        call_queue_duration_histogram.labels(
            task_name="cleanup_expired_call_queue_records", env=env_value
        ).observe(duration)

        push_metrics_to_amp(
            "call_queue_task_duration_seconds",
            duration,
            {"task_name": "cleanup_expired_call_queue_records", "env": env_value},
        )


def update_call_queue_priorities():
    """
    Optional task to recalculate priority scores for pending records
    based on current date (since priority is date-based).
    """
    try:
        logger.info("Starting priority score update for call queue")

        update_query = """
        UPDATE patient_call_queue 
        SET 
            priority_score = CASE
                WHEN txt_error_code IS NOT NULL AND txt_error_code != ''
                THEN 1000000 + (CURRENT_DATE - balance_date)
                ELSE (CURRENT_DATE - balance_date)
            END,
            updated_at = NOW()
        WHERE queue_status = 'pending'
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(update_query)
            rows_updated = cursor.rowcount

        logger.info(f"Updated priority scores for {rows_updated} pending records")
        return {"records_updated": rows_updated, "status": "success"}

    except Exception as exc:
        logger.error(
            f"Error in update_call_queue_priorities task: {exc}", exc_info=True
        )
        raise exc


@shared_task
def update_resolved_payment_holds():
    """
    Task to mark call queue records as complete when the corresponding
    rxfill is no longer in paymentHold status and is not in patient_outreach.
    """
    env_value = getattr(settings, "ENVIRONMENT", "unknown")
    start_time = time.time()

    try:
        logger.info("Starting update of resolved payment hold records")

        update_query = """
        UPDATE patient_call_queue 
        SET 
            queue_status = 'completed',
            updated_at = NOW()
        FROM rxfill rf
        WHERE rf.id = patient_call_queue.rx_fillid
        AND rf.status <> 'paymentHold'
        AND patient_call_queue.queue_status = 'pending'
        AND NOT EXISTS (
            SELECT 1 
            FROM patient_outreach po 
            WHERE po.rx_fillid = patient_call_queue.rx_fillid
            and po.status = 'pending'
        )
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(update_query)
            rows_updated = cursor.rowcount

        # Track resolved payment holds
        call_queue_processed_counter.labels(
            task_name="update_resolved_payment_holds", status="resolved", env=env_value
        ).inc(rows_updated)

        push_metrics_to_amp(
            "call_queue_records_processed_total",
            rows_updated,
            {
                "task_name": "update_resolved_payment_holds",
                "status": "resolved",
                "env": env_value,
            },
        )

        logger.info(
            f"Marked {rows_updated} call queue records as complete (payment holds resolved)"
        )
        return {"records_updated": rows_updated, "status": "success"}

    except Exception as exc:
        logger.error(
            f"Error in update_resolved_payment_holds task: {exc}", exc_info=True
        )

        # Track error
        call_queue_errors_counter.labels(
            task_name="update_resolved_payment_holds",
            error_type=type(exc).__name__,
            env=env_value,
        ).inc()

        push_metrics_to_amp(
            "call_queue_task_errors_total",
            1,
            {
                "task_name": "update_resolved_payment_holds",
                "error_type": type(exc).__name__,
                "env": env_value,
            },
        )

        raise exc

    finally:
        # Track duration
        duration = time.time() - start_time
        call_queue_duration_histogram.labels(
            task_name="update_resolved_payment_holds", env=env_value
        ).observe(duration)

        push_metrics_to_amp(
            "call_queue_task_duration_seconds",
            duration,
            {"task_name": "update_resolved_payment_holds", "env": env_value},
        )


@shared_task
def update_multiple_patient_queue_status():
    """
    Task to mark patient_call_queue records with 'multiple' status.

    Updates pending records to 'multiple' when a patient has more than one
    pending queue entry and the rx_fillid has no patient_outreach records.
    """
    env_value = getattr(settings, "ENVIRONMENT", "unknown")
    start_time = time.time()

    try:
        logger.info("Starting update of multiple patient queue status")

        update_query = """
        UPDATE patient_call_queue
        SET queue_status = 'multiple', updated_at = NOW()
        WHERE queue_status = 'pending'
        AND patient_id IN (
            SELECT pcq.patient_id
            FROM patient_call_queue pcq
            GROUP BY pcq.patient_id
            HAVING COUNT(*) > 1
        )
        AND NOT EXISTS (
            SELECT 1
            FROM patient_outreach po
            WHERE po.rx_fillid = patient_call_queue.rx_fillid
        )
        """

        with connections["fred"].cursor() as cursor:
            with transaction.atomic(using="fred"):
                cursor.execute(update_query)
                rows_updated = cursor.rowcount

                logger.info(
                    f"Successfully updated {rows_updated} records to 'multiple' status in patient_call_queue"
                )

        # Track multiple status updates
        call_queue_processed_counter.labels(
            task_name="update_multiple_patient_queue_status",
            status="multiple",
            env=env_value,
        ).inc(rows_updated)

        push_metrics_to_amp(
            "call_queue_records_processed_total",
            rows_updated,
            {
                "task_name": "update_multiple_patient_queue_status",
                "status": "multiple",
                "env": env_value,
            },
        )

        return {
            "status": "success",
            "rows_updated": rows_updated,
        }

    except Exception as exc:
        logger.error(
            f"Error in update_multiple_patient_queue_status task: {exc}", exc_info=True
        )

        # Track error
        call_queue_errors_counter.labels(
            task_name="update_multiple_patient_queue_status",
            error_type=type(exc).__name__,
            env=env_value,
        ).inc()

        push_metrics_to_amp(
            "call_queue_task_errors_total",
            1,
            {
                "task_name": "update_multiple_patient_queue_status",
                "error_type": type(exc).__name__,
                "env": env_value,
            },
        )

        raise exc

    finally:
        # Track duration
        duration = time.time() - start_time
        call_queue_duration_histogram.labels(
            task_name="update_multiple_patient_queue_status", env=env_value
        ).observe(duration)

        push_metrics_to_amp(
            "call_queue_task_duration_seconds",
            duration,
            {"task_name": "update_multiple_patient_queue_status", "env": env_value},
        )


@shared_task
def release_expired_on_hold_records():
    """
    Task to release patient_call_queue records from 'on_hold' status.

    Updates records from 'on_hold' to 'pending' when the existing_outreach_date
    is 2 or more days old, allowing them to be processed again.
    """
    env_value = getattr(settings, "ENVIRONMENT", "unknown")
    start_time = time.time()

    try:
        logger.info("Starting release of expired on_hold records")

        update_query = """
        UPDATE patient_call_queue
        SET queue_status = 'pending', updated_at = NOW()
        WHERE queue_status = 'on_hold'
        AND existing_outreach_date <= (CURRENT_TIMESTAMP - INTERVAL '2 days')
        """

        with connections["fred"].cursor() as cursor:
            with transaction.atomic(using="fred"):
                cursor.execute(update_query)
                rows_updated = cursor.rowcount

                logger.info(
                    f"Successfully released {rows_updated} records from 'on_hold' to 'pending' status in patient_call_queue"
                )

        # Track released records
        call_queue_processed_counter.labels(
            task_name="release_expired_on_hold_records",
            status="released",
            env=env_value,
        ).inc(rows_updated)

        push_metrics_to_amp(
            "call_queue_records_processed_total",
            rows_updated,
            {
                "task_name": "release_expired_on_hold_records",
                "status": "released",
                "env": env_value,
            },
        )

        return {
            "status": "success",
            "rows_updated": rows_updated,
        }

    except Exception as exc:
        logger.error(
            f"Error in release_expired_on_hold_records task: {exc}", exc_info=True
        )

        # Track error
        call_queue_errors_counter.labels(
            task_name="release_expired_on_hold_records",
            error_type=type(exc).__name__,
            env=env_value,
        ).inc()

        push_metrics_to_amp(
            "call_queue_task_errors_total",
            1,
            {
                "task_name": "release_expired_on_hold_records",
                "error_type": type(exc).__name__,
                "env": env_value,
            },
        )

        raise exc

    finally:
        # Track duration
        duration = time.time() - start_time
        call_queue_duration_histogram.labels(
            task_name="release_expired_on_hold_records", env=env_value
        ).observe(duration)

        push_metrics_to_amp(
            "call_queue_task_duration_seconds",
            duration,
            {"task_name": "release_expired_on_hold_records", "env": env_value},
        )


@shared_task
def process_patient_outreach_records():
    """
    Task to update patient_call_queue records based on the outcome of the Capacity call recorded in patient_outreach
    """
    env_value = getattr(settings, "ENVIRONMENT", "unknown")
    start_time = time.time()
    recipe_counters = {
        "recipe_1": {
            "success": 0,
            "failed": 0,
        },
        "recipe_2": {
            "success": 0,
            "failed": 0,
        },
        "recipe_3": {
            "success": 0,
            "failed": 0,
        },
        "recipe_4": {
            "success": 0,
            "failed": 0,
        },
        "invalid": {
            "failed": 0,
        },
    }

    try:
        logger.info("Starting Patient Outreach Processing")

        results = {}

        patient_outreach_records = PatientOutreach.objects.filter(
            status__exact="pending"
        )

        for patient_outreach_record in patient_outreach_records:
            rx_fillid = patient_outreach_record.rx_fillid
            outcome = patient_outreach_record.call_outcome
            if (
                outcome == "OAI_HUNG_UP"
                or outcome == "OAI_CALL_FAILED"
                or outcome == "OAI_NO_ANSWER"
                or outcome == "OAI_VM_ATTEMPT"
                or outcome == "OAI_BUSY_SIGNAL"
                or outcome == "OAI_CUST_TIMEDOUT"
            ) and patient_outreach_record.outreach_attempt < 3:
                """
                Recipe 1 - Set the patient_call_queue record to be called again after 2 days (no more than 3 calls total)
                """
                patient_call_queue_updates = {
                    "rx_fillid": patient_outreach_record.rx_fillid,
                    "queue_status": "on_hold",
                    "existing_outreach_attempt": patient_outreach_record.outreach_attempt,
                    "existing_outreach_date": patient_outreach_record.created,
                    "existing_call_outcome": patient_outreach_record.call_outcome,
                    "total_call_attempts": patient_outreach_record.outreach_attempt,
                }

                try:
                    with transaction.atomic(using="fred"):
                        serializer = UpdatePatientCallQueueSerializer(
                            data=patient_call_queue_updates
                        )
                        if not serializer.is_valid():
                            raise Exception(
                                f"Recipe 1 - Call Queue Serailizer Invalid: {serializer.errors}"
                            )
                        else:
                            update_result = update_patient_call_queue_record(serializer)
                            if update_result["status"] == "success":
                                patient_outreach_record.status = "completed"
                                patient_outreach_record.processed = timezone.now()
                                patient_outreach_record.full_clean()
                                patient_outreach_record.save()

                                results[patient_outreach_record.id] = {
                                    "status": "success",
                                    "message": "Recipe 1 - Success",
                                }
                                recipe_counters["recipe_1"]["success"] += 1
                            else:
                                raise Exception(
                                    f"Recipe 1 - Failed to Update Call Queue"
                                )
                except Exception as e:
                    results[patient_outreach_record.id] = {
                        "status": "failed",
                        "message": str(e),
                    }
                    patient_outreach_record.status = "failed"
                    patient_outreach_record.processed = timezone.now()
                    patient_outreach_record.full_clean()
                    patient_outreach_record.save()
                    recipe_counters["recipe_1"]["failed"] += 1
            elif (
                (
                    patient_outreach_record.outreach_attempt >= 3
                    and outcome != "OAI_SEND_PAYMENT_LINK"
                    and outcome != "OAI_ORDER_PAID"
                )
                or outcome == "OAI_CUST_NOT_INTERESTED"
                or outcome == "OAI_REQUEST_CALLBACK"
                or outcome == "OAI_XFER"
                or outcome == "OAI_XFER_ADDITIONAL_HELP"
                or outcome == "OAI_XFER_ADDRESS_MISMATCH"
                or outcome == "OAI_XFER_CC"
                or outcome == "OAI_XFER_PRICING"
                or outcome == "OAI_XFER_PAYMENT_FAILED"
                or outcome == "OAI_WRONG_NUMBER"
                or outcome == "OAI_DNC"
                or outcome == "OAI_INVALID_DESTINATION"
            ):
                """
                Recipe 2 - Set patient call queue record to not be called again.
                """
                patient_call_queue_updates = {
                    "rx_fillid": patient_outreach_record.rx_fillid,
                    "queue_status": "completed",
                    "existing_outreach_attempt": patient_outreach_record.outreach_attempt,
                    "existing_outreach_date": patient_outreach_record.created,
                    "existing_call_outcome": patient_outreach_record.call_outcome,
                    "total_call_attempts": patient_outreach_record.outreach_attempt,
                    "final_outcome": patient_outreach_record.call_outcome,
                }
                try:
                    with transaction.atomic(using="fred"):
                        serializer = UpdatePatientCallQueueSerializer(
                            data=patient_call_queue_updates
                        )
                        if not serializer.is_valid():
                            raise Exception(
                                f"Recipe 2 - Call Queue Serailizer Invalid: {serializer.errors}"
                            )
                        else:
                            update_result = update_patient_call_queue_record(serializer)
                            if update_result["status"] == "success":
                                patient_outreach_record.status = "completed"
                                patient_outreach_record.processed = timezone.now()
                                patient_outreach_record.full_clean()
                                patient_outreach_record.save()
                                results[patient_outreach_record.id] = {
                                    "status": "success",
                                    "message": "Recipe 2 - Success",
                                }
                                recipe_counters["recipe_2"]["success"] += 1
                            else:
                                raise Exception(
                                    f"Recipe 2 - Failed to Update Call Queue"
                                )
                except Exception as e:
                    results[patient_outreach_record.id] = {
                        "status": "failed",
                        "message": str(e),
                    }
                    patient_outreach_record.status = "failed"
                    patient_outreach_record.processed = timezone.now()
                    patient_outreach_record.full_clean()
                    patient_outreach_record.save()
                    recipe_counters["recipe_2"]["failed"] += 1
            elif outcome == "OAI_SEND_PAYMENT_LINK":
                """
                Recipe 3 - Send payment link to patient and complete call queue record
                """
                patient_call_queue_updates = {
                    "rx_fillid": patient_outreach_record.rx_fillid,
                    "queue_status": "completed",
                    "existing_outreach_attempt": patient_outreach_record.outreach_attempt,
                    "existing_outreach_date": patient_outreach_record.created,
                    "existing_call_outcome": patient_outreach_record.call_outcome,
                    "total_call_attempts": patient_outreach_record.outreach_attempt,
                    "final_outcome": patient_outreach_record.call_outcome,
                }
                try:
                    with transaction.atomic(using="fred"):
                        serializer = UpdatePatientCallQueueSerializer(
                            data=patient_call_queue_updates
                        )
                        if not serializer.is_valid():
                            raise Exception(
                                f"Recipe 3 - Call Queue Serailizer Invalid: {serializer.errors}"
                            )
                        else:
                            update_result = update_patient_call_queue_record(serializer)
                            if update_result["status"] == "success":
                                patient_outreach_record.status = "completed"
                                patient_outreach_record.processed = timezone.now()
                                patient_outreach_record.full_clean()
                                patient_outreach_record.save()
                            else:
                                raise Exception(
                                    f"Recipe 3 - Failed to Update Call Queue"
                                )
                            payment_text_result = send_payment_text(
                                patient_outreach_record.rx_fillid
                            )
                            if payment_text_result["status"] == "error":
                                raise Exception(
                                    f"Recipe 3 - Failed to Send Payment Text: {payment_text_result["message"]}"
                                )
                            results[patient_outreach_record.id] = {
                                "status": "success",
                                "message": "Recipe 3 - Payment Text Sent Successfully",
                            }
                            recipe_counters["recipe_3"]["success"] += 1
                except Exception as e:
                    results[patient_outreach_record.id] = {
                        "status": "failed",
                        "message": str(e),
                    }
                    patient_outreach_record.status = "failed"
                    patient_outreach_record.processed = timezone.now()
                    patient_outreach_record.full_clean()
                    patient_outreach_record.save()
                    recipe_counters["recipe_3"]["failed"] += 1
            elif outcome == "OAI_ORDER_PAID":
                """
                Recipe 4 - Make a Payment record in Fred and match it to the Rx. Complete the call queue record.
                """
                qty = 3 if patient_outreach_record.payment_amount > 60 else 1
                try:
                    rx = Rx.objects.get(id=patient_outreach_record.rxid)
                except Rx.DoesNotExist:
                    logger.error(
                        f"Error in process_patient_outreach_records task: Rx with id {patient_outreach_record.rxid} not found"
                    )
                    results[patient_outreach_record.id] = {
                        "status": "failed",
                        "message": f"Rx with id {patient_outreach_record.rxid} not found",
                    }
                    patient_outreach_record.status = "failed"
                    patient_outreach_record.processed = timezone.now()
                    patient_outreach_record.full_clean()
                    patient_outreach_record.save()
                    recipe_counters["recipe_4"]["failed"] += 1
                    continue

                create_payment_payload = {
                    "patientid": patient_outreach_record.patient_id,
                    "officeid": rx.officeid,
                    "amount": patient_outreach_record.payment_amount,
                    "txid": patient_outreach_record.request_id,
                    "sqrcid": "",
                    "qty": qty,
                    "type": "payment",
                    "status": "completed",
                    "paymentProvider": "cybersource",
                    "discount": 24.75 if qty == 3 else 0.00,
                    "shippingcost": patient_outreach_record.shipping_fee,
                    "couponDiscountMap": (
                        [{"couponcode": "kfhnuxxn90daybulk", "amount": "24.75"}]
                        if qty == 3
                        else {}
                    ),
                }
                client = APIClient()
                client.credentials(
                    HTTP_AUTHORIZATION="Token " + settings.INTERNAL_TOKEN
                )
                try:
                    with transaction.atomic(using="fred"):
                        response = client.post(
                            settings.API_DOMAIN + "fred/v1/payments/create/",
                            create_payment_payload,
                            format="json",
                        )
                        logger.info(response.content)
                        response_json = json.loads(response.content)
                        if "error" not in response_json:
                            payment_details = response_json["payment"]

                            match_rx_payload = {
                                "payment_id": payment_details["id"],
                                "rxfill_id": patient_outreach_record.rx_fillid,
                                "qty": qty,
                            }
                            match_rx_response = client.post(
                                settings.API_DOMAIN
                                + "fred/v1/payments/match-to-rxfill/",
                                match_rx_payload,
                                format="json",
                            )
                            match_rx_response_json = json.loads(
                                match_rx_response.content
                            )
                            if "error" not in match_rx_response_json:
                                patient_call_queue_updates = {
                                    "rx_fillid": patient_outreach_record.rx_fillid,
                                    "queue_status": "completed",
                                    "existing_outreach_attempt": patient_outreach_record.outreach_attempt,
                                    "existing_outreach_date": patient_outreach_record.created,
                                    "existing_call_outcome": patient_outreach_record.call_outcome,
                                    "total_call_attempts": patient_outreach_record.outreach_attempt,
                                    "final_outcome": patient_outreach_record.call_outcome,
                                }
                                serializer = UpdatePatientCallQueueSerializer(
                                    data=patient_call_queue_updates
                                )
                                if not serializer.is_valid():
                                    results[patient_outreach_record.id] = {
                                        "error": serializer.errors,
                                        "status": "failed",
                                    }
                                    recipe_counters["recipe_4"]["failed"] += 1
                                else:
                                    update_result = update_patient_call_queue_record(
                                        serializer
                                    )
                                    if update_result["status"] == "success":
                                        patient_outreach_record.status = "completed"
                                        patient_outreach_record.processed = (
                                            timezone.now()
                                        )
                                        patient_outreach_record.full_clean()
                                        patient_outreach_record.save()
                                    else:
                                        raise Exception(
                                            f"Recipe 4 - Failed to Update Call Queue"
                                        )
                                results[patient_outreach_record.id] = {
                                    "status": "success"
                                }
                                recipe_counters["recipe_4"]["success"] += 1
                            else:
                                raise Exception(
                                    f"Recipe 4 - Failed Payment Match: {match_rx_response_json["error"]}"
                                )
                        else:
                            raise Exception(
                                f"Recipe 4 - Failed to create Payment record {response_json["error"]}"
                            )
                except Exception as e:
                    logger.error(f"Error in process_patient_outreach_records task: {e}")
                    results[patient_outreach_record.id] = {
                        "status": "failed",
                        "message": str(e),
                    }
                    patient_outreach_record.status = "failed"
                    patient_outreach_record.processed = timezone.now()
                    patient_outreach_record.full_clean()
                    patient_outreach_record.save()
                    recipe_counters["recipe_4"]["failed"] += 1
            else:
                results[patient_outreach_record.id] = {
                    "status": "failed",
                    "message": "Invalid Call Outcome",
                }
                patient_outreach_record.status = "failed"
                patient_outreach_record.processed = timezone.now()
                patient_outreach_record.full_clean()
                patient_outreach_record.save()
                recipe_counters["invalid"]["failed"] += 1

        # Push metrics for each recipe
        for recipe, value in recipe_counters.items():
            if recipe != "invalid":
                outreach_processed_counter.labels(
                    recipe=recipe,
                    status="success",
                    env=env_value,
                ).inc(value["success"])

                push_metrics_to_amp(
                    "patient_outreach_processed_total",
                    value["success"],
                    {
                        "recipe": recipe,
                        "status": "success",
                        "env": env_value,
                    },
                )

            outreach_processed_counter.labels(
                recipe=recipe,
                status="failed",
                env=env_value,
            ).inc(value["failed"])

            push_metrics_to_amp(
                "patient_outreach_processed_total",
                value["failed"],
                {
                    "recipe": recipe,
                    "status": "failed",
                    "env": env_value,
                },
            )
        logger.info(results)
        return results

    except Exception as exc:
        logger.error(
            f"Error in process_patient_outreach_records task: {exc}", exc_info=True
        )

        # Track error
        call_queue_errors_counter.labels(
            task_name="process_patient_outreach_records",
            error_type=type(exc).__name__,
            env=env_value,
        ).inc()

        push_metrics_to_amp(
            "call_queue_task_errors_total",
            1,
            {
                "task_name": "process_patient_outreach_records",
                "error_type": type(exc).__name__,
                "env": env_value,
            },
        )

        raise exc

    finally:
        # Track duration
        duration = time.time() - start_time
        call_queue_duration_histogram.labels(
            task_name="process_patient_outreach_records", env=env_value
        ).observe(duration)

        push_metrics_to_amp(
            "call_queue_task_duration_seconds",
            duration,
            {"task_name": "process_patient_outreach_records", "env": env_value},
        )


def update_patient_call_queue_record(serializer):
    patient_call_queue_record = PatientCallQueue.objects.get(
        rx_fillid__exact=serializer.data["rx_fillid"]
    )
    for key, value in serializer.data.items():
        setattr(patient_call_queue_record, key, value)
        logger.info(f"Set {key} to {value}")
    patient_call_queue_record.full_clean()
    patient_call_queue_record.save()
    return {"status": "success"}


def send_payment_text(fillid):
    """
    Get necessary payment text info
    """
    try:
        """
        Get a pay token for the rxfill if one exists
        """
        rxfill_token = Token.objects.filter(
            recordid=fillid, type__exact="pay", recordtype__exact="fill"
        ).exclude(status__exact="inactive")

        """
        Get the rxfill information
        """
        try:
            rxfill = Rxfill.objects.get(id=fillid)
        except Rxfill.DoesNotExist:
            return {"status": "error", "message": f"RxFill with id {fillid} not found"}

        """
        Get the Rx Information
        """
        try:
            rx = Rx.objects.get(id=rxfill.rxid)
        except Rx.DoesNotExist:
            return {"status": "error", "message": f"Rx with id {rxfill.rxid} not found"}

        """
        Get the Patient Information
        """
        try:
            patient = Patient2.objects.get(id=rx.patientid)
        except Patient2.DoesNotExist:
            return {
                "status": "error",
                "message": f"Patient with id {rx.patientid} not found",
            }

        """
        Get the Medication information
        """
        try:
            medication = Medication.objects.get(ndc__exact=rx.medicationid)
        except Medication.DoesNotExist:
            return {
                "status": "error",
                "message": f"Medication with NDC {rx.medicationid} not found",
            }

        """
        Get the fee of the medication
        """
        try:
            fee = Fee.objects.get(ndc__exact=medication.ndc)
        except Fee.DoesNotExist:
            return {
                "status": "error",
                "message": f"Fee with NDC {medication.ndc} not found",
            }

        """
        Get the Office of the Rx
        """
        try:
            office = Office.objects.get(id=rx.officeid)
        except Office.DoesNotExist:
            return {
                "status": "error",
                "message": f"Office with id {rx.officeid} not found",
            }

        """
        If the token does not exist, we need to create one, which will require some more information.
        """
        if not rxfill_token:
            try:
                token = Token(
                    token=secrets.token_urlsafe(8),
                    status="active",
                    type="pay",
                    recordtype="fill",
                    recordid=rxfill.id,
                    amount=rx.qty * fee.fee / 100,
                    created=timezone.now(),
                )
                token.save()
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Payment Token could not be created",
                }
        else:
            token = rxfill_token[0]

        """
        Decide the verbiage of the text to send
        """
        dh_url = f"{settings.DH_APP_URL}/rx/{token.token}"
        msg = f"Your SKNV prescription is ready to ship. Please use this secure link to pay for your Rx and confirm your shipping address: {dh_url}"

        if rxfill.type == "newrx" and office.name is not None:
            msg = f"Your SKNV prescription from {office.name} is ready to ship. Please use this secure link to pay for your Rx and confirm your shipping address: {dh_url}"
        elif rxfill.type == "refill" and office.name is not None:
            msg = f"It's time to refill your SKNV prescription from {office.name}. If you would like your refill, please use this secure link to pay & confirm your shipping address: {dh_url}"
        elif rxfill.type == "refill" and office.name is None:
            msg = f"It's time to refill your SKNV prescription. If you would like your refill, please use this secure link to pay & confirm your shipping address: {dh_url}"

        """
        Send Text
        """
        try:
            text_sent_token = secrets.token_urlsafe().replace("_", "0")
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_=f"{settings.TWILIO_FROM_NUMBER}",
                body=msg,
                to=patient.phone,
                status_callback=f"{settings.FRED_API}/text/update/{text_sent_token}",
            )
        except Exception as e:
            return {"status": "error", "message": f"Failed to send Text Message"}

        """
        Create TextSent Object in Fred DB
        """
        try:
            text_sent = Textsent(
                patientid=patient.id,
                rxid=rx.id,
                type="payment-confirmation",
                phonenumber=patient.phone,
                sid=message.sid,
                status=message.status,
                message=(
                    message.error_message
                    if message.error_message is not None
                    else "The API request to send a message was successful and the message is queued to be sent out."
                ),
                token=text_sent_token,
                datecreated=timezone.now(),
                datemodified=None,
            )
            text_sent.save()
        except Exception as e:
            return {"status": "error", "message": f"Failed to create Textsent record"}

        return {
            "status": "success",
            "message": "Successfully sent message",
            "textsentid": text_sent.id,
        }
    except Exception as e:
        logger.error(f"Error in Manual Payment Text: {e}")
        return {
            "status": "error",
            "message": "An error occurred during manual payment text",
        }
