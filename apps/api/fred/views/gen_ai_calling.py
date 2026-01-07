"""
Gen AI Calling Views Module

Contains views/viewsets related to gen ai calling management.

"""

from django.conf import settings
from rest_framework import generics, viewsets, status
from django.db import connections, IntegrityError, transaction
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from twilio.rest import Client
from datetime import datetime, timedelta
from twilio.base.exceptions import TwilioRestException
import math
import logging
import re
import secrets

from fred.models import PatientCallQueue, PatientOutreach
from fred.serializers import (
    FredPatientOutreachSerializer,
    UpdatePatientCallQueueSerializer,
    PatientCallQueueSerializer,
    PatientOutreachCreateSerializer,
    PatientOutreachStatusUpdateSerializer,
)

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class CallListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


class CallListView(generics.ListAPIView):
    """
    API endpoint for retrieving call list data from patient_call_queue table
    Supports optional 'region' query parameters
    Orders by priority_score (descending) then created_at
    Automatically marks pulled records as 'pulled' status
    """

    serializer_class = PatientCallQueueSerializer
    pagination_class = CallListPagination

    # Define valid regions to prevent any malicious input
    VALID_REGIONS = {
        "EASTERN",
        "CENTRAL",
        "MOUNTAIN",
        "PACIFIC",
        "ALASKA",
        "HAWAII",
        # Add your actual valid region names here
    }

    def validate_region(self, region):
        """Validate the region parameter"""
        if not region:
            return None

        # Remove any whitespace
        region = region.strip()

        # Check if region contains only alphanumeric characters and underscores
        if not re.match(r"^[a-zA-Z0-9_]+$", region):
            raise ValidationError("Region parameter contains invalid characters")

        # Check against whitelist of valid regions
        if region not in self.VALID_REGIONS:
            raise ValidationError(
                f"Invalid region. Valid regions: {', '.join(self.VALID_REGIONS)}"
            )

        return region

    def validate_update_status(self, update_status_param):
        """Validate the update_status parameter"""
        if not update_status_param:
            return True  # Default to True (update records)

        # Convert string to boolean
        if update_status_param.lower() in ["true", "1", "yes"]:
            return True
        elif update_status_param.lower() in ["false", "0", "no"]:
            return False
        else:
            raise ValidationError(
                "update_status parameter must be true, false, 1, 0, yes, or no"
            )

    def validate_page(self, page_str):
        """Validate the page parameter"""
        try:
            page = int(page_str)
            if page < 1:
                raise ValidationError("Page number must be greater than 0")
            return page
        except (ValueError, TypeError):
            raise ValidationError("Page parameter must be a valid integer")

    def validate_page_size(self, page_size_str):
        """Validate the page_size parameter"""
        if not page_size_str:
            return self.pagination_class.page_size  # Return default

        try:
            page_size = int(page_size_str)
            if page_size < 1:
                raise ValidationError("Page size must be greater than 0")
            if page_size > self.pagination_class.max_page_size:
                raise ValidationError(
                    f"Page size cannot exceed {self.pagination_class.max_page_size}"
                )
            return page_size
        except (ValueError, TypeError):
            raise ValidationError("Page size parameter must be a valid integer")

    def get_queryset(self):
        """Get the base queryset - will be filtered in list() method"""
        return PatientCallQueue.objects.using("fred").all()

    def list(self, request, *args, **kwargs):
        try:
            # Validate input parameters
            region_param = request.query_params.get("region", None)
            page_param = request.query_params.get("page", "1")
            page_size_param = request.query_params.get("page_size", None)
            update_status_param = request.query_params.get("update_status", None)
            queue_status_param = request.query_params.get("queue_status", "pending")
            region = self.validate_region(region_param)
            page = self.validate_page(page_param)
            page_size = self.validate_page_size(page_size_param)
            should_update_status = self.validate_update_status(update_status_param)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Build base queryset with filters and ordering
            queryset = PatientCallQueue.objects.using("fred")

            if queue_status_param.lower() != "all":
                queryset = queryset.filter(queue_status=queue_status_param)

            # queryset = queryset.exclude(
            #     txt_error_code__isnull=False, txt_error_code__gt=""
            # )

            queryset = queryset.extra(
                select={
                    "text_delivery_failed": """
                CASE WHEN txt_error_code IS NOT NULL AND txt_error_code != '' 
                THEN TRUE ELSE FALSE END
                """
                }
            )

            # Add region filter if provided - use timezone field directly
            if region:
                queryset = queryset.filter(timezone=region)

            # Apply ordering
            queryset = queryset.order_by("-priority_score", "rx_fillid")

            # Get total count before pagination
            total_count = queryset.count()

            # Calculate pagination
            if page_size <= 0:
                page_size = 100  # fallback

            offset = (page - 1) * page_size
            total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

            # Validate page number against total pages
            if page > total_pages and total_count > 0:
                return Response(
                    {
                        "error": f"Page {page} does not exist. Total pages: {total_pages}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get the records for this page
            records = list(queryset[offset : offset + page_size])

            # Update pulled records if they were in 'pending' status
            records_to_update = []
            if should_update_status:
                records_to_update = [
                    record.id for record in records if record.queue_status == "pending"
                ]

            if records_to_update:
                PatientCallQueue.objects.using("fred").filter(
                    id__in=records_to_update
                ).update(
                    queue_status="pulled",
                    pulled_at=timezone.now(),
                    pulled_by="Capacity API",
                    updated_at=timezone.now(),
                )

                # Update the local objects for serialization
                for record in records:
                    if record.id in records_to_update:
                        record.queue_status = "pulled"
                        record.pulled_at = timezone.now()
                        record.pulled_by = "Capacity API"

        except Exception as e:
            # Log the error (you should use proper logging here)
            print(f"Database error: {e}")
            return Response(
                {"error": "An error occurred while retrieving data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Serialize the data
        serializer = self.get_serializer(records, many=True)

        # Build pagination URLs
        next_page = None
        previous_page = None

        if page < total_pages:
            next_page = self._build_page_url(
                request,
                page + 1,
                region_param,
                page_size,
                update_status_param,
            )

        if page > 1:
            previous_page = self._build_page_url(
                request,
                page - 1,
                region_param,
                page_size,
                update_status_param,
            )

        return Response(
            {
                "count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "next": next_page,
                "previous": previous_page,
                "results": serializer.data,
                "records_pulled": len(records_to_update),
                "status_updated": should_update_status,
            }
        )

    def _build_page_url(
        self,
        request,
        page_num,
        region=None,
        page_size=None,
        update_status=None,
    ):
        """Helper method to build pagination URLs safely"""
        base_url = request.build_absolute_uri().split("?")[0]
        url = f"{base_url}?page={page_num}"
        if region:
            url += f"&region={region}"
        if page_size and page_size != self.pagination_class.page_size:
            url += f"&page_size={page_size}"
        if update_status is not None:
            url += f"&update_status={update_status}"
        return url


class FredPatientOutreachView(generics.ListCreateAPIView):
    queryset = PatientOutreach.objects.all().using("fred")
    serializer_class = FredPatientOutreachSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "rxid", "outreach_attempt", "patient_id"]


class FredPatientOutreachDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PatientOutreach.objects.all().using("fred")
    serializer_class = FredPatientOutreachSerializer


class PatientOutreachCreateView(generics.CreateAPIView):
    """
    Create patient outreach record for a specific RX ID
    POST /patient-outreach/rx/{rxid}/
    """

    serializer_class = PatientOutreachCreateSerializer

    def create(self, request, rxid=None):
        """
        Create a new patient outreach record with rxid from URL
        """
        if not rxid:
            return Response(
                {"error": "rxid is required in URL"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate rxid is a positive integer
        try:
            rxid = int(rxid)
            if rxid < 1:
                raise ValueError("rxid must be positive")
        except (ValueError, TypeError):
            return Response(
                {"error": "rxid must be a valid positive integer"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Serialize and validate the request data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create the record with rxid from URL, current timestamp, and default status
            outreach_data = serializer.validated_data
            outreach_data["rxid"] = rxid
            outreach_data["created"] = timezone.now()
            outreach_data["status"] = "pending"  # Default status for new records
            # processed field remains None for new records

            # Create record using the fred database
            patient_outreach = PatientOutreach.objects.using("fred").create(
                **outreach_data
            )

            # Return the created record
            response_serializer = FredPatientOutreachSerializer(patient_outreach)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # Handle unique constraint violation
            if "uk_patient_outreach_rx_attempt" in str(e):
                return Response(
                    {
                        "error": f"A record with rxid {rxid} and outreach_attempt {outreach_data.get('outreach_attempt')} already exists"
                    },
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                return Response(
                    {"error": "Database constraint violation"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            # Log the error (you should use proper logging here)
            print(f"Error creating patient outreach record: {e}")
            return Response(
                {"error": "An error occurred while creating the record"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PatientOutreachQueueView(generics.ListAPIView):
    """
    Get pending/retry records for cronjob processing
    GET /patient-outreach/queue/?status=pending&limit=100
    """

    serializer_class = FredPatientOutreachSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = PatientOutreach.objects.using("fred")

        # Filter by status (default to pending and retry)
        status_param = self.request.query_params.get("status", "pending,retry")
        if status_param:
            status_list = [s.strip() for s in status_param.split(",")]
            queryset = queryset.filter(status__in=status_list)

        # Order by created date (oldest first for FIFO processing)
        return queryset.order_by("created")


class PatientOutreachStatusUpdateView(generics.UpdateAPIView):
    """
    Update status and processed timestamp for cronjob
    PATCH /patient-outreach/status/{id}/
    """

    queryset = PatientOutreach.objects.all().using("fred")
    serializer_class = PatientOutreachStatusUpdateSerializer

    def update(self, request, *args, **kwargs):
        """
        Update status and optionally set processed timestamp
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # If status is being set to completed or failed, set processed timestamp
            new_status = serializer.validated_data.get("status")
            if (
                new_status in ["completed", "failed"]
                and "processed" not in serializer.validated_data
            ):
                serializer.validated_data["processed"] = timezone.now()

            # Also update the modified timestamp
            serializer.validated_data["modified"] = timezone.now()

            # Save using the fred database
            serializer.save()

            # Return updated record
            response_serializer = FredPatientOutreachSerializer(instance)
            return Response(response_serializer.data)

        except Exception as e:
            print(f"Error updating patient outreach status: {e}")
            return Response(
                {"error": "An error occurred while updating the record"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PatientOutreachBulkStatusUpdateView(generics.GenericAPIView):
    """
    Bulk update status for multiple records (useful for cronjob)
    POST /patient-outreach/bulk-status-update/
    Body: {"ids": [1,2,3], "status": "processing", "set_processed": true}
    """

    def post(self, request):
        """
        Bulk update status for multiple records
        """
        try:
            ids = request.data.get("ids", [])
            new_status = request.data.get("status")
            set_processed = request.data.get("set_processed", False)

            if not ids or not new_status:
                return Response(
                    {"error": "ids and status are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate status
            valid_statuses = [choice[0] for choice in PatientOutreach.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return Response(
                    {"error": f"Status must be one of: {', '.join(valid_statuses)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Prepare update data
            update_data = {"status": new_status, "modified": timezone.now()}

            if set_processed and new_status in ["completed", "failed"]:
                update_data["processed"] = timezone.now()

            # Perform bulk update
            updated_count = (
                PatientOutreach.objects.using("fred")
                .filter(id__in=ids)
                .update(**update_data)
            )

            return Response(
                {
                    "message": f"Successfully updated {updated_count} records",
                    "updated_count": updated_count,
                    "status": new_status,
                }
            )

        except Exception as e:
            print(f"Error in bulk status update: {e}")
            return Response(
                {"error": "An error occurred while updating records"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdatePatientCallQueueView(generics.UpdateAPIView):
    """
    Update patient_call_queue record gathered from provided rxfill id and fields to update
    Expected Payload Example:
    {
        fillid: 1
        fields:
        {
            (All Optional)
            patient_id: int
            cybersource_customerid: string
            patient_firstname: string
            patient_lastname: string
            patient_dob: string
            phonenumber: string
            address1: string
            address2: string
            city: string
            state: string
            zip: string
            timezone: string
            rx_name: string
            rx_number: int
            outstanding_balance: int
            remaining_refills: int
            balance_date: timestamp
            prescriber_name: string
            prescriber_npi: string
            txt_msg: string
            txt_error_message: string
            txt_error_code: string
            txt_date_sent: timestamp
            text_delivery_failed: boolean
            existing_outreach_attempt: int
            existing_outreach_date: timestamp
            existing_call_outcome: string
            queue_status: string
            priority_score: int
            pulled_at: timestamp
            pulled_by: String
            total_call_attempt: int
            successful_contact_made: boolean
            final_outcome: string
            final_outcome_notes: string
            created_at: timestamp
            updated_at: timestamp
        }
    }
    """

    def update(self, request, *args, **kwargs):
        try:
            serializer = UpdatePatientCallQueueSerializer(data=request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                patient_call_queue_record = PatientCallQueue.objects.get(
                    rx_fillid__exact=serializer.data["rx_fillid"]
                )
                for key, value in serializer.data.items():
                    # patient_call_queue_record[0][f"{key}"] = value
                    setattr(patient_call_queue_record, key, value)
                    print(f"Set {key} to {value}")
                patient_call_queue_record.save()
                return Response(
                    {
                        "message": "Data is valid",
                        "stuff": serializer.data,
                    }
                )
        except Exception as e:
            logger.error(f"Error in UpdatePatientCallQueueView: {e}")
            return Response(
                {
                    "error": "An error occurred during Update Patient Call Queue",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PatientOutreachDeleteByRxView(APIView):
    """
    Delete patient outreach record(s) by rxid or rx_fillid
    DELETE /patient-outreach/delete-by-rx/?rxid=123
    DELETE /patient-outreach/delete-by-rx/?rx_fillid=456
    """

    def delete(self, request):
        """
        Delete patient outreach record(s) based on rxid or rx_fillid query parameter
        """
        rxid = request.query_params.get("rxid")
        rx_fillid = request.query_params.get("rx_fillid")

        if not rxid and not rx_fillid:
            return Response(
                {"error": "Either rxid or rx_fillid query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            queryset = PatientOutreach.objects.using("fred")

            if rxid:
                records = queryset.filter(rxid=rxid)
            else:
                records = queryset.filter(rx_fillid=rx_fillid)

            count = records.count()

            if count == 0:
                return Response(
                    {"error": "No patient outreach records found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            records.delete()

            return Response(
                {
                    "message": f"Successfully deleted {count} patient outreach record(s)",
                    "deleted_count": count,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error deleting patient outreach records: {e}")
            return Response(
                {"error": "An error occurred while deleting records"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CallQueueListView(generics.ListAPIView):
    """
    API endpoint for retrieving patient call queue records
    Supports filtering, sorting, and pagination
    """

    serializer_class = PatientCallQueueSerializer
    pagination_class = CallListPagination

    VALID_QUEUE_STATUSES = {"pending", "pulled", "on_hold", "completed", "expired"}
    VALID_ORDER_FIELDS = {
        "priority_score",
        "-priority_score",
        "rx_number",
        "-rx_number",
        "outstanding_balance",
        "-outstanding_balance",
        "cost",
        "-cost",
        "remaining_refills",
        "-remaining_refills",
        "patient_lastname",
        "-patient_lastname",
        "phonenumber",
        "-phonenumber",
        "pulled_at",
        "-pulled_at",
        "queue_status",
        "-queue_status",
        "existing_call_outcome",
        "-existing_call_outcome",
        "call_outcome",
        "-call_outcome",
        "existing_outreach_attempt",
        "-existing_outreach_attempt",
        "outreach_attempt",
        "-outreach_attempt",
        "rx_name",
        "-rx_name",
    }

    # Map API/serializer field names to database model field names
    SORT_FIELD_MAPPING = {
        "cost": "outstanding_balance",
        "call_outcome": "existing_call_outcome",
        "outreach_attempt": "existing_outreach_attempt",
    }

    def list(self, request, *args, **kwargs):
        try:
            params = self._get_validated_params(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = self._build_queryset(params)
            metadata = self._get_metadata(params)

            total_count = queryset.count()
            page_data = self._paginate_queryset(queryset, params, total_count)

            if isinstance(page_data, Response):
                return page_data

            serializer = self.get_serializer(page_data["records"], many=True)

            return Response(
                {
                    "count": total_count,
                    "total_pages": page_data["total_pages"],
                    "current_page": params["page"],
                    "page_size": params["page_size"],
                    "next": page_data["next_url"],
                    "previous": page_data["previous_url"],
                    "results": serializer.data,
                    "queue_counts": metadata["queue_counts"],
                    "available_outcomes": metadata["available_outcomes"],
                    "available_medications": metadata["available_medications"],
                }
            )

        except Exception as e:
            print(f"Database error: {e}")
            return Response(
                {"error": "An error occurred while retrieving data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_validated_params(self, request):
        """Extract and validate all request parameters"""
        params = {}

        # Queue status validation (supports comma-separated or 'all')
        queue_status_param = request.query_params.get("queue_status", "all")
        if queue_status_param.lower() == "all":
            params["queue_statuses"] = None
        else:
            statuses = [
                s.strip().lower() for s in queue_status_param.split(",") if s.strip()
            ]
            invalid = [s for s in statuses if s not in self.VALID_QUEUE_STATUSES]
            if invalid:
                raise ValidationError(
                    f"Invalid queue status(es): {', '.join(invalid)}. "
                    f"Valid statuses: {', '.join(self.VALID_QUEUE_STATUSES)}"
                )
            params["queue_statuses"] = statuses if statuses else None

        # Call outcome validation (comma-separated)
        call_outcome = request.query_params.get("call_outcome")
        params["call_outcomes"] = (
            [o.strip() for o in call_outcome.split(",") if o.strip()]
            if call_outcome
            else None
        )

        # Medication filter
        params["rx_name"] = request.query_params.get("rx_name")

        # Order by validation
        order_by = request.query_params.get("order_by", "-priority_score")
        if order_by not in self.VALID_ORDER_FIELDS:
            order_by = "-priority_score"
        params["order_by"] = order_by

        # Pagination validation
        try:
            page = int(request.query_params.get("page", "1"))
            if page < 1:
                raise ValidationError("Page number must be greater than 0")
            params["page"] = page
        except (ValueError, TypeError):
            raise ValidationError("Page parameter must be a valid integer")

        page_size_param = request.query_params.get("page_size")
        if page_size_param:
            try:
                page_size = int(page_size_param)
                if page_size < 1:
                    raise ValidationError("Page size must be greater than 0")
                if page_size > self.pagination_class.max_page_size:
                    raise ValidationError(
                        f"Page size cannot exceed {self.pagination_class.max_page_size}"
                    )
                params["page_size"] = page_size
            except (ValueError, TypeError):
                raise ValidationError("Page size parameter must be a valid integer")
        else:
            params["page_size"] = self.pagination_class.page_size

        return params

    def _build_queryset(self, params):
        """Build filtered and ordered queryset"""
        from django.db.models import Value, IntegerField
        from django.db.models.functions import Coalesce

        queryset = PatientCallQueue.objects.using("fred")

        # Exclude expired records by default
        queryset = queryset.exclude(queue_status="expired")

        # Apply filters
        if params["queue_statuses"]:
            queryset = queryset.filter(queue_status__in=params["queue_statuses"])

        if params["call_outcomes"]:
            queryset = queryset.filter(
                existing_call_outcome__in=params["call_outcomes"]
            )

        if params["rx_name"]:
            queryset = queryset.filter(rx_name=params["rx_name"])

        # Add text delivery failed annotation
        queryset = queryset.extra(
            select={
                "text_delivery_failed": """
                    CASE WHEN txt_error_code IS NOT NULL AND txt_error_code != '' 
                    THEN TRUE ELSE FALSE END
                """
            }
        )

        # Get sort field - map API field to database field if needed
        order_by = params["order_by"]
        is_desc = order_by.startswith("-")
        field_name = order_by.lstrip("-")

        # Map to database field name if mapping exists
        if field_name in self.SORT_FIELD_MAPPING:
            field_name = self.SORT_FIELD_MAPPING[field_name]

        # Handle NULL values for existing_outreach_attempt - treat NULL as 0
        if field_name == "existing_outreach_attempt":
            queryset = queryset.annotate(
                outreach_attempt_sort=Coalesce(
                    "existing_outreach_attempt", Value(0), output_field=IntegerField()
                )
            )
            db_order_by = (
                "-outreach_attempt_sort" if is_desc else "outreach_attempt_sort"
            )
        else:
            db_order_by = f"-{field_name}" if is_desc else field_name

        # Apply ordering
        queryset = queryset.order_by(db_order_by, "rx_fillid")

        return queryset

    def _get_metadata(self, params):
        """Get queue counts and available filter options"""
        # Queue counts (unfiltered but excluding expired)
        base_qs = PatientCallQueue.objects.using("fred").exclude(queue_status="expired")

        queue_counts = {
            "pending": base_qs.filter(queue_status="pending").count(),
            "pulled": base_qs.filter(queue_status="pulled").count(),
            "on_hold": base_qs.filter(queue_status="on_hold").count(),
            "completed": base_qs.filter(queue_status="completed").count(),
        }

        # Build filter options queryset based on current filters
        options_qs = PatientCallQueue.objects.using("fred").exclude(
            queue_status="expired"
        )
        if params["queue_statuses"]:
            options_qs = options_qs.filter(queue_status__in=params["queue_statuses"])

        # Get available medications
        if params["call_outcomes"]:
            med_qs = options_qs.filter(
                existing_call_outcome__in=params["call_outcomes"]
            )
        else:
            med_qs = options_qs

        available_medications = list(
            med_qs.exclude(rx_name__isnull=True)
            .exclude(rx_name="")
            .values_list("rx_name", flat=True)
            .distinct()
            .order_by("rx_name")
        )

        # Get available outcomes
        if params["rx_name"]:
            outcome_qs = options_qs.filter(rx_name=params["rx_name"])
        else:
            outcome_qs = options_qs

        available_outcomes = list(
            outcome_qs.exclude(existing_call_outcome__isnull=True)
            .exclude(existing_call_outcome="")
            .values_list("existing_call_outcome", flat=True)
            .distinct()
            .order_by("existing_call_outcome")
        )

        return {
            "queue_counts": queue_counts,
            "available_medications": available_medications,
            "available_outcomes": available_outcomes,
        }

    def _paginate_queryset(self, queryset, params, total_count):
        """Handle pagination logic"""
        page = params["page"]
        page_size = params["page_size"]

        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        if page > total_pages and total_count > 0:
            return Response(
                {"error": f"Page {page} does not exist. Total pages: {total_pages}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        offset = (page - 1) * page_size
        records = list(queryset[offset : offset + page_size])

        next_url = (
            self._build_url(self.request, page + 1, params)
            if page < total_pages
            else None
        )
        previous_url = (
            self._build_url(self.request, page - 1, params) if page > 1 else None
        )

        return {
            "records": records,
            "total_pages": total_pages,
            "next_url": next_url,
            "previous_url": previous_url,
        }

    def _build_url(self, request, page_num, params):
        """Build pagination URL with all query parameters"""
        base_url = request.build_absolute_uri().split("?")[0]
        query_params = [f"page={page_num}"]

        if params["page_size"] != self.pagination_class.page_size:
            query_params.append(f"page_size={params['page_size']}")
        if params["queue_statuses"]:
            query_params.append(f"queue_status={','.join(params['queue_statuses'])}")
        if params["call_outcomes"]:
            query_params.append(f"call_outcome={','.join(params['call_outcomes'])}")
        if params["rx_name"]:
            query_params.append(f"rx_name={params['rx_name']}")
        if params["order_by"]:
            query_params.append(f"order_by={params['order_by']}")

        return f"{base_url}?{'&'.join(query_params)}"


class PatientOutreachListPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class PatientOutreachListView(generics.ListAPIView):
    """
    API endpoint for retrieving patient outreach records with server-side pagination
    """

    serializer_class = FredPatientOutreachSerializer
    pagination_class = PatientOutreachListPagination

    VALID_STATUSES = {"pending", "processing", "completed", "failed", "retry"}

    VALID_ORDER_FIELDS = {
        "created",
        "-created",
        "processed",
        "-processed",
        "status",
        "-status",
        "call_outcome",
        "-call_outcome",
        "outreach_attempt",
        "-outreach_attempt",
        "rxid",
        "-rxid",
        "rx_name",
        "-rx_name",
        "patient_id",
        "-patient_id",
    }

    def get_queryset(self):
        """Base queryset"""
        return PatientOutreach.objects.using("fred").all()

    def list(self, request, *args, **kwargs):
        try:
            params = self._get_validated_params(request)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get base queryset with only date filters for accurate counts
            date_filtered_qs = self._get_date_filtered_queryset(params)

            # Calculate status counts FIRST (before applying status/outcome filters)
            # This ensures the tiles show counts for ALL records in date range
            status_counts = self._calculate_status_counts(date_filtered_qs)

            logger.info(f"Status counts: {status_counts}")

            # Get available filter options from date-filtered data
            available_statuses = self._get_available_statuses(date_filtered_qs)
            available_outcomes = self._get_available_outcomes(date_filtered_qs)
            available_medications = self._get_available_medications(date_filtered_qs)

            # Now apply all filters for the actual results
            queryset = self._build_filtered_queryset(date_filtered_qs, params)

            total_count = queryset.count()
            page_data = self._paginate_queryset(queryset, params, total_count)

            if isinstance(page_data, Response):
                return page_data

            serializer = self.get_serializer(page_data["records"], many=True)

            response_data = {
                "count": total_count,
                "total_pages": page_data["total_pages"],
                "current_page": params["page"],
                "page_size": params["page_size"],
                "next": page_data["next_url"],
                "previous": page_data["previous_url"],
                "results": serializer.data,
                "status_counts": status_counts,
                "available_statuses": available_statuses,
                "available_outcomes": available_outcomes,
                "available_medications": available_medications,
            }

            logger.info(f"Response status_counts: {response_data['status_counts']}")

            return Response(response_data)

        except Exception as e:
            logger.error(f"Database error in PatientOutreachListView: {e}")
            import traceback

            traceback.print_exc()
            return Response(
                {"error": f"An error occurred while retrieving data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_validated_params(self, request):
        """Extract and validate all request parameters"""
        params = {}

        # Status validation (supports comma-separated)
        status_param = request.query_params.get("status")
        if status_param:
            statuses = [s.strip() for s in status_param.split(",") if s.strip()]
            params["statuses"] = statuses if statuses else None
        else:
            params["statuses"] = None

        # Call outcome validation (comma-separated)
        call_outcome = request.query_params.get("call_outcome")
        params["call_outcomes"] = (
            [o.strip() for o in call_outcome.split(",") if o.strip()]
            if call_outcome
            else None
        )

        # Medication filter
        params["rx_name"] = request.query_params.get("rx_name")

        # Date filters
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if date_from:
            try:
                params["date_from"] = datetime.strptime(date_from, "%Y-%m-%d")
            except ValueError:
                raise ValidationError("date_from must be in YYYY-MM-DD format")
        else:
            params["date_from"] = None

        if date_to:
            try:
                params["date_to"] = datetime.strptime(date_to, "%Y-%m-%d")
                # Set to end of day
                params["date_to"] = params["date_to"].replace(
                    hour=23, minute=59, second=59
                )
            except ValueError:
                raise ValidationError("date_to must be in YYYY-MM-DD format")
        else:
            params["date_to"] = None

        # Order by validation
        order_by = request.query_params.get("order_by", "-created")
        if order_by not in self.VALID_ORDER_FIELDS:
            order_by = "-created"
        params["order_by"] = order_by

        # Pagination validation
        try:
            page = int(request.query_params.get("page", "1"))
            if page < 1:
                raise ValidationError("Page number must be greater than 0")
            params["page"] = page
        except (ValueError, TypeError):
            raise ValidationError("Page parameter must be a valid integer")

        page_size_param = request.query_params.get("page_size")
        if page_size_param:
            try:
                page_size = int(page_size_param)
                if page_size < 1:
                    raise ValidationError("Page size must be greater than 0")
                if page_size > self.pagination_class.max_page_size:
                    raise ValidationError(
                        f"Page size cannot exceed {self.pagination_class.max_page_size}"
                    )
                params["page_size"] = page_size
            except (ValueError, TypeError):
                raise ValidationError("Page size parameter must be a valid integer")
        else:
            params["page_size"] = self.pagination_class.page_size

        return params

    def _get_date_filtered_queryset(self, params):
        """Get queryset with only date filters applied (for accurate counts)"""
        queryset = PatientOutreach.objects.using("fred")

        if params["date_from"]:
            queryset = queryset.filter(created__gte=params["date_from"])

        if params["date_to"]:
            queryset = queryset.filter(created__lte=params["date_to"])

        return queryset

    def _build_filtered_queryset(self, queryset, params):
        """Build fully filtered and ordered queryset"""
        # Apply status filter
        if params["statuses"]:
            queryset = queryset.filter(status__in=params["statuses"])

        # Apply outcome filter
        if params["call_outcomes"]:
            queryset = queryset.filter(call_outcome__in=params["call_outcomes"])

        # Apply medication filter
        if params["rx_name"]:
            queryset = queryset.filter(rx_name=params["rx_name"])

        # Apply ordering
        queryset = queryset.order_by(params["order_by"], "-id")

        return queryset

    def _calculate_status_counts(self, queryset):
        """Calculate status counts from queryset using individual queries"""
        try:
            # Get total count
            total = queryset.count()

            # Status-based counts - using individual filter queries for reliability
            pending_count = queryset.filter(status="pending").count()
            completed_count = queryset.filter(status="completed").count()
            failed_count = queryset.filter(status="failed").count()
            processing_count = queryset.filter(status="processing").count()
            retry_count = queryset.filter(status="retry").count()

            # Outcome-based counts
            paid_count = queryset.filter(call_outcome="OAI_ORDER_PAID").count()
            vm_count = queryset.filter(call_outcome="OAI_VM_ATTEMPT").count()
            no_answer_count = queryset.filter(call_outcome="OAI_NO_ANSWER").count()
            hung_up_count = queryset.filter(call_outcome="OAI_HUNG_UP").count()
            not_interested_count = queryset.filter(
                call_outcome="OAI_CUST_NOT_INTERESTED"
            ).count()
            invalid_number_count = queryset.filter(
                call_outcome="OAI_INVALID_NO"
            ).count()
            wrong_number_count = queryset.filter(
                call_outcome="OAI_WRONG_NUMBER"
            ).count()

            result = {
                "total": total,
                "pending": pending_count,
                "completed": completed_count,
                "failed": failed_count,
                "processing": processing_count,
                "retry": retry_count,
                "paid": paid_count,
                "vm": vm_count,
                "no_answer": no_answer_count,
                "hung_up": hung_up_count,
                "not_interested": not_interested_count,
                "invalid_number": invalid_number_count,
                "wrong_number": wrong_number_count,
            }

            logger.info(f"Calculated status_counts: {result}")
            return result

        except Exception as e:
            logger.error(f"Error calculating status counts: {e}")
            import traceback

            traceback.print_exc()

            return {
                "total": 0,
                "pending": 0,
                "completed": 0,
                "failed": 0,
                "processing": 0,
                "retry": 0,
                "paid": 0,
                "vm": 0,
                "no_answer": 0,
                "hung_up": 0,
                "not_interested": 0,
                "invalid_number": 0,
                "wrong_number": 0,
            }

    def _get_available_statuses(self, queryset):
        """Get list of available statuses"""
        try:
            statuses = list(
                queryset.exclude(status__isnull=True)
                .exclude(status="")
                .values_list("status", flat=True)
                .distinct()
                .order_by("status")
            )
            logger.info(f"Available statuses: {statuses}")
            return statuses
        except Exception as e:
            logger.error(f"Error getting available statuses: {e}")
            return []

    def _get_available_outcomes(self, queryset):
        """Get list of available outcomes"""
        try:
            outcomes = list(
                queryset.exclude(call_outcome__isnull=True)
                .exclude(call_outcome="")
                .values_list("call_outcome", flat=True)
                .distinct()
                .order_by("call_outcome")
            )
            logger.info(f"Available outcomes: {outcomes}")
            return outcomes
        except Exception as e:
            logger.error(f"Error getting available outcomes: {e}")
            return []

    def _get_available_medications(self, queryset):
        """Get list of available medications"""
        try:
            medications = list(
                queryset.exclude(rx_name__isnull=True)
                .exclude(rx_name="")
                .values_list("rx_name", flat=True)
                .distinct()
                .order_by("rx_name")
            )
            logger.info(f"Available medications count: {len(medications)}")
            return medications
        except Exception as e:
            logger.error(f"Error getting available medications: {e}")
            return []

    def _paginate_queryset(self, queryset, params, total_count):
        """Handle pagination logic"""
        page = params["page"]
        page_size = params["page_size"]

        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        if page > total_pages and total_count > 0:
            return Response(
                {"error": f"Page {page} does not exist. Total pages: {total_pages}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        offset = (page - 1) * page_size
        records = list(queryset[offset : offset + page_size])

        next_url = (
            self._build_url(self.request, page + 1, params)
            if page < total_pages
            else None
        )
        previous_url = (
            self._build_url(self.request, page - 1, params) if page > 1 else None
        )

        return {
            "records": records,
            "total_pages": total_pages,
            "next_url": next_url,
            "previous_url": previous_url,
        }

    def _build_url(self, request, page_num, params):
        """Build pagination URL with all query parameters"""
        base_url = request.build_absolute_uri().split("?")[0]
        query_params = [f"page={page_num}"]

        if params["page_size"] != self.pagination_class.page_size:
            query_params.append(f"page_size={params['page_size']}")
        if params["statuses"]:
            query_params.append(f"status={','.join(params['statuses'])}")
        if params["call_outcomes"]:
            query_params.append(f"call_outcome={','.join(params['call_outcomes'])}")
        if params["rx_name"]:
            query_params.append(f"rx_name={params['rx_name']}")
        if params["date_from"]:
            query_params.append(f"date_from={params['date_from'].strftime('%Y-%m-%d')}")
        if params["date_to"]:
            query_params.append(f"date_to={params['date_to'].strftime('%Y-%m-%d')}")
        if params["order_by"]:
            query_params.append(f"order_by={params['order_by']}")

        return f"{base_url}?{'&'.join(query_params)}"


__all__ = [
    "StandardResultsSetPagination",
    "CallListPagination",
    "CallListView",
    "FredPatientOutreachView",
    "FredPatientOutreachDetailView",
    "PatientOutreachCreateView",
    "PatientOutreachQueueView",
    "PatientOutreachStatusUpdateView",
    "PatientOutreachBulkStatusUpdateView",
    "UpdatePatientCallQueueView",
    "PatientOutreachDeleteByRxView",
    "CallQueueListView",
    "PatientOutreachListPagination",
    "PatientOutreachListView",
]
