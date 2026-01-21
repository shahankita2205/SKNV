# tasks/hubspot/tasks.py
"""
Celery tasks for HubSpot data synchronization.

This module provides all the functionality needed to sync data between Fred (source of truth)
and HubSpot CRM. All database operations use Django's database connections (no SSH tunnels needed).

Pipeline Steps (as individual tasks):
1. extract_fred_data - Extract Fred data into hubspot.fred_data table
2. export_hubspot_contacts - Fetch contacts from HubSpot API and store in DB
3. export_hubspot_companies - Fetch companies from HubSpot API and store in DB
4. export_hubspot_owners - Fetch owners from HubSpot API and store in DB
5. compare_fred_hubspot - Compare Fred vs HubSpot and identify changes
6. create_hubspot_companies - Create new companies in HubSpot
7. create_hubspot_contacts - Create new contacts in HubSpot
8. update_hubspot_companies - Update existing companies in HubSpot
9. update_hubspot_contacts - Update existing contacts in HubSpot

Orchestration:
- run_hubspot_sync_pipeline - Runs all steps in sequence
"""
import io
import logging
import time
import requests
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any, Set

from django.db import connections, transaction
from django.conf import settings
from celery import shared_task, chain
from celery.utils.log import get_task_logger
from django.utils import timezone

from prometheus_client import Counter, Histogram

from ..prometheus_remote_write import push_sample_to_amp

logger = get_task_logger(__name__)


# =============================================================================
# Prometheus Metrics
# =============================================================================

hubspot_task_counter = Counter(
    "hubspot_task_total",
    "Total number of HubSpot task executions",
    ["task_name", "status", "env"],
)

hubspot_task_duration = Histogram(
    "hubspot_task_duration_seconds",
    "Duration of HubSpot tasks in seconds",
    ["task_name", "env"],
    buckets=[10, 30, 60, 120, 300, 600, 900, 1800, 3600],
)

hubspot_records_counter = Counter(
    "hubspot_records_processed_total",
    "Total number of records processed",
    ["task_name", "record_type", "env"],
)


# =============================================================================
# Utility Functions
# =============================================================================


def get_env_value() -> str:
    """Get environment value for metrics"""
    return getattr(settings, "ENVIRONMENT", "unknown")


def get_hubspot_access_token() -> str:
    """Get HubSpot access token from settings"""
    return getattr(settings, "HUBSPOT_ACCESS_TOKEN", "")


def push_metrics_to_amp(metric_name: str, value: float, labels: Dict[str, str]) -> bool:
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


def track_task_metrics(
    task_name: str,
    status: str,
    duration: float,
    record_count: int = 0,
    record_type: str = "",
):
    """Track task metrics in Prometheus"""
    env = get_env_value()

    hubspot_task_counter.labels(task_name=task_name, status=status, env=env).inc()
    hubspot_task_duration.labels(task_name=task_name, env=env).observe(duration)

    if record_count > 0 and record_type:
        hubspot_records_counter.labels(
            task_name=task_name, record_type=record_type, env=env
        ).inc(record_count)

    push_metrics_to_amp(
        "hubspot_task_total", 1, {"task_name": task_name, "status": status, "env": env}
    )
    push_metrics_to_amp(
        "hubspot_task_duration_seconds", duration, {"task_name": task_name, "env": env}
    )


def convert_for_json(value: Any) -> Any:
    """Convert value to JSON-serializable type.

    Handles Decimal conversion to string to preserve precision for currency values.
    """
    if isinstance(value, Decimal):
        return str(value)
    return value


def deduplicate_batch_updates(batch_updates: list, logger) -> list:
    """Deduplicate batch updates by ID, merging properties for duplicates."""
    seen_ids = {}
    deduplicated = []

    for update in batch_updates:
        record_id = update["id"]
        if record_id in seen_ids:
            seen_ids[record_id]["properties"].update(update["properties"])
        else:
            seen_ids[record_id] = update
            deduplicated.append(update)

    duplicate_count = len(batch_updates) - len(deduplicated)
    if duplicate_count > 0:
        logger.warning(f"Removed {duplicate_count} duplicate IDs from batch updates")

    return deduplicated


# =============================================================================
# HubSpot API Client
# =============================================================================


class HubSpotAPIClient:
    """Client for HubSpot API operations"""

    BASE_URL = "https://api.hubapi.com"

    # Contact properties to fetch
    CONTACT_PROPERTIES = [
        "firstname",
        "lastname",
        "phone",
        "email",
        "npi_number",
        "total_rx_created",
        "total_rx_paid",
        "total_rx_paid_amount",
        "total_rx_unpaid",
        "total_rx_unpaid_amount",
        "total_rx_fills_created",
        "total_rx_fills_paid",
        "total_rx_fills_paid_amount",
        "total_rx_fills_unpaid",
        "total_rx_fills_unpaid_amount",
        "total_dios_created",
        "total_dtps_created",
        "total_dtps_paid",
        "total_dtps_unpaid",
    ]

    # Company properties to fetch
    COMPANY_PROPERTIES = [
        "fred_id",
        "name",
        "address",
        "address2",
        "city",
        "state_abbreviation",
        "zip",
        "phone",
        "company_email",
        "new_netsuite_id",
        "hubspot_owner_id",
        "company_type",
        "rx_total_shipments",
        "suppress_refill_notifications",
        "total_rx_created",
        "total_rx_paid",
        "total_rx_paid_amount",
        "total_rx_unpaid",
        "total_rx_unpaid_amount",
        "total_rx_fills_created",
        "total_rx_fills_paid",
        "total_rx_fills_paid_amount",
        "total_rx_fills_unpaid",
        "total_rx_fills_unpaid_amount",
        "total_dios_created",
        "total_dtps_created",
        "total_dtps_paid",
        "total_dtps_unpaid",
    ]

    # Owner properties to fetch
    OWNER_PROPERTIES = [
        "email",
        "firstName",
        "lastName",
        "userId",
        "createdAt",
        "updatedAt",
    ]

    def __init__(self, access_token: str = None):
        self.access_token = access_token or get_hubspot_access_token()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make HTTP request to HubSpot API with error handling and rate limiting"""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                logger.warning(f"Rate limit hit. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, **kwargs)
            else:
                logger.error(f"HTTP Error {response.status_code}: {e}")
                logger.error(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {e}")
            return None

    def get_all_contacts(self, limit: int = 100) -> List[Dict]:
        """Fetch all contacts from HubSpot"""
        all_contacts = []
        after = None

        params = {
            "limit": min(limit, 100),
            "properties": ",".join(self.CONTACT_PROPERTIES),
        }

        while True:
            if after:
                params["after"] = after

            response = self._make_request(
                "GET", "/crm/v3/objects/contacts", params=params
            )

            if not response:
                break

            results = response.get("results", [])
            all_contacts.extend(results)

            logger.info(f"Fetched {len(results)} contacts (Total: {len(all_contacts)})")

            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")

            if not after:
                break

            time.sleep(0.1)

        return all_contacts

    def get_all_companies(self, limit: int = 100) -> List[Dict]:
        """Fetch all companies from HubSpot"""
        all_companies = []
        after = None

        params = {
            "limit": min(limit, 100),
            "properties": ",".join(self.COMPANY_PROPERTIES),
        }

        while True:
            if after:
                params["after"] = after

            response = self._make_request(
                "GET", "/crm/v3/objects/companies", params=params
            )

            if not response:
                break

            results = response.get("results", [])
            all_companies.extend(results)

            logger.info(
                f"Fetched {len(results)} companies (Total: {len(all_companies)})"
            )

            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")

            if not after:
                break

            time.sleep(0.1)

        return all_companies

    def get_all_owners(self) -> List[Dict]:
        """Fetch all owners from HubSpot"""
        all_owners = []
        after = None

        while True:
            params = {"limit": 100}
            if after:
                params["after"] = after

            response = self._make_request("GET", "/crm/v3/owners", params=params)

            if not response:
                break

            results = response.get("results", [])
            all_owners.extend(results)

            logger.info(f"Fetched {len(results)} owners (Total: {len(all_owners)})")

            paging = response.get("paging", {})
            after = paging.get("next", {}).get("after")

            if not after:
                break

        return all_owners

    def create_company(self, properties: Dict[str, Any]) -> Optional[Dict]:
        """Create a company in HubSpot"""
        return self._make_request(
            "POST", "/crm/v3/objects/companies", json={"properties": properties}
        )

    def update_company(
        self, company_id: str, properties: Dict[str, Any]
    ) -> Optional[Dict]:
        """Update a company in HubSpot"""
        return self._make_request(
            "PATCH",
            f"/crm/v3/objects/companies/{company_id}",
            json={"properties": properties},
        )

    def create_contact(self, properties: Dict[str, Any]) -> Optional[Dict]:
        """Create a contact in HubSpot"""
        return self._make_request(
            "POST", "/crm/v3/objects/contacts", json={"properties": properties}
        )

    def update_contact(
        self, contact_id: str, properties: Dict[str, Any]
    ) -> Optional[Dict]:
        """Update a contact in HubSpot"""
        return self._make_request(
            "PATCH",
            f"/crm/v3/objects/contacts/{contact_id}",
            json={"properties": properties},
        )

    def search_company_by_fred_id(self, fred_id: str) -> Optional[Dict]:
        """Search for a company by Fred ID"""
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "fred_id",
                            "operator": "EQ",
                            "value": str(fred_id),
                        }
                    ]
                }
            ],
            "properties": ["name", "fred_id"],
            "limit": 1,
        }
        response = self._make_request(
            "POST", "/crm/v3/objects/companies/search", json=payload
        )
        if response and response.get("results"):
            return response["results"][0]
        return None

    def search_contact_by_npi(self, npi: str) -> Optional[Dict]:
        """Search for a contact by NPI"""
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "npi_number",
                            "operator": "EQ",
                            "value": str(npi),
                        }
                    ]
                }
            ],
            "properties": ["firstname", "lastname", "npi_number", "email"],
            "limit": 1,
        }
        response = self._make_request(
            "POST", "/crm/v3/objects/contacts/search", json=payload
        )
        if response and response.get("results"):
            return response["results"][0]
        return None

    def associate_contact_to_company(self, contact_id: str, company_id: str) -> bool:
        """Associate a contact to a company"""
        endpoint = f"/crm/v3/objects/contacts/{contact_id}/associations/companies/{company_id}/contact_to_company"
        response = self._make_request("PUT", endpoint)
        return response is not None

    def batch_update_companies(self, updates: List[Dict[str, Any]]) -> Optional[Dict]:
        """
        Batch update companies in HubSpot.

        Args:
            updates: List of dicts with 'id' and 'properties' keys
                    e.g., [{'id': '123', 'properties': {'name': 'New Name'}}]

        Returns:
            API response or None on failure
        """
        if not updates:
            return {"results": [], "status": "COMPLETE"}

        return self._make_request(
            "POST", "/crm/v3/objects/companies/batch/update", json={"inputs": updates}
        )

    def batch_update_contacts(self, updates: List[Dict[str, Any]]) -> Optional[Dict]:
        """
        Batch update contacts in HubSpot.

        Args:
            updates: List of dicts with 'id' and 'properties' keys
                    e.g., [{'id': '123', 'properties': {'firstname': 'John'}}]

        Returns:
            API response or None on failure
        """
        if not updates:
            return {"results": [], "status": "COMPLETE"}

        return self._make_request(
            "POST", "/crm/v3/objects/contacts/batch/update", json={"inputs": updates}
        )


# =============================================================================
# SQL Queries
# =============================================================================

FRED_DATA_EXTRACTION_QUERY = r"""
WITH base_data AS (
    SELECT
        r.id as rx_id,
        r.doctorid,
        r.officeid,
        rf.id as rxfill_id,
        rf.paymentid,
        rf.status,
        p.amount,
        s.id as shipmentid
    FROM rx r
    JOIN rxfill rf ON r.id = rf.rxid
    LEFT JOIN payment p ON p.id = rf.paymentid
    LEFT JOIN shipment s ON s.id = rf.shipmentid
    WHERE r.created >= CURRENT_DATE - INTERVAL '365 days'
),
office_metrics AS (
    SELECT
        officeid,
        COUNT(DISTINCT rx_id) as office_total_rx_created,
        COUNT(DISTINCT CASE WHEN paymentid IS NOT NULL THEN rx_id END) as office_total_rx_paid,
        COALESCE(SUM(CASE WHEN paymentid IS NOT NULL THEN cast(amount as numeric) END), 0) as office_total_rx_paid_amount,
        COUNT(DISTINCT CASE WHEN paymentid IS NULL THEN rx_id END) as office_total_rx_unpaid,
        COUNT(rxfill_id) as office_total_rx_fills_created,
        COUNT(CASE WHEN paymentid IS NOT NULL THEN rxfill_id END) as office_total_rx_fills_paid,
        COALESCE(SUM(CASE WHEN paymentid IS NOT NULL THEN cast(amount as numeric) END), 0) as office_total_rx_fills_paid_amount,
        COUNT(CASE WHEN paymentid IS NULL THEN rxfill_id END) as office_total_rx_fills_unpaid,
        COUNT(DISTINCT CASE WHEN shipmentid IS NOT NULL THEN rx_id END) as office_total_rx_shipped,
        COUNT(CASE WHEN status IN ('dispensedInOffice', 'verifyInOfficeDispenseNoLot', 'verifyInOfficeDispenseNoOffice') THEN rxfill_id END) as office_total_dios_created,
        COUNT(CASE WHEN status IN ('inFill', 'medNotFound', 'needsApproval', 'other', 'paymentHold', 'shipped', 'toFill', 'verifyQty') THEN rxfill_id END) as office_total_dtps_created,
        COUNT(CASE WHEN status IN ('inFill', 'medNotFound', 'needsApproval', 'other', 'paymentHold', 'shipped', 'toFill', 'verifyQty') AND paymentid IS NOT NULL AND paymentid != 0 THEN rxfill_id END) as office_total_dtps_paid,
        COUNT(CASE WHEN status IN ('inFill', 'medNotFound', 'needsApproval', 'other', 'paymentHold', 'shipped', 'toFill', 'verifyQty') AND (paymentid IS NULL OR paymentid = 0) THEN rxfill_id END) as office_total_dtps_unpaid
    FROM base_data
    GROUP BY officeid
),
prescriber_metrics AS (
    SELECT
        doctorid,
        COUNT(DISTINCT rx_id) as prescriber_total_rx_created,
        COUNT(DISTINCT CASE WHEN paymentid IS NOT NULL THEN rx_id END) as prescriber_total_rx_paid,
        COALESCE(SUM(CASE WHEN paymentid IS NOT NULL THEN cast(amount as numeric) END), 0) as prescriber_total_rx_paid_amount,
        COUNT(DISTINCT CASE WHEN paymentid IS NULL THEN rx_id END) as prescriber_total_rx_unpaid,
        COUNT(rxfill_id) as prescriber_total_rx_fills_created,
        COUNT(CASE WHEN paymentid IS NOT NULL THEN rxfill_id END) as prescriber_total_rx_fills_paid,
        COALESCE(SUM(CASE WHEN paymentid IS NOT NULL THEN cast(amount as numeric) END), 0) as prescriber_total_rx_fills_paid_amount,
        COUNT(CASE WHEN paymentid IS NULL THEN rxfill_id END) as prescriber_total_rx_fills_unpaid,
        COUNT(CASE WHEN status IN ('dispensedInOffice', 'verifyInOfficeDispenseNoLot', 'verifyInOfficeDispenseNoOffice') THEN rxfill_id END) as prescriber_total_dios_created,
        COUNT(CASE WHEN status IN ('inFill', 'medNotFound', 'needsApproval', 'other', 'paymentHold', 'shipped', 'toFill', 'verifyQty') THEN rxfill_id END) as prescriber_total_dtps_created,
        COUNT(CASE WHEN status IN ('inFill', 'medNotFound', 'needsApproval', 'other', 'paymentHold', 'shipped', 'toFill', 'verifyQty') AND paymentid IS NOT NULL AND paymentid != 0 THEN rxfill_id END) as prescriber_total_dtps_paid,
        COUNT(CASE WHEN status IN ('inFill', 'medNotFound', 'needsApproval', 'other', 'paymentHold', 'shipped', 'toFill', 'verifyQty') AND (paymentid IS NULL OR paymentid = 0) THEN rxfill_id END) as prescriber_total_dtps_unpaid
    FROM base_data
    GROUP BY doctorid
),
office_types AS (
    SELECT 
        o.id AS office_id,
        BOOL_OR(rf.status IN ('dispensedInOffice', 'verifyInOfficeDispenseNoLot')) AS has_dio,
        BOOL_OR(rf.status IN ('inFill', 'shipped', 'toFill')) AS has_dtp,
        BOOL_OR(r.virx = true) AS has_sknv_cloud
    FROM office o
    JOIN rx r ON r.officeid = o.id
    JOIN rxfill rf ON rf.rxid = r.id
    GROUP BY o.id
)
SELECT DISTINCT
    INITCAP(TRIM(REGEXP_REPLACE(trim(SPLIT_PART(d.name, ',', 1)), '^.*\s+(\S+)$', E'\\1'))) AS lastname,
    INITCAP(TRIM(REGEXP_REPLACE(trim(SPLIT_PART(d.name, ',', 1)), '\s+\S+$', ''))) AS firstname,
    d.phone,
    d.email,
    d.npi,
    o.id,
    o.name,
    a.address1,
    a.address2,
    a.city,
    a.state,
    a.zip,
    '' as office_phone,
    o.officeEmail,
    o.netsuiteId,
    users.email as salesconsultantEmail,
    CASE 
        WHEN ot.has_dio AND ot.has_dtp AND ot.has_sknv_cloud THEN 'DIO;DTP;SKNV Cloud'
        WHEN ot.has_dio AND ot.has_dtp THEN 'DIO;DTP'
        WHEN ot.has_dio AND ot.has_sknv_cloud THEN 'DIO;SKNV Cloud'
        WHEN ot.has_dtp AND ot.has_sknv_cloud THEN 'DTP;SKNV Cloud'
        WHEN ot.has_dio THEN 'DIO'
        WHEN ot.has_dtp THEN 'DTP'
        WHEN ot.has_sknv_cloud THEN 'SKNV Cloud'
        ELSE ''
    END AS inOfficeDispense,
    om.office_total_rx_shipped,
    o.suppressrefills as suppress_refills,
    om.office_total_rx_created,
    om.office_total_rx_paid,
    om.office_total_rx_paid_amount,
    om.office_total_rx_unpaid,
    om.office_total_rx_fills_created,
    om.office_total_rx_fills_paid,
    om.office_total_rx_fills_paid_amount,
    om.office_total_rx_fills_unpaid,
    om.office_total_dios_created,
    om.office_total_dtps_created,
    om.office_total_dtps_paid,
    om.office_total_dtps_unpaid,
    pm.prescriber_total_rx_created,
    pm.prescriber_total_rx_paid,
    pm.prescriber_total_rx_paid_amount,
    pm.prescriber_total_rx_unpaid,
    pm.prescriber_total_rx_fills_created,
    pm.prescriber_total_rx_fills_paid,
    pm.prescriber_total_rx_fills_paid_amount,
    pm.prescriber_total_rx_fills_unpaid,
    pm.prescriber_total_dios_created,
    pm.prescriber_total_dtps_created,
    pm.prescriber_total_dtps_paid,
    pm.prescriber_total_dtps_unpaid
FROM base_data bd
JOIN doctor d ON d.id = bd.doctorid
JOIN office o ON o.id = bd.officeid
JOIN office_metrics om ON om.officeid = bd.officeid
JOIN prescriber_metrics pm ON pm.doctorid = bd.doctorid
JOIN address a ON a.id = o.addressid
LEFT JOIN office_types ot ON ot.office_id = o.id
LEFT JOIN users ON users.id = replace(replace(o.sales, '[', ''), ']', '')::INTEGER
ORDER BY o.name, lastname, firstname
"""


# =============================================================================
# Data Comparison Classes
# =============================================================================


@dataclass
class ComparisonResult:
    """Result of comparing Fred vs HubSpot data"""

    companies_to_add: List[Dict] = field(default_factory=list)
    companies_to_update: List[Dict] = field(default_factory=list)
    contacts_to_add: List[Dict] = field(default_factory=list)
    contacts_to_update: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "companies_to_add": len(self.companies_to_add),
            "companies_to_update": len(self.companies_to_update),
            "contacts_to_add": len(self.contacts_to_add),
            "contacts_to_update": len(self.contacts_to_update),
            "total_actions": self.total_actions(),
        }

    def total_actions(self) -> int:
        return (
            len(self.companies_to_add)
            + len(self.companies_to_update)
            + len(self.contacts_to_add)
            + len(self.contacts_to_update)
        )


# =============================================================================
# Helper Functions for Data Processing
# =============================================================================


def safe_int(value) -> Optional[int]:
    """Safely convert value to int"""
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def safe_float(value) -> Optional[float]:
    """Safely convert value to float"""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_bool(value) -> Optional[bool]:
    """Safely convert value to bool"""
    if value is None or value == "":
        return None
    return str(value).lower() in ("true", "t", "yes", "1")


def clean_npi(npi: str) -> Optional[str]:
    """Clean and validate NPI number (must be 10 digits)"""
    if not npi or npi == "0000":
        return None

    npi_clean = npi.strip()
    if npi_clean.upper().startswith("NPI "):
        npi_clean = npi_clean[4:].strip()

    npi_clean = npi_clean.replace(" ", "").replace("-", "")

    if npi_clean.isdigit() and len(npi_clean) == 10:
        return npi_clean

    return None


def values_match(val1, val2, tolerance: float = 0.01) -> bool:
    """Check if two numeric values match within tolerance"""
    if val1 is None and val2 is None:
        return True
    if val1 is None or val2 is None:
        return False

    try:
        v1 = float(val1)
        v2 = float(val2)
    except (ValueError, TypeError):
        return False

    if v1 == 0 and v2 == 0:
        return True
    if v1 == 0 or v2 == 0:
        return abs(v1 - v2) < 0.01

    diff_pct = abs(v1 - v2) / max(abs(v1), abs(v2))
    return diff_pct <= tolerance


# =============================================================================
# Celery Tasks - Data Extraction
# =============================================================================


@shared_task(bind=True, max_retries=3, default_retry_delay=600)
def extract_fred_data(self) -> Dict[str, Any]:
    """
    Extract Fred data into hubspot.fred_data table.

    This task extracts production data from Fred database tables and inserts
    aggregated metrics into the hubspot.fred_data comparison table.
    """
    task_name = "extract_fred_data"
    start_time = time.time()

    try:
        logger.info(f"Starting Fred data extraction at {timezone.now()}")

        with connections["fred"].cursor() as cursor:
            with transaction.atomic(using="fred"):
                logger.info("Truncating existing hubspot.fred_data...")
                cursor.execute("TRUNCATE TABLE hubspot.fred_data")

                logger.info("Executing extraction query...")
                insert_sql = f"""
                INSERT INTO hubspot.fred_data (
                    lastname, firstname, phone, email, npi,
                    office_id, office_name, address1, address2, city, state, zip,
                    office_phone, office_email, netsuite_id, salesconsultant_email,
                    in_office_dispense, office_total_rx_shipped, suppress_refills,
                    office_total_rx_created, office_total_rx_paid, office_total_rx_paid_amount,
                    office_total_rx_unpaid, office_total_rx_fills_created, office_total_rx_fills_paid,
                    office_total_rx_fills_paid_amount, office_total_rx_fills_unpaid,
                    office_total_dios_created, office_total_dtps_created,
                    office_total_dtps_paid, office_total_dtps_unpaid,   
                    prescriber_total_rx_created, prescriber_total_rx_paid, prescriber_total_rx_paid_amount,
                    prescriber_total_rx_unpaid, prescriber_total_rx_fills_created, prescriber_total_rx_fills_paid,
                    prescriber_total_rx_fills_paid_amount, prescriber_total_rx_fills_unpaid,
                    prescriber_total_dios_created, prescriber_total_dtps_created,
                    prescriber_total_dtps_paid, prescriber_total_dtps_unpaid  
                )
                {FRED_DATA_EXTRACTION_QUERY}
                """
                cursor.execute(insert_sql)
                rows_inserted = cursor.rowcount
                logger.info(f"Inserted {rows_inserted} rows into hubspot.fred_data")

            # Get summary stats
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_rows,
                    COUNT(DISTINCT office_id) as unique_offices,
                    COUNT(DISTINCT npi) as unique_prescribers
                FROM hubspot.fred_data
            """
            )
            stats = cursor.fetchone()

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            "rows_inserted": rows_inserted,
            "unique_offices": stats[1],
            "unique_prescribers": stats[2],
            "duration_seconds": duration,
            "status": "success",
        }

        track_task_metrics(
            task_name, "success", duration, rows_inserted, "fred_records"
        )
        logger.info(f"Fred data extraction completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in extract_fred_data: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def export_hubspot_contacts(self) -> Dict[str, Any]:
    """
    Fetch all contacts from HubSpot API and store in database.
    """
    task_name = "export_hubspot_contacts"
    start_time = time.time()

    try:
        logger.info("Fetching contacts from HubSpot...")
        client = HubSpotAPIClient()
        contacts = client.get_all_contacts()

        logger.info(f"Fetched {len(contacts)} contacts, storing in database...")

        with connections["fred"].cursor() as cursor:
            cursor.execute("TRUNCATE TABLE hubspot.contacts")

            for contact in contacts:
                props = contact.get("properties", {})
                cursor.execute(
                    """
                    INSERT INTO hubspot.contacts (
                        id, firstname, lastname, phone, email, npi_number,
                        total_rx_created, total_rx_paid, total_rx_paid_amount,
                        total_rx_unpaid, total_rx_fills_created, total_rx_fills_paid,
                        total_rx_fills_paid_amount, total_rx_fills_unpaid,
                        total_dios_created, total_dtps_created, total_dtps_paid, total_dtps_unpaid
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    [
                        contact["id"],
                        props.get("firstname"),
                        props.get("lastname"),
                        props.get("phone"),
                        props.get("email"),
                        props.get("npi_number"),
                        safe_int(props.get("total_rx_created")),
                        safe_int(props.get("total_rx_paid")),
                        safe_float(props.get("total_rx_paid_amount")),
                        safe_int(props.get("total_rx_unpaid")),
                        safe_int(props.get("total_rx_fills_created")),
                        safe_int(props.get("total_rx_fills_paid")),
                        safe_float(props.get("total_rx_fills_paid_amount")),
                        safe_int(props.get("total_rx_fills_unpaid")),
                        safe_int(props.get("total_dios_created")),
                        safe_int(props.get("total_dtps_created")),
                        safe_int(props.get("total_dtps_paid")),
                        safe_int(props.get("total_dtps_unpaid")),
                    ],
                )

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            "contacts_exported": len(contacts),
            "duration_seconds": duration,
            "status": "success",
        }

        track_task_metrics(task_name, "success", duration, len(contacts), "contacts")
        logger.info(f"HubSpot contacts export completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in export_hubspot_contacts: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def export_hubspot_companies(self) -> Dict[str, Any]:
    """
    Fetch all companies from HubSpot API and store in database.
    """
    task_name = "export_hubspot_companies"
    start_time = time.time()

    try:
        logger.info("Fetching companies from HubSpot...")
        client = HubSpotAPIClient()
        companies = client.get_all_companies()

        logger.info(f"Fetched {len(companies)} companies, storing in database...")

        with connections["fred"].cursor() as cursor:
            cursor.execute("TRUNCATE TABLE hubspot.companies")

            for company in companies:
                props = company.get("properties", {})
                cursor.execute(
                    """
                    INSERT INTO hubspot.companies (
                        id, fred_id, name, address, address2, city, state_abbreviation, zip,
                        phone, company_email, new_netsuite_id, hubspot_owner_id, company_type,
                        rx_total_shipments, suppress_refill_notifications,
                        total_rx_created, total_rx_paid, total_rx_paid_amount,
                        total_rx_unpaid, total_rx_fills_created, total_rx_fills_paid,
                        total_rx_fills_paid_amount, total_rx_fills_unpaid,
                        total_dios_created, total_dtps_created, total_dtps_paid, total_dtps_unpaid
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    [
                        company["id"],
                        props.get("fred_id"),
                        props.get("name"),
                        props.get("address"),
                        props.get("address2"),
                        props.get("city"),
                        props.get("state_abbreviation"),
                        props.get("zip"),
                        props.get("phone"),
                        props.get("company_email"),
                        props.get("new_netsuite_id"),
                        safe_int(props.get("hubspot_owner_id")),
                        props.get("company_type"),
                        safe_int(props.get("rx_total_shipments")),
                        safe_bool(props.get("suppress_refill_notifications")),
                        safe_int(props.get("total_rx_created")),
                        safe_int(props.get("total_rx_paid")),
                        safe_float(props.get("total_rx_paid_amount")),
                        safe_int(props.get("total_rx_unpaid")),
                        safe_int(props.get("total_rx_fills_created")),
                        safe_int(props.get("total_rx_fills_paid")),
                        safe_float(props.get("total_rx_fills_paid_amount")),
                        safe_int(props.get("total_rx_fills_unpaid")),
                        safe_int(props.get("total_dios_created")),
                        safe_int(props.get("total_dtps_created")),
                        safe_int(props.get("total_dtps_paid")),
                        safe_int(props.get("total_dtps_unpaid")),
                    ],
                )

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            "companies_exported": len(companies),
            "duration_seconds": duration,
            "status": "success",
        }

        track_task_metrics(task_name, "success", duration, len(companies), "companies")
        logger.info(f"HubSpot companies export completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in export_hubspot_companies: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def export_hubspot_owners(self) -> Dict[str, Any]:
    """
    Fetch all owners from HubSpot API and store in database.
    """
    task_name = "export_hubspot_owners"
    start_time = time.time()

    try:
        logger.info("Fetching owners from HubSpot...")
        client = HubSpotAPIClient()
        owners = client.get_all_owners()

        logger.info(f"Fetched {len(owners)} owners, storing in database...")

        with connections["fred"].cursor() as cursor:
            cursor.execute("TRUNCATE TABLE hubspot.owners")

            for owner in owners:
                cursor.execute(
                    """
                    INSERT INTO hubspot.owners (id, email, first_name, last_name, user_id)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    [
                        owner["id"],
                        owner.get("email"),
                        owner.get("firstName"),
                        owner.get("lastName"),
                        safe_int(owner.get("userId")),
                    ],
                )

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            "owners_exported": len(owners),
            "duration_seconds": duration,
            "status": "success",
        }

        track_task_metrics(task_name, "success", duration, len(owners), "owners")
        logger.info(f"HubSpot owners export completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in export_hubspot_owners: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


# =============================================================================
# Celery Tasks - Comparison
# =============================================================================


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def compare_fred_hubspot(self, tolerance: float = 0.0) -> Dict[str, Any]:
    """
    Compare Fred vs HubSpot data and identify changes needed.

    Returns summary of companies/contacts to add/update.
    """
    task_name = "compare_fred_hubspot"
    start_time = time.time()

    try:
        logger.info("Starting Fred vs HubSpot comparison...")
        result = ComparisonResult()

        with connections["fred"].cursor() as cursor:
            # Find companies to ADD (in Fred but not in HubSpot)
            logger.info("Finding companies to add...")
            cursor.execute(
                """
                SELECT DISTINCT
                    f.office_id, f.office_name, f.netsuite_id, f.address1, f.address2,
                    f.city, f.state, f.zip, f.office_phone, f.office_email,
                    f.salesconsultant_email, o.id as hubspot_owner_id, f.in_office_dispense,
                    f.office_total_rx_shipped, f.suppress_refills,
                    f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                    f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                    f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                    f.office_total_dios_created, f.office_total_dtps_created,
                    f.office_total_dtps_paid, f.office_total_dtps_unpaid
                FROM hubspot.fred_data f
                LEFT JOIN hubspot.companies h1 ON CAST(h1.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
                LEFT JOIN hubspot.companies h2 ON h2.new_netsuite_id = f.netsuite_id
                LEFT JOIN hubspot.owners o ON LOWER(TRIM(o.email)) = LOWER(TRIM(f.salesconsultant_email))
                WHERE h1.id IS NULL AND h2.id IS NULL
            """
            )

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                result.companies_to_add.append(dict(zip(columns, row)))

            logger.info(f"Found {len(result.companies_to_add)} companies to add")

            # Find companies to UPDATE
            logger.info("Finding companies to update...")
            cursor.execute(
                """
                SELECT 
                    h.id as hubspot_id, h.name as hubspot_name, h.fred_id, f.office_id,
                    f.office_total_rx_shipped, f.suppress_refills,
                    f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                    f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                    f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                    f.office_total_dios_created, f.office_total_dtps_created,
                    f.office_total_dtps_paid, f.office_total_dtps_unpaid,
                    h.rx_total_shipments, h.suppress_refill_notifications,
                    h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                    h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                    h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                    h.total_dios_created, h.total_dtps_created,
                    h.total_dtps_paid, h.total_dtps_unpaid
                FROM hubspot.companies h
                JOIN hubspot.fred_data f ON CAST(h.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
                WHERE h.fred_id IS NOT NULL AND h.fred_id != ''
            """
            )

            for row in cursor.fetchall():
                updates = {}
                # Compare metrics (Fred values are indices 4-17, HubSpot are 18-31)
                metric_pairs = [
                    ("rx_total_shipments", row[4], row[18]),
                    ("suppress_refill_notifications", row[5], row[19]),
                    ("total_rx_created", row[6], row[20]),
                    ("total_rx_paid", row[7], row[21]),
                    ("total_rx_paid_amount", row[8], row[22]),
                    ("total_rx_unpaid", row[9], row[23]),
                    ("total_rx_fills_created", row[10], row[24]),
                    ("total_rx_fills_paid", row[11], row[25]),
                    ("total_rx_fills_paid_amount", row[12], row[26]),
                    ("total_rx_fills_unpaid", row[13], row[27]),
                    ("total_dios_created", row[14], row[28]),
                    ("total_dtps_created", row[15], row[29]),
                    ("total_dtps_paid", row[16], row[30]),
                    ("total_dtps_unpaid", row[17], row[31]),
                ]

                for field_name, fred_val, hubspot_val in metric_pairs:
                    if not values_match(hubspot_val, fred_val, tolerance):
                        updates[field_name] = convert_for_json(fred_val)

                if updates:
                    result.companies_to_update.append(
                        {
                            "hubspot_id": row[0],
                            "hubspot_name": row[1],
                            "fred_id": row[2],
                            **updates,
                        }
                    )

            logger.info(f"Found {len(result.companies_to_update)} companies to update")

            # Find contacts to ADD
            logger.info("Finding contacts to add...")
            cursor.execute(
                """
                SELECT DISTINCT
                    f.firstname, f.lastname, f.phone, f.email, f.npi, f.office_id,
                    f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                    f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                    f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                    f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                    f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                    f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid
                FROM hubspot.fred_data f
                LEFT JOIN hubspot.contacts h ON f.npi = h.npi_number
                WHERE h.id IS NULL
                AND f.npi IS NOT NULL AND f.npi != ''
                AND LENGTH(f.npi) = 10
            """
            )

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                result.contacts_to_add.append(dict(zip(columns, row)))

            logger.info(f"Found {len(result.contacts_to_add)} contacts to add")

            # Find contacts to UPDATE
            logger.info("Finding contacts to update...")
            cursor.execute(
                """
                SELECT 
                    h.id as hubspot_id, h.firstname, h.lastname, h.npi_number,
                    f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                    f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                    f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                    f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                    f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                    f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid,
                    h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                    h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                    h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                    h.total_dios_created, h.total_dtps_created,
                    h.total_dtps_paid, h.total_dtps_unpaid
                FROM hubspot.contacts h
                JOIN hubspot.fred_data f ON f.npi = h.npi_number
                WHERE h.npi_number IS NOT NULL AND h.npi_number != ''
            """
            )

            for row in cursor.fetchall():
                updates = {}
                metric_pairs = [
                    ("total_rx_created", row[4], row[16]),
                    ("total_rx_paid", row[5], row[17]),
                    ("total_rx_paid_amount", row[6], row[18]),
                    ("total_rx_unpaid", row[7], row[19]),
                    ("total_rx_fills_created", row[8], row[20]),
                    ("total_rx_fills_paid", row[9], row[21]),
                    ("total_rx_fills_paid_amount", row[10], row[22]),
                    ("total_rx_fills_unpaid", row[11], row[23]),
                    ("total_dios_created", row[12], row[24]),
                    ("total_dtps_created", row[13], row[25]),
                    ("total_dtps_paid", row[14], row[26]),
                    ("total_dtps_unpaid", row[15], row[27]),
                ]

                for field_name, fred_val, hubspot_val in metric_pairs:
                    if not values_match(hubspot_val, fred_val, tolerance):
                        updates[field_name] = convert_for_json(fred_val)

                if updates:
                    result.contacts_to_update.append(
                        {
                            "hubspot_id": row[0],
                            "hubspot_name": f"{row[1] or ''} {row[2] or ''}".strip(),
                            "npi": row[3],
                            **updates,
                        }
                    )

            logger.info(f"Found {len(result.contacts_to_update)} contacts to update")

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            **result.to_dict(),
            "duration_seconds": duration,
            "status": "success",
        }

        track_task_metrics(task_name, "success", duration)
        logger.info(f"Comparison completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in compare_fred_hubspot: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


# =============================================================================
# Celery Tasks - Create/Update HubSpot Records
# =============================================================================


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def create_hubspot_companies(self, dry_run: bool = False) -> Dict[str, Any]:
    """
    Create new companies in HubSpot from comparison results.
    """
    task_name = "create_hubspot_companies"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0}

    try:
        logger.info(f"Creating companies in HubSpot (dry_run={dry_run})...")
        client = HubSpotAPIClient()

        # Get companies to add from comparison results
        with connections["fred"].cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT
                    f.office_id, f.office_name, f.netsuite_id, f.address1, f.address2,
                    f.city, f.state, f.zip, f.office_phone, f.office_email,
                    o.id as hubspot_owner_id, f.in_office_dispense,
                    f.office_total_rx_shipped, f.suppress_refills,
                    f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                    f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                    f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                    f.office_total_dios_created, f.office_total_dtps_created,
                    f.office_total_dtps_paid, f.office_total_dtps_unpaid
                FROM hubspot.fred_data f
                LEFT JOIN hubspot.companies h1 ON CAST(h1.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
                LEFT JOIN hubspot.companies h2 ON h2.new_netsuite_id = f.netsuite_id
                LEFT JOIN hubspot.owners o ON LOWER(TRIM(o.email)) = LOWER(TRIM(f.salesconsultant_email))
                WHERE h1.id IS NULL AND h2.id IS NULL
            """
            )

            companies_to_add = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        logger.info(f"Processing {len(companies_to_add)} companies...")

        for row in companies_to_add:
            company = dict(zip(columns, row))
            office_id = company["office_id"]
            office_name = company["office_name"]
            hubspot_owner_id = company.get("hubspot_owner_id")

            if not hubspot_owner_id:
                logger.warning(f"Skipping {office_name} - no hubspot_owner_id")
                results["skipped"] += 1
                continue

            properties = {
                "name": office_name,
                "fred_id": str(office_id),
                "new_netsuite_id": company.get("netsuite_id") or "",
                "address": company.get("address1") or "",
                "address2": company.get("address2") or "",
                "city": company.get("city") or "",
                "state_abbreviation": company.get("state") or "",
                "zip": company.get("zip") or "",
                "phone": company.get("office_phone") or "",
                "company_email": company.get("office_email") or "",
                "hubspot_owner_id": hubspot_owner_id,
                "company_type": company.get("in_office_dispense") or "",
                "rx_total_shipments": safe_int(company.get("office_total_rx_shipped")),
                "suppress_refill_notifications": (
                    "TRUE" if company.get("suppress_refills") else "FALSE"
                ),
                "total_rx_created": safe_int(company.get("office_total_rx_created")),
                "total_rx_paid": safe_int(company.get("office_total_rx_paid")),
                "total_rx_paid_amount": safe_float(
                    company.get("office_total_rx_paid_amount")
                ),
                "total_rx_unpaid": safe_int(company.get("office_total_rx_unpaid")),
                "total_rx_fills_created": safe_int(
                    company.get("office_total_rx_fills_created")
                ),
                "total_rx_fills_paid": safe_int(
                    company.get("office_total_rx_fills_paid")
                ),
                "total_rx_fills_paid_amount": safe_float(
                    company.get("office_total_rx_fills_paid_amount")
                ),
                "total_rx_fills_unpaid": safe_int(
                    company.get("office_total_rx_fills_unpaid")
                ),
                "total_dios_created": safe_int(
                    company.get("office_total_dios_created")
                ),
                "total_dtps_created": safe_int(
                    company.get("office_total_dtps_created")
                ),
                "total_dtps_paid": safe_int(company.get("office_total_dtps_paid")),
                "total_dtps_unpaid": safe_int(company.get("office_total_dtps_unpaid")),
            }

            # Remove None values
            properties = {
                k: v for k, v in properties.items() if v is not None and v != ""
            }

            if dry_run:
                logger.info(f"[DRY RUN] Would create company: {office_name}")
                results["success"] += 1
            else:
                response = client.create_company(properties)
                if response:
                    logger.info(
                        f"Created company: {office_name} (ID: {response.get('id')})"
                    )
                    results["success"] += 1
                else:
                    logger.error(f"Failed to create company: {office_name}")
                    results["failed"] += 1

                time.sleep(0.5)  # Rate limiting

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            **results,
            "total_processed": len(companies_to_add),
            "duration_seconds": duration,
            "dry_run": dry_run,
            "status": "success",
        }

        track_task_metrics(
            task_name, "success", duration, results["success"], "companies_created"
        )
        logger.info(f"Create companies completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in create_hubspot_companies: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def create_hubspot_contacts(
    self, dry_run: bool = False, associate_with_company: bool = True
) -> Dict[str, Any]:
    """
    Create new contacts in HubSpot from comparison results.
    """
    task_name = "create_hubspot_contacts"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0}

    try:
        logger.info(f"Creating contacts in HubSpot (dry_run={dry_run})...")
        client = HubSpotAPIClient()

        # Get contacts to add
        with connections["fred"].cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT
                    f.firstname, f.lastname, f.phone, f.email, f.npi, f.office_id,
                    f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                    f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                    f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                    f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                    f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                    f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid
                FROM hubspot.fred_data f
                LEFT JOIN hubspot.contacts h ON f.npi = h.npi_number
                WHERE h.id IS NULL
                AND f.npi IS NOT NULL AND f.npi != ''
                AND LENGTH(f.npi) = 10
            """
            )

            contacts_to_add = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

        logger.info(f"Processing {len(contacts_to_add)} contacts...")

        for row in contacts_to_add:
            contact = dict(zip(columns, row))
            npi = contact["npi"]
            contact_name = f"{contact.get('firstname') or ''} {contact.get('lastname') or ''}".strip()

            cleaned_npi = clean_npi(npi)
            if not cleaned_npi:
                logger.warning(f"Skipping {contact_name} - invalid NPI: {npi}")
                results["skipped"] += 1
                continue

            properties = {
                "firstname": contact.get("firstname") or "",
                "lastname": contact.get("lastname") or "",
                "email": contact.get("email") or "",
                "phone": contact.get("phone") or "",
                "npi_number": cleaned_npi,
                "total_rx_created": safe_int(
                    contact.get("prescriber_total_rx_created")
                ),
                "total_rx_paid": safe_int(contact.get("prescriber_total_rx_paid")),
                "total_rx_paid_amount": safe_float(
                    contact.get("prescriber_total_rx_paid_amount")
                ),
                "total_rx_unpaid": safe_int(contact.get("prescriber_total_rx_unpaid")),
                "total_rx_fills_created": safe_int(
                    contact.get("prescriber_total_rx_fills_created")
                ),
                "total_rx_fills_paid": safe_int(
                    contact.get("prescriber_total_rx_fills_paid")
                ),
                "total_rx_fills_paid_amount": safe_float(
                    contact.get("prescriber_total_rx_fills_paid_amount")
                ),
                "total_rx_fills_unpaid": safe_int(
                    contact.get("prescriber_total_rx_fills_unpaid")
                ),
                "total_dios_created": safe_int(
                    contact.get("prescriber_total_dios_created")
                ),
                "total_dtps_created": safe_int(
                    contact.get("prescriber_total_dtps_created")
                ),
                "total_dtps_paid": safe_int(contact.get("prescriber_total_dtps_paid")),
                "total_dtps_unpaid": safe_int(
                    contact.get("prescriber_total_dtps_unpaid")
                ),
            }

            properties = {
                k: v for k, v in properties.items() if v is not None and v != ""
            }

            if dry_run:
                logger.info(f"[DRY RUN] Would create contact: {contact_name}")
                results["success"] += 1
            else:
                response = client.create_contact(properties)
                if response:
                    contact_id = response.get("id")
                    logger.info(f"Created contact: {contact_name} (ID: {contact_id})")

                    # Associate with company if requested
                    if associate_with_company and contact.get("office_id"):
                        company = client.search_company_by_fred_id(
                            str(contact["office_id"])
                        )
                        if company:
                            client.associate_contact_to_company(
                                contact_id, company["id"]
                            )
                            logger.info(
                                f"Associated contact {contact_id} with company {company['id']}"
                            )

                    results["success"] += 1
                else:
                    logger.error(f"Failed to create contact: {contact_name}")
                    results["failed"] += 1

                time.sleep(0.5)

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            **results,
            "total_processed": len(contacts_to_add),
            "duration_seconds": duration,
            "dry_run": dry_run,
            "status": "success",
        }

        track_task_metrics(
            task_name, "success", duration, results["success"], "contacts_created"
        )
        logger.info(f"Create contacts completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in create_hubspot_contacts: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def update_hubspot_companies(self, dry_run: bool = False) -> Dict[str, Any]:
    """
    Update existing companies in HubSpot with changed metrics.
    """
    task_name = "update_hubspot_companies"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0}

    try:
        logger.info(f"Updating companies in HubSpot (dry_run={dry_run})...")
        client = HubSpotAPIClient()

        # Get companies needing updates
        with connections["fred"].cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    h.id as hubspot_id, h.name as hubspot_name, h.fred_id,
                    f.office_total_rx_shipped, f.suppress_refills,
                    f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                    f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                    f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                    f.office_total_dios_created, f.office_total_dtps_created,
                    f.office_total_dtps_paid, f.office_total_dtps_unpaid,
                    h.rx_total_shipments, h.suppress_refill_notifications,
                    h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                    h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                    h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                    h.total_dios_created, h.total_dtps_created,
                    h.total_dtps_paid, h.total_dtps_unpaid
                FROM hubspot.companies h
                JOIN hubspot.fred_data f ON CAST(h.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
                WHERE h.fred_id IS NOT NULL AND h.fred_id != ''
            """
            )

            companies = cursor.fetchall()

        logger.info(f"Checking {len(companies)} companies for updates...")

        for row in companies:
            hubspot_id = row[0]
            hubspot_name = row[1]

            updates = {}
            metric_pairs = [
                ("rx_total_shipments", row[3], row[17]),
                (
                    "suppress_refill_notifications",
                    "TRUE" if row[4] else "FALSE",
                    "TRUE" if row[18] else "FALSE",
                ),
                ("total_rx_created", row[5], row[19]),
                ("total_rx_paid", row[6], row[20]),
                ("total_rx_paid_amount", row[7], row[21]),
                ("total_rx_unpaid", row[8], row[22]),
                ("total_rx_fills_created", row[9], row[23]),
                ("total_rx_fills_paid", row[10], row[24]),
                ("total_rx_fills_paid_amount", row[11], row[25]),
                ("total_rx_fills_unpaid", row[12], row[26]),
                ("total_dios_created", row[13], row[27]),
                ("total_dtps_created", row[14], row[28]),
                ("total_dtps_paid", row[15], row[29]),
                ("total_dtps_unpaid", row[16], row[30]),
            ]

            for field_name, fred_val, hubspot_val in metric_pairs:
                if field_name == "suppress_refill_notifications":
                    if fred_val != hubspot_val:
                        updates[field_name] = fred_val
                elif not values_match(hubspot_val, fred_val):
                    updates[field_name] = convert_for_json(fred_val)

            if not updates:
                continue

            if dry_run:
                logger.info(
                    f"[DRY RUN] Would update company {hubspot_name}: {list(updates.keys())}"
                )
                results["success"] += 1
            else:
                response = client.update_company(hubspot_id, updates)
                if response:
                    logger.info(f"Updated company: {hubspot_name}")
                    results["success"] += 1
                else:
                    logger.error(f"Failed to update company: {hubspot_name}")
                    results["failed"] += 1

                time.sleep(0.3)

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            **results,
            "total_checked": len(companies),
            "duration_seconds": duration,
            "dry_run": dry_run,
            "status": "success",
        }

        track_task_metrics(
            task_name, "success", duration, results["success"], "companies_updated"
        )
        logger.info(f"Update companies completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in update_hubspot_companies: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


@shared_task(bind=True, max_retries=2, default_retry_delay=600)
def update_hubspot_contacts(self, dry_run: bool = False) -> Dict[str, Any]:
    """
    Update existing contacts in HubSpot with changed metrics.
    """
    task_name = "update_hubspot_contacts"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0}

    try:
        logger.info(f"Updating contacts in HubSpot (dry_run={dry_run})...")
        client = HubSpotAPIClient()

        # Get contacts needing updates
        with connections["fred"].cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    h.id as hubspot_id, h.firstname, h.lastname, h.npi_number,
                    f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                    f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                    f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                    f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                    f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                    f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid,
                    h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                    h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                    h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                    h.total_dios_created, h.total_dtps_created,
                    h.total_dtps_paid, h.total_dtps_unpaid
                FROM hubspot.contacts h
                JOIN hubspot.fred_data f ON f.npi = h.npi_number
                WHERE h.npi_number IS NOT NULL AND h.npi_number != ''
            """
            )

            contacts = cursor.fetchall()

        logger.info(f"Checking {len(contacts)} contacts for updates...")

        for row in contacts:
            hubspot_id = row[0]
            contact_name = f"{row[1] or ''} {row[2] or ''}".strip()

            updates = {}
            metric_pairs = [
                ("total_rx_created", row[4], row[16]),
                ("total_rx_paid", row[5], row[17]),
                ("total_rx_paid_amount", row[6], row[18]),
                ("total_rx_unpaid", row[7], row[19]),
                ("total_rx_fills_created", row[8], row[20]),
                ("total_rx_fills_paid", row[9], row[21]),
                ("total_rx_fills_paid_amount", row[10], row[22]),
                ("total_rx_fills_unpaid", row[11], row[23]),
                ("total_dios_created", row[12], row[24]),
                ("total_dtps_created", row[13], row[25]),
                ("total_dtps_paid", row[14], row[26]),
                ("total_dtps_unpaid", row[15], row[27]),
            ]

            for field_name, fred_val, hubspot_val in metric_pairs:
                if not values_match(hubspot_val, fred_val):
                    updates[field_name] = convert_for_json(fred_val)

            if not updates:
                continue

            if dry_run:
                logger.info(
                    f"[DRY RUN] Would update contact {contact_name}: {list(updates.keys())}"
                )
                results["success"] += 1
            else:
                response = client.update_contact(hubspot_id, updates)
                if response:
                    logger.info(f"Updated contact: {contact_name}")
                    results["success"] += 1
                else:
                    logger.error(f"Failed to update contact: {contact_name}")
                    results["failed"] += 1

                time.sleep(0.3)

        duration = time.time() - start_time
        summary = {
            "task_id": self.request.id,
            **results,
            "total_checked": len(contacts),
            "duration_seconds": duration,
            "dry_run": dry_run,
            "status": "success",
        }

        track_task_metrics(
            task_name, "success", duration, results["success"], "contacts_updated"
        )
        logger.info(f"Update contacts completed: {summary}")
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Error in update_hubspot_contacts: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise


# =============================================================================
# Pipeline Step Functions (non-task versions for synchronous execution)
# =============================================================================


def _run_extract_fred_data() -> Dict[str, Any]:
    """Extract Fred data - synchronous version for pipeline use."""
    task_name = "extract_fred_data"
    start_time = time.time()

    logger.info(f"Starting Fred data extraction at {timezone.now()}")

    with connections["fred"].cursor() as cursor:
        with transaction.atomic(using="fred"):
            logger.info("Truncating existing hubspot.fred_data...")
            cursor.execute("TRUNCATE TABLE hubspot.fred_data")

            logger.info("Executing extraction query...")
            insert_sql = f"""
            INSERT INTO hubspot.fred_data (
                lastname, firstname, phone, email, npi,
                office_id, office_name, address1, address2, city, state, zip,
                office_phone, office_email, netsuite_id, salesconsultant_email,
                in_office_dispense, office_total_rx_shipped, suppress_refills,
                office_total_rx_created, office_total_rx_paid, office_total_rx_paid_amount,
                office_total_rx_unpaid, office_total_rx_fills_created, office_total_rx_fills_paid,
                office_total_rx_fills_paid_amount, office_total_rx_fills_unpaid,
                office_total_dios_created, office_total_dtps_created,
                office_total_dtps_paid, office_total_dtps_unpaid,   
                prescriber_total_rx_created, prescriber_total_rx_paid, prescriber_total_rx_paid_amount,
                prescriber_total_rx_unpaid, prescriber_total_rx_fills_created, prescriber_total_rx_fills_paid,
                prescriber_total_rx_fills_paid_amount, prescriber_total_rx_fills_unpaid,
                prescriber_total_dios_created, prescriber_total_dtps_created,
                prescriber_total_dtps_paid, prescriber_total_dtps_unpaid  
            )
            {FRED_DATA_EXTRACTION_QUERY}
            """
            cursor.execute(insert_sql)
            rows_inserted = cursor.rowcount
            logger.info(f"Inserted {rows_inserted} rows into hubspot.fred_data")

        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_rows,
                COUNT(DISTINCT office_id) as unique_offices,
                COUNT(DISTINCT npi) as unique_prescribers
            FROM hubspot.fred_data
        """
        )
        stats = cursor.fetchone()

    duration = time.time() - start_time
    summary = {
        "rows_inserted": rows_inserted,
        "unique_offices": stats[1],
        "unique_prescribers": stats[2],
        "duration_seconds": duration,
        "status": "success",
    }

    track_task_metrics(task_name, "success", duration, rows_inserted, "fred_records")
    logger.info(f"Fred data extraction completed: {summary}")
    return summary


def _run_export_hubspot_contacts() -> Dict[str, Any]:
    """Export HubSpot contacts - synchronous version for pipeline use."""
    task_name = "export_hubspot_contacts"
    start_time = time.time()

    logger.info("Fetching contacts from HubSpot...")
    client = HubSpotAPIClient()
    contacts = client.get_all_contacts()

    logger.info(f"Fetched {len(contacts)} contacts, storing in database...")

    with connections["fred"].cursor() as cursor:
        cursor.execute("TRUNCATE TABLE hubspot.contacts")

        for contact in contacts:
            props = contact.get("properties", {})
            cursor.execute(
                """
                INSERT INTO hubspot.contacts (
                    id, firstname, lastname, phone, email, npi_number,
                    total_rx_created, total_rx_paid, total_rx_paid_amount,
                    total_rx_unpaid, total_rx_fills_created, total_rx_fills_paid,
                    total_rx_fills_paid_amount, total_rx_fills_unpaid,
                    total_dios_created, total_dtps_created, total_dtps_paid, total_dtps_unpaid
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                [
                    contact["id"],
                    props.get("firstname"),
                    props.get("lastname"),
                    props.get("phone"),
                    props.get("email"),
                    props.get("npi_number"),
                    safe_int(props.get("total_rx_created")),
                    safe_int(props.get("total_rx_paid")),
                    safe_float(props.get("total_rx_paid_amount")),
                    safe_int(props.get("total_rx_unpaid")),
                    safe_int(props.get("total_rx_fills_created")),
                    safe_int(props.get("total_rx_fills_paid")),
                    safe_float(props.get("total_rx_fills_paid_amount")),
                    safe_int(props.get("total_rx_fills_unpaid")),
                    safe_int(props.get("total_dios_created")),
                    safe_int(props.get("total_dtps_created")),
                    safe_int(props.get("total_dtps_paid")),
                    safe_int(props.get("total_dtps_unpaid")),
                ],
            )

    duration = time.time() - start_time
    summary = {
        "contacts_exported": len(contacts),
        "duration_seconds": duration,
        "status": "success",
    }

    track_task_metrics(task_name, "success", duration, len(contacts), "contacts")
    logger.info(f"HubSpot contacts export completed: {summary}")
    return summary


def _run_export_hubspot_companies() -> Dict[str, Any]:
    """Export HubSpot companies - synchronous version for pipeline use."""
    task_name = "export_hubspot_companies"
    start_time = time.time()

    logger.info("Fetching companies from HubSpot...")
    client = HubSpotAPIClient()
    companies = client.get_all_companies()

    logger.info(f"Fetched {len(companies)} companies, storing in database...")

    with connections["fred"].cursor() as cursor:
        cursor.execute("TRUNCATE TABLE hubspot.companies")

        for company in companies:
            props = company.get("properties", {})
            cursor.execute(
                """
                INSERT INTO hubspot.companies (
                    id, fred_id, name, address, address2, city, state_abbreviation, zip,
                    phone, company_email, new_netsuite_id, hubspot_owner_id, company_type,
                    rx_total_shipments, suppress_refill_notifications,
                    total_rx_created, total_rx_paid, total_rx_paid_amount,
                    total_rx_unpaid, total_rx_fills_created, total_rx_fills_paid,
                    total_rx_fills_paid_amount, total_rx_fills_unpaid,
                    total_dios_created, total_dtps_created, total_dtps_paid, total_dtps_unpaid
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                [
                    company["id"],
                    props.get("fred_id"),
                    props.get("name"),
                    props.get("address"),
                    props.get("address2"),
                    props.get("city"),
                    props.get("state_abbreviation"),
                    props.get("zip"),
                    props.get("phone"),
                    props.get("company_email"),
                    props.get("new_netsuite_id"),
                    safe_int(props.get("hubspot_owner_id")),
                    props.get("company_type"),
                    safe_int(props.get("rx_total_shipments")),
                    safe_bool(props.get("suppress_refill_notifications")),
                    safe_int(props.get("total_rx_created")),
                    safe_int(props.get("total_rx_paid")),
                    safe_float(props.get("total_rx_paid_amount")),
                    safe_int(props.get("total_rx_unpaid")),
                    safe_int(props.get("total_rx_fills_created")),
                    safe_int(props.get("total_rx_fills_paid")),
                    safe_float(props.get("total_rx_fills_paid_amount")),
                    safe_int(props.get("total_rx_fills_unpaid")),
                    safe_int(props.get("total_dios_created")),
                    safe_int(props.get("total_dtps_created")),
                    safe_int(props.get("total_dtps_paid")),
                    safe_int(props.get("total_dtps_unpaid")),
                ],
            )

    duration = time.time() - start_time
    summary = {
        "companies_exported": len(companies),
        "duration_seconds": duration,
        "status": "success",
    }

    track_task_metrics(task_name, "success", duration, len(companies), "companies")
    logger.info(f"HubSpot companies export completed: {summary}")
    return summary


def _run_export_hubspot_owners() -> Dict[str, Any]:
    """Export HubSpot owners - synchronous version for pipeline use."""
    task_name = "export_hubspot_owners"
    start_time = time.time()

    logger.info("Fetching owners from HubSpot...")
    client = HubSpotAPIClient()
    owners = client.get_all_owners()

    logger.info(f"Fetched {len(owners)} owners, storing in database...")

    with connections["fred"].cursor() as cursor:
        cursor.execute("TRUNCATE TABLE hubspot.owners")

        for owner in owners:
            cursor.execute(
                """
                INSERT INTO hubspot.owners (id, email, first_name, last_name, user_id)
                VALUES (%s, %s, %s, %s, %s)
            """,
                [
                    owner["id"],
                    owner.get("email"),
                    owner.get("firstName"),
                    owner.get("lastName"),
                    safe_int(owner.get("userId")),
                ],
            )

    duration = time.time() - start_time
    summary = {
        "owners_exported": len(owners),
        "duration_seconds": duration,
        "status": "success",
    }

    track_task_metrics(task_name, "success", duration, len(owners), "owners")
    logger.info(f"HubSpot owners export completed: {summary}")
    return summary


def _run_compare_fred_hubspot(tolerance: float = 0.0) -> Dict[str, Any]:
    """Compare Fred vs HubSpot - synchronous version for pipeline use."""
    task_name = "compare_fred_hubspot"
    start_time = time.time()

    logger.info("Starting Fred vs HubSpot comparison...")
    result = ComparisonResult()

    with connections["fred"].cursor() as cursor:
        # Find companies to ADD
        logger.info("Finding companies to add...")
        cursor.execute(
            """
            SELECT DISTINCT
                f.office_id, f.office_name, f.netsuite_id, f.address1, f.address2,
                f.city, f.state, f.zip, f.office_phone, f.office_email,
                f.salesconsultant_email, o.id as hubspot_owner_id, f.in_office_dispense,
                f.office_total_rx_shipped, f.suppress_refills,
                f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                f.office_total_dios_created, f.office_total_dtps_created,
                f.office_total_dtps_paid, f.office_total_dtps_unpaid
            FROM hubspot.fred_data f
            LEFT JOIN hubspot.companies h1 ON CAST(h1.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
            LEFT JOIN hubspot.companies h2 ON h2.new_netsuite_id = f.netsuite_id
            LEFT JOIN hubspot.owners o ON LOWER(TRIM(o.email)) = LOWER(TRIM(f.salesconsultant_email))
            WHERE h1.id IS NULL AND h2.id IS NULL
        """
        )

        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            result.companies_to_add.append(dict(zip(columns, row)))

        logger.info(f"Found {len(result.companies_to_add)} companies to add")

        # Find companies to UPDATE
        logger.info("Finding companies to update...")
        cursor.execute(
            """
            SELECT 
                h.id as hubspot_id, h.name as hubspot_name, h.fred_id, f.office_id,
                f.office_total_rx_shipped, f.suppress_refills,
                f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                f.office_total_dios_created, f.office_total_dtps_created,
                f.office_total_dtps_paid, f.office_total_dtps_unpaid,
                h.rx_total_shipments, h.suppress_refill_notifications,
                h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                h.total_dios_created, h.total_dtps_created,
                h.total_dtps_paid, h.total_dtps_unpaid
            FROM hubspot.companies h
            JOIN hubspot.fred_data f ON CAST(h.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
            WHERE h.fred_id IS NOT NULL AND h.fred_id != ''
        """
        )

        for row in cursor.fetchall():
            updates = {}
            metric_pairs = [
                ("rx_total_shipments", row[4], row[18]),
                ("suppress_refill_notifications", row[5], row[19]),
                ("total_rx_created", row[6], row[20]),
                ("total_rx_paid", row[7], row[21]),
                ("total_rx_paid_amount", row[8], row[22]),
                ("total_rx_unpaid", row[9], row[23]),
                ("total_rx_fills_created", row[10], row[24]),
                ("total_rx_fills_paid", row[11], row[25]),
                ("total_rx_fills_paid_amount", row[12], row[26]),
                ("total_rx_fills_unpaid", row[13], row[27]),
                ("total_dios_created", row[14], row[28]),
                ("total_dtps_created", row[15], row[29]),
                ("total_dtps_paid", row[16], row[30]),
                ("total_dtps_unpaid", row[17], row[31]),
            ]

            for field_name, fred_val, hubspot_val in metric_pairs:
                if not values_match(hubspot_val, fred_val, tolerance):
                    updates[field_name] = convert_for_json(fred_val)

            if updates:
                result.companies_to_update.append(
                    {
                        "hubspot_id": row[0],
                        "hubspot_name": row[1],
                        "fred_id": row[2],
                        **updates,
                    }
                )

        logger.info(f"Found {len(result.companies_to_update)} companies to update")

        # Find contacts to ADD
        logger.info("Finding contacts to add...")
        cursor.execute(
            """
            SELECT DISTINCT
                f.firstname, f.lastname, f.phone, f.email, f.npi, f.office_id,
                f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid
            FROM hubspot.fred_data f
            LEFT JOIN hubspot.contacts h ON f.npi = h.npi_number
            WHERE h.id IS NULL
            AND f.npi IS NOT NULL AND f.npi != ''
            AND LENGTH(f.npi) = 10
        """
        )

        columns = [col[0] for col in cursor.description]
        for row in cursor.fetchall():
            result.contacts_to_add.append(dict(zip(columns, row)))

        logger.info(f"Found {len(result.contacts_to_add)} contacts to add")

        # Find contacts to UPDATE
        logger.info("Finding contacts to update...")
        cursor.execute(
            """
            SELECT 
                h.id as hubspot_id, h.firstname, h.lastname, h.npi_number,
                f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid,
                h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                h.total_dios_created, h.total_dtps_created,
                h.total_dtps_paid, h.total_dtps_unpaid
            FROM hubspot.contacts h
            JOIN hubspot.fred_data f ON f.npi = h.npi_number
            WHERE h.npi_number IS NOT NULL AND h.npi_number != ''
        """
        )

        for row in cursor.fetchall():
            updates = {}
            metric_pairs = [
                ("total_rx_created", row[4], row[16]),
                ("total_rx_paid", row[5], row[17]),
                ("total_rx_paid_amount", row[6], row[18]),
                ("total_rx_unpaid", row[7], row[19]),
                ("total_rx_fills_created", row[8], row[20]),
                ("total_rx_fills_paid", row[9], row[21]),
                ("total_rx_fills_paid_amount", row[10], row[22]),
                ("total_rx_fills_unpaid", row[11], row[23]),
                ("total_dios_created", row[12], row[24]),
                ("total_dtps_created", row[13], row[25]),
                ("total_dtps_paid", row[14], row[26]),
                ("total_dtps_unpaid", row[15], row[27]),
            ]

            for field_name, fred_val, hubspot_val in metric_pairs:
                if not values_match(hubspot_val, fred_val, tolerance):
                    updates[field_name] = convert_for_json(fred_val)

            if updates:
                result.contacts_to_update.append(
                    {
                        "hubspot_id": row[0],
                        "hubspot_name": f"{row[1] or ''} {row[2] or ''}".strip(),
                        "npi": row[3],
                        **updates,
                    }
                )

        logger.info(f"Found {len(result.contacts_to_update)} contacts to update")

    duration = time.time() - start_time
    summary = {**result.to_dict(), "duration_seconds": duration, "status": "success"}

    track_task_metrics(task_name, "success", duration)
    logger.info(f"Comparison completed: {summary}")
    return summary


def _run_create_hubspot_companies(dry_run: bool = False) -> Dict[str, Any]:
    """Create HubSpot companies - synchronous version for pipeline use."""
    task_name = "create_hubspot_companies"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0}

    logger.info(f"Creating companies in HubSpot (dry_run={dry_run})...")
    client = HubSpotAPIClient()

    with connections["fred"].cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT
                f.office_id, f.office_name, f.netsuite_id, f.address1, f.address2,
                f.city, f.state, f.zip, f.office_phone, f.office_email,
                o.id as hubspot_owner_id, f.in_office_dispense,
                f.office_total_rx_shipped, f.suppress_refills,
                f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                f.office_total_dios_created, f.office_total_dtps_created,
                f.office_total_dtps_paid, f.office_total_dtps_unpaid
            FROM hubspot.fred_data f
            LEFT JOIN hubspot.companies h1 ON CAST(h1.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
            LEFT JOIN hubspot.companies h2 ON h2.new_netsuite_id = f.netsuite_id
            LEFT JOIN hubspot.owners o ON LOWER(TRIM(o.email)) = LOWER(TRIM(f.salesconsultant_email))
            WHERE h1.id IS NULL AND h2.id IS NULL
        """
        )

        companies_to_add = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    logger.info(f"Processing {len(companies_to_add)} companies...")

    for row in companies_to_add:
        company = dict(zip(columns, row))
        office_id = company["office_id"]
        office_name = company["office_name"]
        hubspot_owner_id = company.get("hubspot_owner_id")

        if not hubspot_owner_id:
            logger.warning(f"Skipping {office_name} - no hubspot_owner_id")
            results["skipped"] += 1
            continue

        properties = {
            "name": office_name,
            "fred_id": str(office_id),
            "new_netsuite_id": company.get("netsuite_id") or "",
            "address": company.get("address1") or "",
            "address2": company.get("address2") or "",
            "city": company.get("city") or "",
            "state_abbreviation": company.get("state") or "",
            "zip": company.get("zip") or "",
            "phone": company.get("office_phone") or "",
            "company_email": company.get("office_email") or "",
            "hubspot_owner_id": hubspot_owner_id,
            "company_type": company.get("in_office_dispense") or "",
            "rx_total_shipments": safe_int(company.get("office_total_rx_shipped")),
            "suppress_refill_notifications": (
                "TRUE" if company.get("suppress_refills") else "FALSE"
            ),
            "total_rx_created": safe_int(company.get("office_total_rx_created")),
            "total_rx_paid": safe_int(company.get("office_total_rx_paid")),
            "total_rx_paid_amount": safe_float(
                company.get("office_total_rx_paid_amount")
            ),
            "total_rx_unpaid": safe_int(company.get("office_total_rx_unpaid")),
            "total_rx_fills_created": safe_int(
                company.get("office_total_rx_fills_created")
            ),
            "total_rx_fills_paid": safe_int(company.get("office_total_rx_fills_paid")),
            "total_rx_fills_paid_amount": safe_float(
                company.get("office_total_rx_fills_paid_amount")
            ),
            "total_rx_fills_unpaid": safe_int(
                company.get("office_total_rx_fills_unpaid")
            ),
            "total_dios_created": safe_int(company.get("office_total_dios_created")),
            "total_dtps_created": safe_int(company.get("office_total_dtps_created")),
            "total_dtps_paid": safe_int(company.get("office_total_dtps_paid")),
            "total_dtps_unpaid": safe_int(company.get("office_total_dtps_unpaid")),
        }

        properties = {k: v for k, v in properties.items() if v is not None and v != ""}

        if dry_run:
            logger.info(f"[DRY RUN] Would create company: {office_name}")
            results["success"] += 1
        else:
            response = client.create_company(properties)
            if response:
                logger.info(
                    f"Created company: {office_name} (ID: {response.get('id')})"
                )
                results["success"] += 1
            else:
                logger.error(f"Failed to create company: {office_name}")
                results["failed"] += 1

            time.sleep(0.5)

    duration = time.time() - start_time
    summary = {
        **results,
        "total_processed": len(companies_to_add),
        "duration_seconds": duration,
        "dry_run": dry_run,
        "status": "success",
    }

    track_task_metrics(
        task_name, "success", duration, results["success"], "companies_created"
    )
    logger.info(f"Create companies completed: {summary}")
    return summary


def _run_create_hubspot_contacts(
    dry_run: bool = False, associate_with_company: bool = True
) -> Dict[str, Any]:
    """Create HubSpot contacts - synchronous version for pipeline use."""
    task_name = "create_hubspot_contacts"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0}

    logger.info(f"Creating contacts in HubSpot (dry_run={dry_run})...")
    client = HubSpotAPIClient()

    with connections["fred"].cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT
                f.firstname, f.lastname, f.phone, f.email, f.npi, f.office_id,
                f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid
            FROM hubspot.fred_data f
            LEFT JOIN hubspot.contacts h ON f.npi = h.npi_number
            WHERE h.id IS NULL
            AND f.npi IS NOT NULL AND f.npi != ''
            AND LENGTH(f.npi) = 10
        """
        )

        contacts_to_add = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    logger.info(f"Processing {len(contacts_to_add)} contacts...")

    for row in contacts_to_add:
        contact = dict(zip(columns, row))
        npi = contact["npi"]
        contact_name = (
            f"{contact.get('firstname') or ''} {contact.get('lastname') or ''}".strip()
        )

        cleaned_npi = clean_npi(npi)
        if not cleaned_npi:
            logger.warning(f"Skipping {contact_name} - invalid NPI: {npi}")
            results["skipped"] += 1
            continue

        properties = {
            "firstname": contact.get("firstname") or "",
            "lastname": contact.get("lastname") or "",
            "email": contact.get("email") or "",
            "phone": contact.get("phone") or "",
            "npi_number": cleaned_npi,
            "total_rx_created": safe_int(contact.get("prescriber_total_rx_created")),
            "total_rx_paid": safe_int(contact.get("prescriber_total_rx_paid")),
            "total_rx_paid_amount": safe_float(
                contact.get("prescriber_total_rx_paid_amount")
            ),
            "total_rx_unpaid": safe_int(contact.get("prescriber_total_rx_unpaid")),
            "total_rx_fills_created": safe_int(
                contact.get("prescriber_total_rx_fills_created")
            ),
            "total_rx_fills_paid": safe_int(
                contact.get("prescriber_total_rx_fills_paid")
            ),
            "total_rx_fills_paid_amount": safe_float(
                contact.get("prescriber_total_rx_fills_paid_amount")
            ),
            "total_rx_fills_unpaid": safe_int(
                contact.get("prescriber_total_rx_fills_unpaid")
            ),
            "total_dios_created": safe_int(
                contact.get("prescriber_total_dios_created")
            ),
            "total_dtps_created": safe_int(
                contact.get("prescriber_total_dtps_created")
            ),
            "total_dtps_paid": safe_int(contact.get("prescriber_total_dtps_paid")),
            "total_dtps_unpaid": safe_int(contact.get("prescriber_total_dtps_unpaid")),
        }

        properties = {k: v for k, v in properties.items() if v is not None and v != ""}

        if dry_run:
            logger.info(f"[DRY RUN] Would create contact: {contact_name}")
            results["success"] += 1
        else:
            response = client.create_contact(properties)
            if response:
                contact_id = response.get("id")
                logger.info(f"Created contact: {contact_name} (ID: {contact_id})")

                if associate_with_company and contact.get("office_id"):
                    company = client.search_company_by_fred_id(
                        str(contact["office_id"])
                    )
                    if company:
                        client.associate_contact_to_company(contact_id, company["id"])
                        logger.info(
                            f"Associated contact {contact_id} with company {company['id']}"
                        )

                results["success"] += 1
            else:
                logger.error(f"Failed to create contact: {contact_name}")
                results["failed"] += 1

            time.sleep(0.5)

    duration = time.time() - start_time
    summary = {
        **results,
        "total_processed": len(contacts_to_add),
        "duration_seconds": duration,
        "dry_run": dry_run,
        "status": "success",
    }

    track_task_metrics(
        task_name, "success", duration, results["success"], "contacts_created"
    )
    logger.info(f"Create contacts completed: {summary}")
    return summary


def _run_update_hubspot_companies(dry_run: bool = False) -> Dict[str, Any]:
    """Update HubSpot companies using batch API for better performance."""
    task_name = "update_hubspot_companies"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0, "errors": []}

    BATCH_SIZE = 100  # HubSpot's maximum batch size
    BATCH_DELAY = 0.2  # 200ms between batches

    logger.info(f"Updating companies in HubSpot (dry_run={dry_run})...")
    client = HubSpotAPIClient()

    with connections["fred"].cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                h.id as hubspot_id, h.name as hubspot_name, h.fred_id,
                f.office_total_rx_shipped, f.suppress_refills,
                f.office_total_rx_created, f.office_total_rx_paid, f.office_total_rx_paid_amount,
                f.office_total_rx_unpaid, f.office_total_rx_fills_created, f.office_total_rx_fills_paid,
                f.office_total_rx_fills_paid_amount, f.office_total_rx_fills_unpaid,
                f.office_total_dios_created, f.office_total_dtps_created,
                f.office_total_dtps_paid, f.office_total_dtps_unpaid,
                h.rx_total_shipments, h.suppress_refill_notifications,
                h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                h.total_dios_created, h.total_dtps_created,
                h.total_dtps_paid, h.total_dtps_unpaid
            FROM hubspot.companies h
            JOIN hubspot.fred_data f ON CAST(h.fred_id AS TEXT) = CAST(f.office_id AS TEXT)
            WHERE h.fred_id IS NOT NULL AND h.fred_id != ''
        """
        )

        companies = cursor.fetchall()

    logger.info(f"Checking {len(companies)} companies for updates...")

    # Collect all updates first
    batch_updates = []

    for row in companies:
        hubspot_id = row[0]
        hubspot_name = row[1]

        updates = {}
        metric_pairs = [
            ("rx_total_shipments", row[3], row[17]),
            (
                "suppress_refill_notifications",
                "TRUE" if row[4] else "FALSE",
                "TRUE" if row[18] else "FALSE",
            ),
            ("total_rx_created", row[5], row[19]),
            ("total_rx_paid", row[6], row[20]),
            ("total_rx_paid_amount", row[7], row[21]),
            ("total_rx_unpaid", row[8], row[22]),
            ("total_rx_fills_created", row[9], row[23]),
            ("total_rx_fills_paid", row[10], row[24]),
            ("total_rx_fills_paid_amount", row[11], row[25]),
            ("total_rx_fills_unpaid", row[12], row[26]),
            ("total_dios_created", row[13], row[27]),
            ("total_dtps_created", row[14], row[28]),
            ("total_dtps_paid", row[15], row[29]),
            ("total_dtps_unpaid", row[16], row[30]),
        ]

        for field_name, fred_val, hubspot_val in metric_pairs:
            if field_name == "suppress_refill_notifications":
                if fred_val != hubspot_val:
                    updates[field_name] = fred_val
            elif not values_match(hubspot_val, fred_val):
                updates[field_name] = convert_for_json(fred_val)

        if updates:
            batch_updates.append(
                {
                    "id": str(hubspot_id),
                    "properties": updates,
                    "_name": hubspot_name,  # Keep for logging, removed before API call
                }
            )
    batch_updates = deduplicate_batch_updates(batch_updates, logger)
    total_updates = len(batch_updates)
    logger.info(f"Found {total_updates} companies requiring updates")

    if total_updates == 0:
        results["skipped"] = len(companies)
    elif dry_run:
        logger.info(
            f"[DRY RUN] Would update {total_updates} companies in batches of {BATCH_SIZE}"
        )
        for update in batch_updates[:5]:  # Log first 5 as sample
            logger.info(f"  - {update['_name']}: {list(update['properties'].keys())}")
        if total_updates > 5:
            logger.info(f"  ... and {total_updates - 5} more")
        results["success"] = total_updates
    else:
        # Process in batches
        batches = [
            batch_updates[i : i + BATCH_SIZE]
            for i in range(0, total_updates, BATCH_SIZE)
        ]
        total_batches = len(batches)

        logger.info(
            f"Processing {total_updates} updates in {total_batches} batch(es)..."
        )

        for batch_num, batch in enumerate(batches, 1):
            # Remove internal _name field before sending to API
            api_batch = [{"id": u["id"], "properties": u["properties"]} for u in batch]

            logger.info(
                f"[Batch {batch_num}/{total_batches}] Updating {len(batch)} companies..."
            )

            try:
                response = client.batch_update_companies(api_batch)

                if response:
                    batch_results = response.get("results", [])
                    success_count = len(batch_results)
                    results["success"] += success_count
                    logger.info(f"  Successfully updated {success_count} companies")

                    # Check for errors in response
                    if "errors" in response:
                        error_count = len(response["errors"])
                        results["failed"] += error_count
                        logger.warning(f"  {error_count} companies failed in batch")
                        for error in response["errors"][:3]:  # Log first 3 errors
                            results["errors"].append(
                                {"batch": batch_num, "error": error}
                            )
                            logger.error(f"    Error: {error}")
                else:
                    logger.error(f"  Batch update failed")
                    results["failed"] += len(batch)

                # Rate limiting delay between batches
                if batch_num < total_batches:
                    time.sleep(BATCH_DELAY)

            except Exception as e:
                logger.error(f"  Error processing batch: {e}")
                results["failed"] += len(batch)
                results["errors"].append({"batch": batch_num, "error": str(e)})

    duration = time.time() - start_time
    summary = {
        "success": results["success"],
        "failed": results["failed"],
        "skipped": results["skipped"],
        "total_checked": len(companies),
        "total_updates_needed": total_updates,
        "duration_seconds": duration,
        "dry_run": dry_run,
        "status": "success",
    }

    if results["errors"]:
        summary["error_count"] = len(results["errors"])

    track_task_metrics(
        task_name, "success", duration, results["success"], "companies_updated"
    )
    logger.info(f"Update companies completed: {summary}")
    return summary


def _run_update_hubspot_contacts(dry_run: bool = False) -> Dict[str, Any]:
    """Update HubSpot contacts using batch API for better performance."""
    task_name = "update_hubspot_contacts"
    start_time = time.time()
    results = {"success": 0, "failed": 0, "skipped": 0, "errors": []}

    BATCH_SIZE = 100  # HubSpot's maximum batch size
    BATCH_DELAY = 0.2  # 200ms between batches

    logger.info(f"Updating contacts in HubSpot (dry_run={dry_run})...")
    client = HubSpotAPIClient()

    with connections["fred"].cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                h.id as hubspot_id, h.firstname, h.lastname, h.npi_number,
                f.prescriber_total_rx_created, f.prescriber_total_rx_paid,
                f.prescriber_total_rx_paid_amount, f.prescriber_total_rx_unpaid,
                f.prescriber_total_rx_fills_created, f.prescriber_total_rx_fills_paid,
                f.prescriber_total_rx_fills_paid_amount, f.prescriber_total_rx_fills_unpaid,
                f.prescriber_total_dios_created, f.prescriber_total_dtps_created,
                f.prescriber_total_dtps_paid, f.prescriber_total_dtps_unpaid,
                h.total_rx_created, h.total_rx_paid, h.total_rx_paid_amount,
                h.total_rx_unpaid, h.total_rx_fills_created, h.total_rx_fills_paid,
                h.total_rx_fills_paid_amount, h.total_rx_fills_unpaid,
                h.total_dios_created, h.total_dtps_created,
                h.total_dtps_paid, h.total_dtps_unpaid
            FROM hubspot.contacts h
            JOIN hubspot.fred_data f ON f.npi = h.npi_number
            WHERE h.npi_number IS NOT NULL AND h.npi_number != ''
        """
        )

        contacts = cursor.fetchall()

    logger.info(f"Checking {len(contacts)} contacts for updates...")

    # Collect all updates first
    batch_updates = []

    for row in contacts:
        hubspot_id = row[0]
        contact_name = f"{row[1] or ''} {row[2] or ''}".strip()

        updates = {}
        metric_pairs = [
            ("total_rx_created", row[4], row[16]),
            ("total_rx_paid", row[5], row[17]),
            ("total_rx_paid_amount", row[6], row[18]),
            ("total_rx_unpaid", row[7], row[19]),
            ("total_rx_fills_created", row[8], row[20]),
            ("total_rx_fills_paid", row[9], row[21]),
            ("total_rx_fills_paid_amount", row[10], row[22]),
            ("total_rx_fills_unpaid", row[11], row[23]),
            ("total_dios_created", row[12], row[24]),
            ("total_dtps_created", row[13], row[25]),
            ("total_dtps_paid", row[14], row[26]),
            ("total_dtps_unpaid", row[15], row[27]),
        ]

        for field_name, fred_val, hubspot_val in metric_pairs:
            if not values_match(hubspot_val, fred_val):
                updates[field_name] = convert_for_json(fred_val)

        if updates:
            batch_updates.append(
                {
                    "id": str(hubspot_id),
                    "properties": updates,
                    "_name": contact_name,  # Keep for logging, removed before API call
                }
            )

    batch_updates = deduplicate_batch_updates(batch_updates, logger)
    total_updates = len(batch_updates)
    logger.info(f"Found {total_updates} contacts requiring updates")

    if total_updates == 0:
        results["skipped"] = len(contacts)
    elif dry_run:
        logger.info(
            f"[DRY RUN] Would update {total_updates} contacts in batches of {BATCH_SIZE}"
        )
        for update in batch_updates[:5]:  # Log first 5 as sample
            logger.info(f"  - {update['_name']}: {list(update['properties'].keys())}")
        if total_updates > 5:
            logger.info(f"  ... and {total_updates - 5} more")
        results["success"] = total_updates
    else:
        # Process in batches
        batches = [
            batch_updates[i : i + BATCH_SIZE]
            for i in range(0, total_updates, BATCH_SIZE)
        ]
        total_batches = len(batches)

        logger.info(
            f"Processing {total_updates} updates in {total_batches} batch(es)..."
        )

        for batch_num, batch in enumerate(batches, 1):
            # Remove internal _name field before sending to API
            api_batch = [{"id": u["id"], "properties": u["properties"]} for u in batch]

            logger.info(
                f"[Batch {batch_num}/{total_batches}] Updating {len(batch)} contacts..."
            )

            try:
                response = client.batch_update_contacts(api_batch)

                if response:
                    batch_results = response.get("results", [])
                    success_count = len(batch_results)
                    results["success"] += success_count
                    logger.info(f"  Successfully updated {success_count} contacts")

                    # Check for errors in response
                    if "errors" in response:
                        error_count = len(response["errors"])
                        results["failed"] += error_count
                        logger.warning(f"  {error_count} contacts failed in batch")
                        for error in response["errors"][:3]:  # Log first 3 errors
                            results["errors"].append(
                                {"batch": batch_num, "error": error}
                            )
                            logger.error(f"    Error: {error}")
                else:
                    logger.error(f"  Batch update failed")
                    results["failed"] += len(batch)

                # Rate limiting delay between batches
                if batch_num < total_batches:
                    time.sleep(BATCH_DELAY)

            except Exception as e:
                logger.error(f"  Error processing batch: {e}")
                results["failed"] += len(batch)
                results["errors"].append({"batch": batch_num, "error": str(e)})

    duration = time.time() - start_time
    summary = {
        "success": results["success"],
        "failed": results["failed"],
        "skipped": results["skipped"],
        "total_checked": len(contacts),
        "total_updates_needed": total_updates,
        "duration_seconds": duration,
        "dry_run": dry_run,
        "status": "success",
    }

    if results["errors"]:
        summary["error_count"] = len(results["errors"])

    track_task_metrics(
        task_name, "success", duration, results["success"], "contacts_updated"
    )
    logger.info(f"Update contacts completed: {summary}")
    return summary


# =============================================================================
# Celery Tasks - Pipeline Orchestration
# =============================================================================


@shared_task(bind=True, max_retries=1, default_retry_delay=1800)
def run_hubspot_sync_pipeline(
    self, dry_run: bool = False, skip_export: bool = False
) -> Dict[str, Any]:
    """
    Run the complete HubSpot synchronization pipeline.

    Pipeline steps:
    1. Extract Fred data
    2. Export HubSpot contacts (unless skip_export=True)
    3. Export HubSpot companies (unless skip_export=True)
    4. Export HubSpot owners (unless skip_export=True)
    5. Compare Fred vs HubSpot
    6. Create new companies
    7. Create new contacts
    8. Update existing companies
    9. Update existing contacts

    Args:
        dry_run: If True, don't make changes to HubSpot (just log what would happen)
        skip_export: If True, skip HubSpot API export steps (use existing DB data)

    Returns:
        Dictionary with pipeline execution summary
    """
    task_name = "run_hubspot_sync_pipeline"
    start_time = time.time()
    pipeline_results = {}

    try:
        logger.info("=" * 80)
        logger.info("HUBSPOT SYNCHRONIZATION PIPELINE")
        logger.info("=" * 80)
        logger.info(f"Started: {timezone.now()}")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        logger.info(f"Skip Export: {skip_export}")

        # Step 1: Extract Fred data
        logger.info("\n[1/9] Extracting Fred data...")
        pipeline_results["extract_fred_data"] = _run_extract_fred_data()

        if not skip_export:
            # Step 2: Export HubSpot contacts
            logger.info("\n[2/9] Exporting HubSpot contacts...")
            pipeline_results["export_hubspot_contacts"] = _run_export_hubspot_contacts()

            # Step 3: Export HubSpot companies
            logger.info("\n[3/9] Exporting HubSpot companies...")
            pipeline_results["export_hubspot_companies"] = (
                _run_export_hubspot_companies()
            )

            # Step 4: Export HubSpot owners
            logger.info("\n[4/9] Exporting HubSpot owners...")
            pipeline_results["export_hubspot_owners"] = _run_export_hubspot_owners()
        else:
            logger.info("\n[2-4/9] Skipping HubSpot exports (skip_export=True)")
            pipeline_results["export_hubspot_contacts"] = {"status": "skipped"}
            pipeline_results["export_hubspot_companies"] = {"status": "skipped"}
            pipeline_results["export_hubspot_owners"] = {"status": "skipped"}

        # Step 5: Compare Fred vs HubSpot
        logger.info("\n[5/9] Comparing Fred vs HubSpot...")
        pipeline_results["compare_fred_hubspot"] = _run_compare_fred_hubspot()

        # Step 6: Create new companies
        logger.info("\n[6/9] Creating new companies...")
        pipeline_results["create_hubspot_companies"] = _run_create_hubspot_companies(
            dry_run=dry_run
        )

        # Step 7: Create new contacts
        logger.info("\n[7/9] Creating new contacts...")
        pipeline_results["create_hubspot_contacts"] = _run_create_hubspot_contacts(
            dry_run=dry_run
        )

        # Step 8: Update existing companies
        logger.info("\n[8/9] Updating existing companies...")
        pipeline_results["update_hubspot_companies"] = _run_update_hubspot_companies(
            dry_run=dry_run
        )

        # Step 9: Update existing contacts
        logger.info("\n[9/9] Updating existing contacts...")
        pipeline_results["update_hubspot_contacts"] = _run_update_hubspot_contacts(
            dry_run=dry_run
        )

        duration = time.time() - start_time

        summary = {
            "task_id": self.request.id,
            "start_time": start_time,
            "duration_seconds": duration,
            "duration_minutes": duration / 60,
            "dry_run": dry_run,
            "skip_export": skip_export,
            "step_results": pipeline_results,
            "status": "success",
        }

        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Total Duration: {duration:.1f}s ({duration/60:.1f} minutes)")

        track_task_metrics(task_name, "success", duration)
        return summary

    except Exception as exc:
        duration = time.time() - start_time
        track_task_metrics(task_name, "failed", duration)
        logger.error(f"Pipeline failed: {exc}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        raise
