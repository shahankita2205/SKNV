#!/usr/bin/env python3
"""
Celery task for ASAP Prescription Dispensing Data Import
Pulls prescription dispensing data directly from database tables and inserts into prescription_dispenses table
"""

from celery import shared_task
from django.db import connections, transaction
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
import logging

# Set up logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def import_prescription_dispenses_from_db_task(self, target_date=None, dry_run=False):
    """
    Celery task to import prescription dispensing data directly from database tables

    Args:
        target_date: Date string in format YYYY-MM-DD (defaults to yesterday)
        dry_run: If True, performs validation but doesn't insert data

    Returns:
        dict: Results including number of records inserted and summary stats
    """

    task_id = self.request.id
    logger.info(f"Task {task_id}: Starting prescription dispensing import")

    # Default to yesterday if no date provided
    if target_date is None:
        yesterday = timezone.now() - timedelta(days=1)
        target_date = yesterday.strftime("%Y-%m-%d")

    # Validate date format
    try:
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        error_msg = f"Invalid date format: {target_date}. Please use YYYY-MM-DD format"
        logger.error(f"Task {task_id}: {error_msg}")
        raise ValueError(error_msg)

    logger.info(
        f"Task {task_id}: Importing prescription dispensing data for date: {target_date}"
    )

    try:
        # Use the 'fred' database connection
        with connections["fred"].cursor() as cursor:
            # Start transaction
            with transaction.atomic(using="fred"):

                if dry_run:
                    logger.info(f"Task {task_id}: Running in dry-run mode")
                    # Count query for dry run - matches your working query structure
                    count_query = """
                    SELECT COUNT(*) as potential_records
                    FROM rx r
                    JOIN patient p ON p.id = r.patientid
                    JOIN address a ON a.id = p.addressid
                    JOIN office o ON o.id = r.officeid
                    JOIN rxfill rf ON rf.rxid = r.id
                    JOIN doctor d ON d.id = r.doctorid
                    JOIN medication m ON m.ndc = r.medicationid
                    JOIN address a1 ON a1.id = o.addressid
                    LEFT JOIN officeinfo oi ON oi.officeid = o.id
                    WHERE a.state = 'MD'
                    AND rf.created >= DATE_TRUNC('day', DATE %s)
                    AND rf.created < DATE_TRUNC('day', DATE %s + INTERVAL '1 day')
                    AND rf.status = 'dispensedInOffice'
                    """

                    cursor.execute(count_query, [target_date, target_date])
                    result = cursor.fetchone()
                    potential_records = result[0] if result else 0

                    logger.info(
                        f"Task {task_id}: Dry run complete. Would process {potential_records} records"
                    )

                    return {
                        "task_id": task_id,
                        "target_date": target_date,
                        "dry_run": True,
                        "potential_records": potential_records,
                        "records_inserted": 0,
                        "status": "success",
                    }

                # The main import query
                import_query = """
                INSERT INTO prescription_dispenses
                (report_start_date, report_end_date, created_at, updated_at, status, 
                 patient_first_name, patient_last_name, patient_dob, patient_gender, 
                 patient_address1, patient_city, patient_state, patient_zip, patient_phone, 
                 rx_number, date_written, refills_authorized, date_filled, fill_number, 
                 ndc, quantity_dispensed, days_supply, dosage_units, payment_type, date_sold, 
                 prescriber_npi, prescriber_dea, prescriber_last_name, prescriber_first_name, 
                 prescriber_middle_name, reporting_status, pharmacy_npi, pharmacy_dea, 
                 pharmacy_name, pharmacy_address1, pharmacy_address2, pharmacy_city, 
                 pharmacy_state, pharmacy_zip, pharmacy_phone, pharmacy_source_id)
                SELECT
                    date(r.created) as report_start_date,
                    date(r.created)+1 as report_end_date,
                    CURRENT_TIMESTAMP as created_at,
                    CURRENT_TIMESTAMP as updated_at,
                    'pending' as status,
                    p.firstname as patient_first_name,
                    p.lastname as patient_last_name,
                    TO_DATE(p.dob, 'YYYYMMDD') as patient_dob,
                    p.gender as patient_gender,
                    a.address1 as patient_address1,
                    a.city as patient_city,
                    a.state as patient_state,
                    a.zip as patient_zip,
                    p.phone as patient_phone,
                    r.id as rx_number,
                    date(r.created) as date_written,
                    r.refills as refills_authorized,
                    date(r.created) as date_filled,
                    0 as fill_number,
                    replace(r.medicationid,'-','') as ndc,
                    rf.qty * cast(SUBSTRING(m.size FROM '^[0-9]+\.?[0-9]*') as numeric) as quantity_dispensed,
                    rf.qty * 30 as days_supply,
                    CASE
                        WHEN lower(REGEXP_REPLACE(
                            REGEXP_REPLACE(m.size, '^[\d.]+', ''),
                            '[()]', '', 'g'
                        )) = 'ml' THEN '02'
                        WHEN lower(REGEXP_REPLACE(
                            REGEXP_REPLACE(m.size, '^[\d.]+', ''),
                            '[()]', '', 'g'
                        )) = 'gm' THEN '03'
                        ELSE '01'
                    END AS dosage_units,
                    '01' as payment_type,
                    date(r.created) as date_sold,
                    d.npi as prescriber_npi,
                    '' as prescriber_dea,
                    TRIM(REGEXP_REPLACE(SPLIT_PART(d.name, ',', 1), '^.*\s+(\S+)$', E'\\1')) AS prescriber_last_name,
                    TRIM(REGEXP_REPLACE(SPLIT_PART(d.name, ',', 1), '\s+\S+$', '')) AS prescriber_first_name,
                    '' as prescriber_middle_name,
                    '00' as reporting_status,
                    '' as pharmacy_npi,
                    '' as pharmacy_dea,
                    o.name as pharmacy_name,
                    a1.address1 as pharmacy_address1,
                    a1.address2 as pharmacy_address2,
                    a1.city as pharmacy_city,
                    a1.state as pharmacy_state,
                    a1.zip as pharmacy_zip,
                    oi.primaryphone as pharmacy_phone,
                    '' as pharmacy_source_id
                FROM rx r
                JOIN patient p ON p.id = r.patientid
                JOIN address a ON a.id = p.addressid
                JOIN office o ON o.id = r.officeid
                JOIN rxfill rf ON rf.rxid = r.id
                JOIN doctor d ON d.id = r.doctorid
                JOIN medication m ON m.ndc = r.medicationid
                JOIN address a1 ON a1.id = o.addressid
                LEFT JOIN officeinfo oi ON oi.officeid = o.id
                WHERE a.state = 'MD'
                AND rf.created >= DATE_TRUNC('day', DATE %s)
                AND rf.created < DATE_TRUNC('day', DATE %s + INTERVAL '1 day')
                AND rf.status = 'dispensedInOffice'
                ON CONFLICT (rx_number, fill_number) DO NOTHING
                """

                # Execute the import query
                cursor.execute(import_query, [target_date, target_date])

                # Get the number of rows affected
                records_inserted = cursor.rowcount

                logger.info(
                    f"Task {task_id}: Successfully imported {records_inserted} prescription dispensing records"
                )

                # Get summary statistics
                summary_query = """
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT patient_last_name || patient_first_name) as unique_patients,
                    COUNT(DISTINCT prescriber_npi) as unique_prescribers,
                    COUNT(DISTINCT pharmacy_name) as unique_pharmacies
                FROM prescription_dispenses 
                WHERE report_start_date = %s
                """

                cursor.execute(summary_query, [target_date])
                summary_result = cursor.fetchone()

                summary_stats = {}
                if summary_result:
                    summary_stats = {
                        "total_records": summary_result[0],
                        "unique_patients": summary_result[1],
                        "unique_prescribers": summary_result[2],
                        "unique_pharmacies": summary_result[3],
                    }

                    logger.info(f"Task {task_id}: Summary for {target_date}:")
                    logger.info(f"  - Total records: {summary_stats['total_records']}")
                    logger.info(
                        f"  - Unique patients: {summary_stats['unique_patients']}"
                    )
                    logger.info(
                        f"  - Unique prescribers: {summary_stats['unique_prescribers']}"
                    )
                    logger.info(
                        f"  - Unique pharmacies: {summary_stats['unique_pharmacies']}"
                    )

                return {
                    "task_id": task_id,
                    "target_date": target_date,
                    "records_inserted": records_inserted,
                    "summary_stats": summary_stats,
                    "status": "success",
                    "dry_run": False,
                }

    except Exception as e:
        logger.error(
            f"Task {task_id}: Error importing prescription dispenses: {str(e)}"
        )

        # Retry logic for transient errors
        if self.request.retries < self.max_retries:
            logger.info(
                f"Task {task_id}: Retrying in {self.default_retry_delay} seconds (attempt {self.request.retries + 1}/{self.max_retries})"
            )
            raise self.retry(countdown=self.default_retry_delay, exc=e)

        # If max retries reached, return error result
        return {
            "task_id": task_id,
            "target_date": target_date,
            "error": str(e),
            "status": "failed",
            "records_inserted": 0,
        }


@shared_task(bind=True)
def import_prescription_dispenses_date_range_task(
    self, start_date, end_date, dry_run=False
):
    """
    Celery task to import prescription dispensing data for a date range

    Args:
        start_date: Start date string in format YYYY-MM-DD
        end_date: End date string in format YYYY-MM-DD
        dry_run: If True, performs validation but doesn't insert data

    Returns:
        dict: Results for each date processed
    """

    task_id = self.request.id
    logger.info(
        f"Task {task_id}: Starting date range import from {start_date} to {end_date}"
    )

    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        error_msg = (
            f"Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}"
        )
        logger.error(f"Task {task_id}: {error_msg}")
        raise ValueError(error_msg)

    if start_date_obj > end_date_obj:
        error_msg = "Start date must be before or equal to end date"
        logger.error(f"Task {task_id}: {error_msg}")
        raise ValueError(error_msg)

    results = []
    current_date = start_date_obj

    while current_date <= end_date_obj:
        date_str = current_date.strftime("%Y-%m-%d")
        logger.info(f"Task {task_id}: Processing date {date_str}")

        try:
            # Call the single-date import task
            result = import_prescription_dispenses_from_db_task.apply_async(
                args=[date_str, dry_run], queue="prescription_dispense"
            ).get()

            results.append({"date": date_str, "result": result})

        except Exception as e:
            logger.error(f"Task {task_id}: Error processing date {date_str}: {str(e)}")
            results.append({"date": date_str, "error": str(e), "status": "failed"})

        current_date += timedelta(days=1)

    logger.info(f"Task {task_id}: Completed date range import")

    return {
        "task_id": task_id,
        "start_date": start_date,
        "end_date": end_date,
        "results": results,
        "total_dates_processed": len(results),
        "successful_dates": len(
            [r for r in results if r.get("result", {}).get("status") == "success"]
        ),
        "failed_dates": len(
            [
                r
                for r in results
                if "error" in r or r.get("result", {}).get("status") == "failed"
            ]
        ),
    }


@shared_task(bind=True)
def cleanup_old_prescription_dispenses_task(self, days_to_keep=90):
    """
    Celery task to cleanup old prescription dispense records

    Args:
        days_to_keep: Number of days of records to keep (default 90)

    Returns:
        dict: Cleanup results
    """

    task_id = self.request.id
    logger.info(
        f"Task {task_id}: Starting cleanup of prescription dispenses older than {days_to_keep} days"
    )

    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        with connections["fred"].cursor() as cursor:
            with transaction.atomic(using="fred"):
                # Count records to be deleted
                count_query = """
                SELECT COUNT(*) FROM prescription_dispenses 
                WHERE report_start_date < %s
                """
                cursor.execute(count_query, [cutoff_date.date()])
                records_to_delete = cursor.fetchone()[0]

                if records_to_delete == 0:
                    logger.info(f"Task {task_id}: No old records found to delete")
                    return {
                        "task_id": task_id,
                        "records_deleted": 0,
                        "cutoff_date": cutoff_date.date().strftime("%Y-%m-%d"),
                        "status": "success",
                    }

                # Delete old records
                delete_query = """
                DELETE FROM prescription_dispenses 
                WHERE report_start_date < %s
                """
                cursor.execute(delete_query, [cutoff_date.date()])
                records_deleted = cursor.rowcount

                logger.info(
                    f"Task {task_id}: Deleted {records_deleted} old prescription dispense records"
                )

                return {
                    "task_id": task_id,
                    "records_deleted": records_deleted,
                    "cutoff_date": cutoff_date.date().strftime("%Y-%m-%d"),
                    "status": "success",
                }

    except Exception as e:
        logger.error(f"Task {task_id}: Error during cleanup: {str(e)}")
        return {
            "task_id": task_id,
            "error": str(e),
            "status": "failed",
            "records_deleted": 0,
        }
