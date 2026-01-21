"""
Office Views Module

Contains views related to office/location management.
Views act as controller actions - simple fetching in views,
validation/creation/updating in serializers.

Legacy Controller Mapping: OfficeController, OfficeTypeController, OfficeAgreementTypeController
"""

from datetime import datetime, timedelta
import json
import logging
import secrets
from typing import Union, List

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction, connections
from django.db.models import Q, Count, Sum
from dateutil.relativedelta import relativedelta

from fred.models.office import Office
from fred.models.models import (
    Users,
    Rx,
    Payment,
    Rxfill,
    DioItems,
    Skincarepairings,
    Shipment,
)
from fred.models.doctor import Doctor
from fred.models.medication import Medication
from fred.serializers import reference as reference_serializer
from fred.serializers.office import (
    OfficeListSerializer,
    OfficeModelSerializer,
    OfficeDetailSerializer,
    OfficeCreateSerializer,
    OfficeUpdateSerializer,
    OfficeMergeSerializer,
    OfficePaginationQuerySerializer,
    OfficeInfoSerializer,
    parse_json_array,
    log_office_history,
    get_office_info,
    get_users_with_details,
)
from fred.serializers.payment import PaymentService
from fred.serializers.rx import RxService
from fred.serializers.rxfill import RxFillService
from fred.serializers.user import UserAddSerializer


logger = logging.getLogger(__name__)


# =============================================================================
# HELPER FUNCTIONS (Used across multiple views)
# =============================================================================


def get_office_ids_by_user(user_id: int) -> List[int]:
    """Get office IDs where user is in sales array."""
    office_ids = []
    for office in (
        Office.objects.using("fred").exclude(sales__isnull=True).exclude(sales="")
    ):
        if user_id in parse_json_array(office.sales):
            office_ids.append(office.id)
    return office_ids


def get_office_ids_by_manager(manager_id: int) -> List[int]:
    """Get office IDs for sales users managed by this manager."""
    managed_sales = list(
        Users.objects.using("fred")
        .filter(managerid=manager_id, role__in=["sales", "sales-manager"])
        .values_list("id", flat=True)
    )

    office_ids = set()
    for office in (
        Office.objects.using("fred").exclude(sales__isnull=True).exclude(sales="")
    ):
        sales_ids = parse_json_array(office.sales)
        if any(sid in managed_sales for sid in sales_ids):
            office_ids.add(office.id)
    return list(office_ids)


def check_data_changed(old_data: dict, new_data: dict) -> bool:
    """Check if two data dicts are different (excluding modified/synced)."""
    for key, value in old_data.items():
        if key not in ("modified", "synced") and new_data.get(key) != value:
            return True
    return False


# =============================================================================
# LIST VIEWS
# =============================================================================


class OfficeListView(APIView):
    """
    GET /office/
    Get all offices.
    """

    def get(self, request):
        try:
            offices = Office.objects.using("fred").order_by("-id")
            serializer = OfficeListSerializer(offices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeFastListView(APIView):
    """
    GET /office/fastlist/
    Get minimal office list for dropdowns.
    """

    def get(self, request):
        try:
            results = list(
                Office.objects.using("fred").values("id", "name").order_by("name")
            )
            return Response({"results": results}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching fast office list: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListPaginatedView(APIView):
    """
    GET /office/list-paginated/
    Get paginated office list.
    """

    def get(self, request):
        try:
            input_serializer = OfficePaginationQuerySerializer(data=request.GET)
            input_serializer.is_valid(raise_exception=True)
            params = input_serializer.validated_data

            user = request.user
            role = getattr(user, "role", None)
            user_id = user.id

            office_ids = None

            if role == "sales":
                office_ids = get_office_ids_by_user(user_id)
                if not office_ids:
                    return Response(
                        {
                            "offices": [],
                            "firstPage": 1,
                            "currentPage": params["page"],
                            "lastPage": 1,
                            "recordsFiltered": 0,
                            "nextPage": None,
                            "previousPage": None,
                            "recordsTotal": 0,
                            "limit": params["limit"],
                        },
                        status=status.HTTP_200_OK,
                    )

            elif role == "sales-manager":
                office_ids = list(
                    set(
                        get_office_ids_by_manager(user_id)
                        + get_office_ids_by_user(user_id)
                    )
                )
                if not office_ids:
                    return Response(
                        {
                            "offices": [],
                            "firstPage": 1,
                            "currentPage": params["page"],
                            "lastPage": 1,
                            "recordsFiltered": 0,
                            "nextPage": None,
                            "previousPage": None,
                            "recordsTotal": 0,
                            "limit": params["limit"],
                        },
                        status=status.HTTP_200_OK,
                    )

            office_serializer = OfficeModelSerializer()
            results = office_serializer.list_paginated(
                page=params["page"],
                limit=params["limit"],
                search=params.get("search"),
                order=params.get("order", 0),
                orderDir=params.get("orderDir", "asc"),
                office_ids=office_ids,
            )

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Error fetching offices list")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListAltView(APIView):
    """
    GET /office/list/
    Get office list (alternate).
    """

    def get(self, request):
        try:
            include_inactive = (
                request.query_params.get("include_inactive", "false").lower() == "true"
            )

            qs = Office.objects.using("fred").all()
            if not include_inactive:
                qs = qs.exclude(name__contains="(x)")

            offices = [
                {
                    "id": o.id,
                    "name": o.name,
                    "netsuiteid": o.netsuiteid,
                    "created": o.created.isoformat() if o.created else None,
                    "inofficedispense": o.inofficedispense,
                }
                for o in qs.order_by("name")
            ]

            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting office list: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListNewView(APIView):
    """
    GET /office/list-new/
    Get new offices.
    """

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
            cutoff = datetime.now() - timedelta(days=days)

            offices = [
                {
                    "id": o.id,
                    "name": o.name,
                    "netsuiteid": o.netsuiteid,
                    "created": o.created.isoformat() if o.created else None,
                }
                for o in Office.objects.using("fred")
                .filter(created__gte=cutoff)
                .order_by("-created")
            ]

            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting new offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListUpdatedView(APIView):
    """
    GET /office/list-updated/
    Get updated offices.
    """

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
            cutoff = datetime.now() - timedelta(days=days)

            offices = [
                {
                    "id": o.id,
                    "name": o.name,
                    "netsuiteid": o.netsuiteid,
                    "created": o.created.isoformat() if o.created else None,
                    "modified": o.modified.isoformat() if o.modified else None,
                }
                for o in Office.objects.using("fred")
                .filter(modified__gte=cutoff)
                .order_by("-modified")
            ]

            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting updated offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeUnassignedPaginatedView(APIView):
    """
    GET /office/unassigned-paginated/
    Get unassigned offices (paginated).
    """

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 10))
            search = request.query_params.get("search", None)

            qs = Office.objects.using("fred").filter(
                Q(sales__isnull=True) | Q(sales="") | Q(sales="[]")
            )
            total_records = qs.count()

            if search:
                qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))

            filtered_records = qs.count()
            offset = (page - 1) * limit
            total_pages = (filtered_records + limit - 1) // limit if limit > 0 else 1

            offices = [
                {
                    "id": o.id,
                    "name": o.name,
                    "netsuiteid": o.netsuiteid,
                    "email": o.email,
                    "created": o.created.isoformat() if o.created else None,
                }
                for o in qs.order_by("name")[offset : offset + limit]
            ]

            return Response(
                {
                    "offices": offices,
                    "currentPage": page,
                    "lastPage": total_pages,
                    "recordsFiltered": filtered_records,
                    "recordsTotal": total_records,
                    "limit": limit,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error getting unassigned offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListWithAddressView(APIView):
    """
    GET /office/listWithAddress/
    Get office list with address.
    """

    def get(self, request):
        try:
            offices = []
            for office in (
                Office.objects.using("fred")
                .exclude(name__contains="(x)")
                .order_by("name")
            ):
                office_data = {
                    "id": office.id,
                    "name": office.name,
                    "netsuiteid": office.netsuiteid,
                    "address": None,
                }
                if office.addressid:
                    addr = (
                        reference_serializer.AddressModelSerializer.get_address_by_id(
                            office.addressid
                        )
                    )
                    if addr:
                        office_data["address"] = {
                            k: addr.get(k)
                            for k in (
                                "id",
                                "address1",
                                "address2",
                                "city",
                                "state",
                                "zip",
                            )
                        }
                offices.append(office_data)

            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting office list with address: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# DETAIL / CRUD VIEWS
# =============================================================================


class OfficeDetailView(APIView):
    """
    GET    /office/{pk}/ - Get office details
    PUT    /office/{pk}/ - Update office
    DELETE /office/{pk}/ - Delete office
    """

    def get(self, request, pk):
        try:
            role = request.query_params.get("role", "admin")
            user_id = request.query_params.get("user_id")
            user_id = int(user_id) if user_id else None

            office = Office.objects.using("fred").get(pk=pk)

            # Access control for doctor/office roles
            if role in ("doctor", "office") and user_id:
                users = parse_json_array(office.users)
                if user_id not in users:
                    return Response({"error": True}, status=status.HTTP_403_FORBIDDEN)

            serializer = OfficeDetailSerializer(office)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error fetching office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            old_data = OfficeListSerializer(office).data

            role = request.query_params.get("role", "admin")

            serializer = OfficeUpdateSerializer(
                office, data=request.data, partial=True, context={"role": role}
            )

            if serializer.is_valid():
                updated_office = serializer.save()
                new_data = OfficeListSerializer(updated_office).data

                user_id = request.query_params.get("user_id", 0)
                if check_data_changed(old_data, new_data):
                    log_office_history(
                        office_id=pk,
                        user_id=int(user_id) if user_id else 0,
                        triggered_action="updateAction",
                        old_data=json.dumps(old_data),
                        new_data=json.dumps(new_data),
                    )

                return Response(status=status.HTTP_200_OK)

            logger.warning(f"Validation errors: {serializer.errors}")
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error updating office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            old_data = OfficeListSerializer(office).data

            office.delete()

            user_id = request.query_params.get("user_id", 0)
            log_office_history(
                office_id=pk,
                user_id=int(user_id) if user_id else 0,
                triggered_action="deleteAction",
                old_data=json.dumps(old_data),
                new_data=None,
            )

            logger.info(f"Office #{pk} has been deleted")
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error deleting office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeCreateView(APIView):
    """
    POST /office/add/
    Create a new office.
    """

    def post(self, request):
        try:
            serializer = OfficeCreateSerializer(data=request.data)

            if serializer.is_valid():
                office = serializer.save()

                user_id = request.query_params.get("user_id", 0)
                new_data = OfficeListSerializer(office).data
                log_office_history(
                    office_id=office.id,
                    user_id=int(user_id) if user_id else 0,
                    triggered_action="addAction",
                    old_data=None,
                    new_data=json.dumps(new_data),
                )

                logger.info(f"{office.name} (office) has been added")
                return Response({"id": office.id}, status=status.HTTP_201_CREATED)

            logger.warning(f"Validation errors: {serializer.errors}")
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        except Exception as e:
            logger.error(f"Error creating office: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeViewView(APIView):
    """
    GET /office/view/{pk}/
    GET /office/view/{pk}/?rx=true  (to pull rx data)
    Get full office view with related records.
    """

    def get(self, request, pk):
        try:
            pull_rx_param = request.query_params.get("rx", None)
            pull_rx = pull_rx_param and pull_rx_param.lower() in ("true", "1", "yes")

            if pull_rx:
                rxs = RxService.get_all_by_office(pk)
                return Response(
                    {
                        "rxs": [
                            rx_data
                            for rx in rxs
                            if (rx_data := RxService.view_q(rx.id, hipaa=True))
                        ]
                    },
                    status=status.HTTP_200_OK,
                )

            office = Office.objects.using("fred").get(pk=pk)
            office_info = get_office_info(pk)

            result = {
                "officeInfo": (
                    OfficeInfoSerializer(office_info).data if office_info else None
                ),
                "officeType": office.officetypeid.type if office.officetypeid else None,
                "office": OfficeListSerializer(office).data,
                "address": (
                    reference_serializer.AddressModelSerializer.get_address_by_id(
                        office.addressid
                    )
                    if office.addressid
                    else None
                ),
                "encryptAcct": office.acct,
            }

            return Response(result, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting office view {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# USER MANAGEMENT VIEWS
# =============================================================================


class OfficeUsersView(APIView):
    """
    GET /office/{pk}/users/
    Get users for an office.
    """

    def get(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            user_ids = parse_json_array(office.users)
            users = get_users_with_details(user_ids)

            return Response(users, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error fetching users for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSetUsersView(APIView):
    """
    POST /office/{pk}/users/set/
    Set users for an office.
    """

    def post(self, request, pk):
        try:
            user_ids = request.data.get("users", [])

            if not isinstance(user_ids, list):
                return Response(
                    {"error": "users must be a list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office = Office.objects.using("fred").get(pk=pk)
            office.users = json.dumps(user_ids)
            office.save(using="fred")

            logger.info(f"Office #{pk} users set to: {user_ids}")
            return Response({"success": True}, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error setting users for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSalesView(APIView):
    """
    GET /office/{pk}/sales/
    Get sales users for an office.
    """

    def get(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            sales_ids = parse_json_array(office.sales)

            all_sales = (
                Users.objects.using("fred")
                .filter(role__in=["sales", "sales-manager"])
                .order_by("first_name")
            )

            assigned, available = [], []
            for user in all_sales:
                user_data = {
                    "id": user.id,
                    "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
                    "email": user.email,
                    "role": user.role,
                }
                (assigned if user.id in sales_ids else available).append(user_data)

            return Response(
                {"assigned": assigned, "available": available},
                status=status.HTTP_200_OK,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error fetching sales for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSetSalesView(APIView):
    """
    POST /office/{pk}/sales/set/
    Set sales for an office.
    """

    def post(self, request, pk):
        try:
            sales_ids = request.data.get("sales", [])

            if not isinstance(sales_ids, list):
                return Response(
                    {"error": "sales must be a list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office = Office.objects.using("fred").get(pk=pk)
            office.sales = json.dumps(sales_ids)
            office.save(using="fred")

            logger.info(f"Office #{pk} sales set to: {sales_ids}")
            return Response({"success": True}, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error setting sales for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserOfficesView(APIView):
    """
    GET /office/user/
    Get offices for logged-in user.
    """

    def get(self, request):
        try:
            user_id = request.query_params.get("user_id")
            if not user_id:
                return Response(
                    {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            user_id = int(user_id)

            result = []
            for office in Office.objects.using("fred").all():
                if user_id in parse_json_array(office.users):
                    name = office.name.replace(" (x)", "") if office.name else ""
                    result.append({"id": office.id, "name": name})

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching user offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeAddUserView(APIView):
    """
    POST /office/addUser/{pk}/
    Add new user to office.
    """

    def post(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)

            email = request.data.get("email")
            if not email:
                return Response(
                    {"error": "email is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            user_data = request.data.copy()
            password = user_data.get("pass") or secrets.token_urlsafe(12)
            user_data["pass"] = password

            serializer = UserAddSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

            with transaction.atomic(using="fred"):
                current_users = parse_json_array(office.users)
                if user.id not in current_users:
                    current_users.append(user.id)
                    office.users = json.dumps(current_users)
                    office.save(using="fred")

            logger.info(f"User #{user.id} added to office #{pk}")
            return Response(
                {"user_id": user.id, "email": user.email, "temp_password": password},
                status=status.HTTP_201_CREATED,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error adding user to office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeContactsView(APIView):
    """
    GET /office/contacts/{pk}/
    Get office contacts.
    """

    def get(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            contacts = get_users_with_details(parse_json_array(office.users))

            return Response(contacts, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting contacts for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# PERFORMANCE VIEW
# =============================================================================


class OfficePerformanceView(APIView):
    """
    GET /office/performance/{pk}/
    Get office performance metrics.
    """

    def _count_rx(self, oid, start=None, end=None, rx_type="newrx"):
        offices = oid if isinstance(oid, list) else [oid]
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid__in=offices)
            .values_list("id", flat=True)
        )
        qs = Rxfill.objects.using("fred").filter(rxid__in=rx_ids, type=rx_type)
        if start:
            qs = qs.filter(created__gt=start)
        if end:
            qs = qs.filter(created__lt=end)
        return qs.count()

    def _count_shipments(self, oid, start=None, end=None):
        offices = oid if isinstance(oid, list) else [oid]
        rx_ids = (
            Rx.objects.using("fred")
            .filter(officeid__in=offices)
            .values_list("id", flat=True)
        )
        shipment_ids = (
            Rxfill.objects.using("fred")
            .filter(rxid__in=rx_ids, shipmentid__isnull=False)
            .values_list("shipmentid", flat=True)
        )
        qs = Shipment.objects.using("fred").filter(id__in=shipment_ids)
        if start:
            qs = qs.filter(created__gt=start)
        if end:
            qs = qs.filter(created__lt=end)
        return qs.count()

    def _count_payments(self, oid, start=None, end=None, payment_type=None):
        offices = oid if isinstance(oid, list) else [oid]
        qs = Payment.objects.using("fred").filter(officeid__in=offices)
        if payment_type:
            qs = qs.filter(type=payment_type)
        if start:
            qs = qs.filter(created__gt=start)
        if end:
            qs = qs.filter(created__lt=end)
        return qs.count()

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)  # Verify exists

            results = []
            current = datetime(2020, 3, 1)

            while current <= datetime.now():
                month_start = current.replace(day=1)
                month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

                results.append(
                    [
                        month_start.strftime("%Y-%m"),
                        self._count_rx(pk, month_start, month_end, "newrx"),
                        self._count_rx(pk, month_start, month_end, "refill"),
                        self._count_rx(pk, month_start, month_end, "corrector"),
                        self._count_shipments(pk, month_start, month_end),
                        self._count_payments(pk, month_start, month_end, "pos"),
                        self._count_payments(pk, month_start, month_end, "rxportal"),
                        self._count_payments(pk, month_start, month_end, "self"),
                    ]
                )
                current += relativedelta(months=1)

            return Response(results, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": str(e), "type": e.__class__.__name__},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# RX / MEDICATION / PATIENT / PRESCRIBER VIEWS
# =============================================================================


class OfficeMedicationsView(APIView):
    """
    GET /office/medications/{pk}/
    Get office medications.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)

            start = request.query_params.get("start")
            end = request.query_params.get("end")

            start_dt = datetime.fromisoformat(start) if start else None
            end_dt = datetime.fromisoformat(end) if end else None

            medications = RxService.get_medications_by_office(pk, start_dt, end_dt)
            return Response(medications, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting medications for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePrescribersView(APIView):
    """
    GET /office/prescribers/{pk}/
    Get office prescribers.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)
            prescribers = RxService.get_prescribers_by_office(pk)
            return Response(prescribers, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting prescribers for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePatientsView(APIView):
    """
    GET /office/patients/{pk}/
    Get office patients.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)
            patients = RxService.get_patients_by_office(pk)
            return Response(patients, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting patients for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeRxView(APIView):
    """
    GET /office/rx/{pk}/
    Get office prescriptions.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)

            role = getattr(request.user, "role", None)
            start = request.query_params.get("start")
            end = request.query_params.get("end")

            no_drilldown = role in {"sales", "sales-manager", "office", "doctor"}
            data = RxService.build_rx_response(
                rxs=RxService.get_rx_by_office(pk, start, end, kind="rx"),
                payments=RxService.get_rx_by_office(pk, start, end, kind="payment"),
                shipments=RxService.get_rx_by_office(pk, start, end, kind="shipment"),
                role=role,
                no_drilldown=no_drilldown,
            )

            return Response(data, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.exception(f"Error getting prescriptions for office {pk}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePendingRxView(APIView):
    """
    GET /office/pendingrx/{pk}/
    Get pending prescriptions.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)
            pending = RxFillService.get_pending_fills_by_office(pk)
            return Response(pending, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting pending rx for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePendingPaymentsView(APIView):
    """
    GET /office/pendingpayments/{pk}/
    Get pending payments.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)
            pending = PaymentService.get_pending_by_office(pk)
            return Response(pending, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting pending payments for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePaidRxsView(APIView):
    """
    GET /office/paid-rxs/{pk}/
    Get paid prescriptions.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)
            paid_rxs = RxFillService.get_paid_fills_by_office(pk)
            return Response(paid_rxs, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting paid rxs for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# LOOKUP VIEWS
# =============================================================================


class OfficeUpdateVendorIdView(APIView):
    """
    PUT /office/update-vendor-id/{pk}/
    Update vendor ID.
    """

    def put(self, request, pk):
        try:
            vendor_id = request.data.get("vendorid")

            if vendor_id is None:
                return Response(
                    {"error": "vendorid is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic(using="fred"):
                office = Office.objects.using("fred").get(pk=pk)
                office.vendorid = int(vendor_id)
                office.save(using="fred")

            logger.info(f"Office #{pk} vendor ID updated to {vendor_id}")
            return Response(
                {"success": True, "vendorid": office.vendorid},
                status=status.HTTP_200_OK,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error updating vendor ID for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeByNetsuiteIdView(APIView):
    """
    GET /office/nsid/
    Get office by NetSuite ID.
    """

    def get(self, request):
        try:
            nsid = request.query_params.get("id")
            if not nsid:
                return Response(
                    {"error": "id (NetSuite ID) is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office = Office.objects.using("fred").get(netsuiteid=int(nsid))
            serializer = OfficeDetailSerializer(office)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with NetSuite ID {nsid} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting office by NetSuite ID: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# SPECIAL OPERATIONS VIEWS
# =============================================================================


class OfficeCanPrescribeView(APIView):
    """
    GET /office/canPrescribe/{pk}/
    Check if office can prescribe.
    """

    def get(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            user_ids = parse_json_array(office.users)
            active_doctors = []

            for uid in user_ids:
                try:
                    user = Users.objects.using("fred").get(pk=uid)
                    if (
                        user.role == "doctor"
                        and user.doctorid
                        and user.status == "active"
                    ):
                        try:
                            doctor = Doctor.objects.using("fred").get(pk=user.doctorid)
                            if doctor.npi:
                                active_doctors.append(
                                    {
                                        "userId": user.id,
                                        "doctorId": doctor.id,
                                        "name": doctor.name,
                                        "npi": doctor.npi,
                                    }
                                )
                        except Doctor.DoesNotExist:
                            pass
                except Users.DoesNotExist:
                    continue

            return Response(
                {
                    "officeId": pk,
                    "canPrescribe": len(active_doctors) > 0,
                    "activeDoctors": active_doctors,
                    "doctorCount": len(active_doctors),
                },
                status=status.HTTP_200_OK,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error checking if office {pk} can prescribe: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeLeafletView(APIView):
    """
    GET /office/leaflet/{pk}/
    Get office leaflet data.
    """

    def get(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            office_info = get_office_info(pk)

            leaflet = {
                "officeId": office.id,
                "name": office.displayname or office.name,
                "logo": office.logo,
                "address": None,
                "phone": office_info.primaryphone if office_info else None,
                "fax": office_info.fax if office_info else None,
                "email": office.officeemail or office.email,
            }

            if office.addressid:
                addr = reference_serializer.AddressModelSerializer.get_address_by_id(
                    office.addressid
                )
                if addr:
                    leaflet["address"] = {
                        k: addr.get(k)
                        for k in ("address1", "address2", "city", "state", "zip")
                    }

            return Response(leaflet, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting leaflet for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeQrView(APIView):
    """
    GET /office/qr/{pk}/
    Get office QR code data.
    """

    def get(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            slug = office.officeslug or str(office.id)
            qr_url = f"https://skinvera.com/office/{slug}"

            return Response(
                {
                    "officeId": office.id,
                    "name": office.name,
                    "slug": office.officeslug,
                    "qrUrl": qr_url,
                    "qrData": qr_url,
                },
                status=status.HTTP_200_OK,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting QR for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeReportsView(APIView):
    """
    GET /office/reports/
    Get available report types.
    """

    def get(self, request):
        try:
            reports = [
                {
                    "id": "summary",
                    "name": "Summary Report",
                    "description": "Overview of office activity",
                },
                {
                    "id": "inventory",
                    "name": "Inventory Report",
                    "description": "Current inventory status",
                },
                {
                    "id": "escrow",
                    "name": "Escrow Report",
                    "description": "Escrow account details",
                },
                {
                    "id": "rx",
                    "name": "Prescription Report",
                    "description": "Prescription history",
                },
                {
                    "id": "payment",
                    "name": "Payment Report",
                    "description": "Payment history",
                },
            ]
            return Response(reports, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting reports: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeLeafletSampleView(APIView):
    """
    GET /office/leafletSample/
    Get sample leaflet template.
    """

    def get(self, request):
        try:
            sample = {
                "template": "default",
                "sections": [
                    {"id": "header", "name": "Header", "required": True},
                    {"id": "about", "name": "About Us", "required": False},
                    {"id": "services", "name": "Services", "required": False},
                    {"id": "contact", "name": "Contact Info", "required": True},
                    {"id": "footer", "name": "Footer", "required": True},
                ],
                "sampleData": {
                    "name": "Sample Medical Office",
                    "displayname": "Sample Medical",
                    "logo": "https://example.com/sample-logo.png",
                    "aboutHtml": "<p>Welcome to our practice.</p>",
                    "address": {
                        "address1": "123 Medical Way",
                        "city": "Healthcare City",
                        "state": "CA",
                        "zip": "90210",
                    },
                    "phone": "555-123-4567",
                    "fax": "555-123-4568",
                    "email": "info@sampleoffice.com",
                },
            }
            return Response(sample, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting leaflet sample: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# MERGE / MOVE VIEWS
# =============================================================================


class OfficeMergeView(APIView):
    """
    POST /office/merge/
    Merge offices.
    """

    def post(self, request):
        try:
            serializer = OfficeMergeSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            source_office_id = serializer.validated_data["sourceOfficeId"]
            target_office_id = serializer.validated_data["targetOfficeId"]
            user_id = request.query_params.get("user_id", 0)

            with transaction.atomic(using="fred"):
                source = Office.objects.using("fred").get(pk=source_office_id)
                target = Office.objects.using("fred").get(pk=target_office_id)

                rx_count = (
                    Rx.objects.using("fred")
                    .filter(officeid=source_office_id)
                    .update(officeid=target_office_id)
                )
                payment_count = (
                    Payment.objects.using("fred")
                    .filter(officeid=source_office_id)
                    .update(officeid=target_office_id)
                )

                source_users = parse_json_array(source.users)
                target_users = parse_json_array(target.users)
                target.users = json.dumps(list(set(target_users + source_users)))

                source_sales = parse_json_array(source.sales)
                target_sales = parse_json_array(target.sales)
                target.sales = json.dumps(list(set(target_sales + source_sales)))
                target.save(using="fred")

                if "(x)" not in source.name:
                    source.name = f"{source.name} (x)"
                    source.save(using="fred")

                log_office_history(
                    office_id=target_office_id,
                    user_id=int(user_id) if user_id else 0,
                    triggered_action="mergeAction",
                    old_data=json.dumps({"sourceOfficeId": source_office_id}),
                    new_data=json.dumps(
                        {
                            "rxMoved": rx_count,
                            "paymentsMoved": payment_count,
                            "usersMerged": len(source_users),
                        }
                    ),
                )

            logger.info(f"Merged office #{source_office_id} into #{target_office_id}")
            return Response(
                {
                    "success": True,
                    "sourceOfficeId": source_office_id,
                    "targetOfficeId": target_office_id,
                    "rxMoved": rx_count,
                    "paymentsMoved": payment_count,
                    "usersMerged": len(source_users),
                    "salesMerged": len(source_sales),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error merging offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeMovePaymentView(APIView):
    """
    POST /office/movePayment/
    Move payment between offices.
    """

    def post(self, request):
        try:
            payment_id = request.data.get("paymentId")
            from_office_id = request.data.get("fromOfficeId")
            to_office_id = request.data.get("toOfficeId")

            if not all([payment_id, from_office_id, to_office_id]):
                return Response(
                    {"error": "paymentId, fromOfficeId, and toOfficeId are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Verify offices exist
            Office.objects.using("fred").get(pk=int(from_office_id))
            Office.objects.using("fred").get(pk=int(to_office_id))

            result = PaymentService.move_payment(
                int(payment_id), int(from_office_id), int(to_office_id)
            )
            return Response(result, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": "Office not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error moving payment: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# REPORT VIEWS
# =============================================================================


class OfficeSummaryReportView(APIView):
    """
    POST /office/summaryreport/
    Get summary report data.
    """

    def post(self, request):
        try:
            office_id = request.data.get("officeId")
            start_date = request.data.get("startDate")
            end_date = request.data.get("endDate")

            if not office_id or not start_date or not end_date:
                return Response(
                    {
                        "error": True,
                        "message": "Missing required parameters: officeId, startDate, or endDate",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            params = {
                "office_id": office_id,
                "start_date": start_date,
                "end_date": end_date,
            }

            summary_sql = """
                WITH
                all_active_skus AS (
                    SELECT DISTINCT sku FROM vi_items WHERE officeid = %(office_id)s
                    UNION
                    SELECT DISTINCT med.formulacode as sku FROM vi_proceeds vp
                    JOIN rx ON vp.rxid = rx.id JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s
                ),
                office_info AS (SELECT DISTINCT o.name as office_name FROM office o WHERE o.id = %(office_id)s),
                proceeds_by_sku AS (
                    SELECT med.formulacode AS sku, SUM(vp.qty) AS total_qty, SUM(vp.proceeds) AS total_proceeds,
                           SUM(vp.shippingandhandlingfee) AS total_sh_fees, SUM((vp.viprice * vp.qty) - vp.discounttotal) AS viprice
                    FROM vi_proceeds vp JOIN rx ON vp.rxid = rx.id JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY med.formulacode
                ),
                proceeds_by_sku_old AS (
                    SELECT med.formulacode AS sku, SUM(vp.qty) AS total_qty
                    FROM vi_proceeds vp JOIN rx ON vp.rxid = rx.id JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s AND vp.created < TO_DATE(%(start_date)s, 'DD/MM/YYYY')
                    GROUP BY med.formulacode
                ),
                beginning_inventory_by_sku AS (
                    SELECT vi_items.sku, COALESCE(SUM(vi_items.qty), 0) - COALESCE(pb.total_qty, 0) AS beginning_inventory
                    FROM vi_items LEFT JOIN proceeds_by_sku_old pb ON pb.sku = vi_items.sku
                    WHERE vi_items.officeid = %(office_id)s AND vi_items.transactiondate < TO_DATE(%(start_date)s, 'DD/MM/YYYY')
                    GROUP BY vi_items.sku, pb.total_qty
                ),
                auto_replenishment_by_sku AS (
                    SELECT vi_items.sku, COALESCE(SUM(vi_items.qty), 0) AS auto_replenishment_qty,
                           COALESCE(SUM(vi_items.itemtotalamount), 0) AS auto_replenishment_cost
                    FROM vi_items LEFT JOIN vi_orders vo ON vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND vo.ordersequencetype = 'AUTO'
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                all_inventory_by_sku AS (
                    SELECT vi_items.sku, COALESCE(SUM(vi_items.qty), 0) AS total_inventory_change
                    FROM vi_items WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                first_stock_dates AS (
                    SELECT vi_items.sku, vo.transactiondate AS date_of_first_stock
                    FROM vi_items JOIN vi_orders vo ON vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND vo.ordersequencetype = 'FIRST'
                ),
                last_replenish_dates AS (
                    SELECT vi_items.sku, MAX(vo.transactiondate) AS date_of_last_replenish
                    FROM vi_items JOIN vi_orders vo ON vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND (vo.ordersequencetype = 'AUTO' or vo.ordersequencetype = 'MANUAL')
                    AND vo.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                average_purchase_cost_by_sku AS (
                    SELECT vi_items.sku, AVG(vi_items.vicost) AS avg_purchase_cost
                    FROM vi_items WHERE vi_items.officeid = %(office_id)s AND vi_items.vicost IS NOT NULL
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                value_per_sku AS (
                    SELECT vi_items.sku, SUM(vi_items.itemtotalamount::NUMERIC) / SUM(vi_items.qty) AS average_price_per_sku
                    FROM vi_items WHERE vi_items.officeid = %(office_id)s
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                units_dispensed_by_sku AS (
                    SELECT med.formulacode AS sku, SUM(vp.qty::NUMERIC) AS dispensed_qty,
                           SUM(vp.qty::NUMERIC) * vps.average_price_per_sku AS dispensed_value
                    FROM vi_proceeds vp INNER JOIN rx ON rx.id = vp.rxid
                    INNER JOIN medication med ON med.ndc = rx.medicationid INNER JOIN value_per_sku vps ON vps.sku = med.formulacode
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY med.formulacode, vps.average_price_per_sku
                ),
                initial_purchases_by_sku AS (
                    SELECT vi_items.sku, COALESCE(SUM(vi_items.qty), 0) AS initial_purchase_qty,
                           COALESCE(SUM(vi_items.itemtotalamount::NUMERIC), 0) AS initial_purchase_amount
                    FROM vi_items INNER JOIN vi_orders ON vi_orders.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND vi_orders.ordersequencetype = 'FIRST'
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                midmonth_replenishments_by_sku AS (
                    SELECT vi_items.sku, COALESCE(SUM(vi_items.qty), 0) AS midmonth_replenish_qty,
                           COALESCE(SUM(vi_items.itemtotalamount::NUMERIC), 0) AS midmonth_replenish_amount
                    FROM vi_items INNER JOIN vi_orders ON vi_orders.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND (vi_orders.ordersequencetype = 'AUTO' OR vi_orders.ordersequencetype = 'MANUAL')
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                eom_replenishments_by_sku AS (
                    SELECT vi_items.sku, COALESCE(SUM(vi_items.qty), 0) AS eom_replenish_qty,
                           COALESCE(SUM(vi_items.itemtotalamount::NUMERIC), 0) AS eom_replenish_amount
                    FROM vi_items INNER JOIN vi_orders ON vi_orders.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND vi_orders.ordersequencetype = 'EOM'
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                summary_by_sku AS (
                    SELECT sku.sku AS product, oi.office_name,
                        COALESCE(bi.beginning_inventory, 0) AS beginning_inventory, COALESCE(pb.total_qty, 0) AS dispensed_units,
                        COALESCE(pb.viprice, 0) AS viprice, COALESCE(pb.total_proceeds, 0) AS dispensed_payment,
                        COALESCE(pb.total_sh_fees, 0) AS sh_fees, COALESCE(ar.auto_replenishment_qty, 0) AS inventory_replenishment,
                        COALESCE(ar.auto_replenishment_cost, 0) AS replenishment_cost,
                        (COALESCE(bi.beginning_inventory, 0) + COALESCE(ai.total_inventory_change, 0) - COALESCE(ud.dispensed_qty, 0)) AS ending_inventory,
                        (COALESCE(pb.total_proceeds, 0) - COALESCE(ar.auto_replenishment_cost, 0) - COALESCE(er.eom_replenish_amount, 0)) AS balance_owed,
                        (COALESCE(pb.viprice, 0) - COALESCE(ar.auto_replenishment_cost, 0) - COALESCE(er.eom_replenish_amount, 0)) AS net_Proceeds_before_sh,
                        fs.date_of_first_stock, lr.date_of_last_replenish,
                        CAST(ROUND(CAST((COALESCE(bi.beginning_inventory, 0) + COALESCE(ai.total_inventory_change, 0) - COALESCE(ud.dispensed_qty, 0)) * COALESCE(apc.avg_purchase_cost, 0) AS NUMERIC), 2) AS NUMERIC(15,2)) AS value_of_ending_inventory,
                        COALESCE(ip.initial_purchase_qty, 0) AS initial_purchase_qty, COALESCE(ip.initial_purchase_amount, 0) AS initial_purchase_amount,
                        COALESCE(mr.midmonth_replenish_qty, 0) AS midmonth_replenish_qty, COALESCE(mr.midmonth_replenish_amount, 0) AS midmonth_replenish_amount,
                        COALESCE(er.eom_replenish_qty, 0) AS eom_replenish_qty, COALESCE(er.eom_replenish_amount, 0) AS eom_replenish_amount,
                        COALESCE(ud.dispensed_value, 0) AS dispensed_value
                    FROM all_active_skus sku CROSS JOIN office_info oi
                    LEFT JOIN proceeds_by_sku pb ON sku.sku = pb.sku LEFT JOIN units_dispensed_by_sku ud ON sku.sku = ud.sku
                    LEFT JOIN auto_replenishment_by_sku ar ON sku.sku = ar.sku LEFT JOIN all_inventory_by_sku ai ON sku.sku = ai.sku
                    LEFT JOIN beginning_inventory_by_sku bi ON sku.sku = bi.sku LEFT JOIN first_stock_dates fs ON sku.sku = fs.sku
                    LEFT JOIN last_replenish_dates lr ON sku.sku = lr.sku LEFT JOIN average_purchase_cost_by_sku apc ON sku.sku = apc.sku
                    LEFT JOIN initial_purchases_by_sku ip ON sku.sku = ip.sku LEFT JOIN midmonth_replenishments_by_sku mr ON sku.sku = mr.sku
                    LEFT JOIN eom_replenishments_by_sku er ON sku.sku = er.sku
                )
                SELECT * FROM summary_by_sku ORDER BY product
            """

            profit_sql = """
                WITH proceeds_by_doctor_sku AS (
                    SELECT med.formulacode AS sku, vp.doctorid, SUM(vp.qty) AS doctor_qty,
                           SUM(vp.proceeds) AS gross_proceeds, SUM(COALESCE(vp.discounttotal, 0)) AS total_discount,
                           SUM(vp.proceeds) AS doctor_proceeds, SUM(vp.shippingandhandlingfee) AS total_sh_fees
                    FROM vi_proceeds vp JOIN rx ON vp.rxid = rx.id JOIN medication med ON rx.medicationid = med.ndc
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY med.formulacode, vp.doctorid
                ),
                total_dispensed_by_sku AS (
                    SELECT sku, SUM(doctor_qty) AS total_qty, SUM(doctor_proceeds) AS total_doctor_proceeds
                    FROM proceeds_by_doctor_sku GROUP BY sku
                ),
                replenishment_cost_by_sku AS (
                    SELECT vi_items.sku, SUM(vi_items.itemtotalamount) AS total_replenishment_cost
                    FROM vi_items LEFT JOIN vi_orders vo on vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND vo.ordersequencetype = 'AUTO'
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                eom_replenishment_cost_by_sku AS (
                    SELECT vi_items.sku, SUM(vi_items.itemtotalamount) AS total_eom_replenishment_cost
                    FROM vi_items LEFT JOIN vi_orders vo on vo.id = vi_items.orderid
                    WHERE vi_items.officeid = %(office_id)s AND vo.ordersequencetype = 'EOM'
                    AND vi_items.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    GROUP BY vi_items.sku
                ),
                doctor_profit_calculation AS (
                    SELECT pds.sku, pds.doctorid, pds.doctor_qty, pds.doctor_proceeds, tds.total_qty, tds.total_doctor_proceeds,
                        COALESCE(rcs.total_replenishment_cost, 0) AS total_replenishment_cost,
                        COALESCE(ercs.total_eom_replenishment_cost, 0) AS total_eom_replenishment_cost,
                        (COALESCE(rcs.total_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty) AS allocated_auto_cost,
                        (COALESCE(ercs.total_eom_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty) AS allocated_eom_cost,
                        (pds.doctor_proceeds - (COALESCE(rcs.total_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty) -
                         (COALESCE(ercs.total_eom_replenishment_cost, 0) * pds.doctor_qty::numeric / tds.total_qty)) AS doctor_profit
                    FROM proceeds_by_doctor_sku pds JOIN total_dispensed_by_sku tds ON pds.sku = tds.sku
                    LEFT JOIN replenishment_cost_by_sku rcs ON pds.sku = rcs.sku
                    LEFT JOIN eom_replenishment_cost_by_sku ercs ON pds.sku = ercs.sku
                ),
                doctor_info AS (SELECT doc.id as doctorid, doc.npi, doc.name FROM doctor doc),
                office_info AS (SELECT id AS officeid, viproceedstype FROM office WHERE id = %(office_id)s),
                doctor_split AS (SELECT id, splitpercent, npi, officeid, vendorid FROM vi_doctor WHERE officeid = %(office_id)s),
                doctor_shares AS (
                    SELECT dpc.doctorid, dpc.sku, dpc.doctor_qty, di.name, di.npi, dpc.doctor_proceeds,
                        dpc.allocated_auto_cost, dpc.allocated_eom_cost, dpc.doctor_profit, oi.viproceedstype,
                        CASE WHEN oi.viproceedstype = 1 THEN 0 WHEN oi.viproceedstype = 2 THEN 100
                             WHEN oi.viproceedstype = 3 THEN COALESCE(ds.splitpercent, 0) ELSE 0 END AS splitpercent,
                        CASE WHEN ds.vendorid IS NULL THEN true ELSE false END AS isescrowheld
                    FROM doctor_profit_calculation dpc JOIN doctor_info di ON dpc.doctorid = di.doctorid
                    CROSS JOIN office_info oi LEFT JOIN doctor_split ds ON di.npi = ds.npi AND ds.officeid = %(office_id)s
                ),
                final_shares AS (
                    SELECT doctorid, name, npi, doctor_profit, viproceedstype, splitpercent, isescrowheld,
                        CASE WHEN viproceedstype IS NULL OR viproceedstype = 1 THEN 0 WHEN viproceedstype = 2 THEN doctor_profit
                             WHEN viproceedstype = 3 THEN doctor_profit * COALESCE(splitpercent, 0) / 100.0 ELSE 0 END AS doctor_share,
                        CASE WHEN viproceedstype IS NULL OR viproceedstype = 1 THEN doctor_profit WHEN viproceedstype = 2 THEN 0
                             WHEN viproceedstype = 3 THEN doctor_profit * (100.0 - COALESCE(splitpercent, 0)) / 100.0 ELSE doctor_profit END AS office_share
                    FROM doctor_shares
                )
                SELECT doctorid, name, splitpercent, SUM(doctor_share) AS doctor_share, SUM(office_share) AS office_share, BOOL_OR(isescrowheld) AS isescrowheld
                FROM final_shares GROUP BY doctorid, splitpercent, name ORDER BY doctorid
            """

            with connections["fred"].cursor() as cursor:
                cursor.execute(summary_sql, params)
                summary_result = [
                    dict(zip([c[0] for c in cursor.description], row))
                    for row in cursor.fetchall()
                ]
                cursor.execute(profit_sql, params)
                profit_result = [
                    dict(zip([c[0] for c in cursor.description], row))
                    for row in cursor.fetchall()
                ]

            return Response(
                {"summary": summary_result, "profitShare": profit_result},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error getting summary report: {e}")
            return Response(
                {"error": True, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeInventoryReportView(APIView):
    """
    POST /office/inventoryreport/
    Get inventory report data.
    """

    def post(self, request):
        try:
            office_id = request.data.get("officeId")
            start_date = request.data.get("startDate")
            end_date = request.data.get("endDate")

            if not office_id or not start_date or not end_date:
                return Response(
                    {
                        "error": True,
                        "message": "Missing required parameters: officeId, startDate, or endDate",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            query = """
                WITH proceeds AS (
                    SELECT o.name AS officename, med.formulacode AS sku, vp.qty, vp.proceeds, vp.doctorid,
                           doc.npi, doc.name, vp.created, vp.servicefee + vp.shippingandhandlingfee as feesperagreement,
                           vp.discounttotal, vp.viprice
                    FROM vi_proceeds vp JOIN rx ON vp.rxid = rx.id JOIN medication med ON rx.medicationid = med.ndc
                    JOIN doctor doc ON vp.doctorid = doc.id JOIN office o ON vp.officeid = o.id
                    WHERE vp.officeid = %(office_id)s
                    AND vp.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                ),
                combined_transactions AS (
                    SELECT o.name AS office_name, vo.transactiondate AS date, vi.sku AS product,
                           vo.ordersequencetype AS order_type, vi.vicost AS unit_cost, vi.qty AS purchased_units,
                           0 AS dispensed_units, 0 AS dispensed_payment, 0 AS discount, vi.expirationdate AS product_exp_date,
                           0 AS fees_per_agreement, 0 as proceeds, NULL AS doctor_name, 0 as doctorid, 'IN' AS record_type
                    FROM vi_orders vo JOIN office o ON vo.officeid = o.id
                    JOIN vi_items vi ON vi.officeid = vo.officeid AND vo.id = vi.orderid
                    WHERE vo.officeid = %(office_id)s
                    AND vo.transactiondate BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
                    UNION ALL
                    SELECT p.officename AS office_name, p.created AS date, p.sku AS product, NULL AS order_type, NULL AS unit_cost,
                           0 AS purchased_units, p.qty AS dispensed_units, p.viprice AS dispensed_payment, p.discounttotal AS discount,
                           NULL AS product_exp_date, p.feesperagreement AS fees_per_agreement, p.proceeds as proceeds,
                           p.name AS doctor_name, p.doctorid as doctorid, 'OUT' AS record_type
                    FROM proceeds p
                )
                SELECT office_name, date, product, order_type, unit_cost, purchased_units, dispensed_units,
                       dispensed_units * dispensed_payment as dispensed_payment, discount,
                       SUM(purchased_units - dispensed_units) OVER (PARTITION BY product ORDER BY date ASC, record_type DESC ROWS UNBOUNDED PRECEDING) AS balanced_units,
                       product_exp_date, fees_per_agreement, proceeds, doctor_name, doctorid, record_type
                FROM combined_transactions
            """

            with connections["fred"].cursor() as cursor:
                cursor.execute(
                    query,
                    {
                        "office_id": office_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                result = [
                    dict(zip([c[0] for c in cursor.description], row))
                    for row in cursor.fetchall()
                ]

            return Response(
                {"success": True, "result": result, "count": len(result)},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error getting inventory report: {e}")
            return Response(
                {
                    "error": True,
                    "message": "Failed to generate inventory report.",
                    "debug": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeEscrowReportView(APIView):
    """
    POST /office/escrowreport/
    Get escrow report data.
    """

    def post(self, request):
        try:
            office_id = request.data.get("officeId")
            start_date = request.data.get("startDate")
            end_date = request.data.get("endDate")

            if not office_id or not start_date or not end_date:
                return Response(
                    {
                        "error": True,
                        "message": "Missing required parameters: officeId, startDate, or endDate",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            query = """
                SELECT o.name AS office_name, p.created AS dispensed_date, m.formulacode AS sku,
                       p.qty AS dispensed_unit, p.qty * p.viprice AS dispensed_amount, r.patientid AS patientid,
                       d.name AS doctor_name, r.id AS fredid, vid.vendorid AS vendorid
                FROM vi_profits_report vpr
                JOIN LATERAL jsonb_array_elements(vpr.payload::jsonb -> 'escrowHeld') AS escrow(entry) ON TRUE
                JOIN LATERAL jsonb_array_elements_text(escrow.entry -> 'proceedIdList') AS pid(proceed_id) ON TRUE
                JOIN vi_proceeds p ON p.id = pid.proceed_id::int JOIN rx r ON r.id = p.rxid
                JOIN office o ON vpr.officeid = o.id::int JOIN medication m ON m.ndc = r.medicationid
                JOIN doctor d ON d.npi = (escrow.entry ->> 'fredDoctorNPI')
                JOIN vi_doctor vid ON vid.npi = (escrow.entry ->> 'fredDoctorNPI')
                WHERE vpr.officeid = %(office_id)s
                AND vpr.created BETWEEN TO_DATE(%(start_date)s, 'DD/MM/YYYY') AND TO_DATE(%(end_date)s, 'DD/MM/YYYY') + INTERVAL '1' DAY - INTERVAL '1' SECOND
            """

            with connections["fred"].cursor() as cursor:
                cursor.execute(
                    query,
                    {
                        "office_id": office_id,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                )
                result = [
                    dict(zip([c[0] for c in cursor.description], row))
                    for row in cursor.fetchall()
                ]

            return Response(
                {"success": True, "result": result, "count": len(result)},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error getting escrow report: {e}")
            return Response(
                {
                    "error": True,
                    "message": "Failed to generate escrow report.",
                    "debug": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# SKINCARE & DIO VIEWS
# =============================================================================


class OfficeSkincareParingsView(APIView):
    """
    GET /office/skincare-pairings/{pk}/
    Get skincare pairings.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)

            pairings = [
                {
                    "id": p.id,
                    "sku": p.sku,
                    "productName": p.product_name,
                    "orderId": p.order_id,
                    "orderStatus": p.order_status,
                    "productNetRevenue": p.product_net_revenue,
                    "dateCreated": (
                        p.date_created.isoformat() if p.date_created else None
                    ),
                    "prescriberNpi": p.prescribernpi,
                }
                for p in Skincarepairings.objects.using("fred")
                .filter(fredofficeid=str(pk))
                .order_by("-date_created")
            ]

            return Response(pairings, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting skincare pairings for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeProviderSkincarePairingsView(APIView):
    """
    GET /office/provider-skincare-pairings/{pk}/
    Get provider skincare pairings.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)

            pairings = (
                Skincarepairings.objects.using("fred")
                .filter(fredofficeid=str(pk))
                .values("prescribernpi")
                .annotate(
                    total_revenue=Sum("product_net_revenue"),
                    order_count=Count("order_id", distinct=True),
                    product_count=Count("id"),
                )
            )

            results = []
            for p in pairings:
                npi = p["prescribernpi"]
                doctor = (
                    Doctor.objects.using("fred").filter(npi=npi).first()
                    if npi
                    else None
                )
                results.append(
                    {
                        "npi": npi,
                        "doctorName": doctor.name if doctor else None,
                        "totalRevenue": p["total_revenue"] or 0,
                        "orderCount": p["order_count"],
                        "productCount": p["product_count"],
                    }
                )

            return Response(results, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(
                f"Error getting provider skincare pairings for office {pk}: {e}"
            )
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeDioBySkuView(APIView):
    """
    GET /office/getdiobysku/{pk}/
    Get DIO by SKU.
    """

    def get(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)

            sku = request.query_params.get("sku")
            qs = DioItems.objects.using("fred").filter(officeid=pk)
            if sku:
                qs = qs.filter(formulacode__icontains=sku)

            items = []
            for item in qs:
                item_data = {
                    "id": item.id,
                    "officeId": item.officeid,
                    "formulacode": item.formulacode,
                    "active": item.active,
                    "created": item.created.isoformat() if item.created else None,
                    "medication": None,
                }
                try:
                    med = Medication.objects.using("fred").get(
                        formulacode=item.formulacode
                    )
                    item_data["medication"] = {
                        "ndc": med.ndc,
                        "formula": med.formula,
                        "brand_name": med.brand_name,
                        "dosage": med.dosage,
                    }
                except Medication.DoesNotExist:
                    pass
                items.append(item_data)

            return Response(items, status=status.HTTP_200_OK)

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting DIO items for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeUpdateSkusView(APIView):
    """
    PUT /office/updateskus/{pk}/
    Update SKUs.
    """

    def put(self, request, pk):
        try:
            Office.objects.using("fred").get(pk=pk)

            skus = request.data.get("skus", [])
            if not isinstance(skus, list):
                return Response(
                    {"error": "skus must be a list"}, status=status.HTTP_400_BAD_REQUEST
                )

            added, updated, deactivated = 0, 0, 0

            with transaction.atomic(using="fred"):
                for sku_data in skus:
                    formulacode = sku_data.get("formulacode")
                    active = sku_data.get("active", True)
                    if not formulacode:
                        continue

                    existing = (
                        DioItems.objects.using("fred")
                        .filter(officeid=pk, formulacode=formulacode)
                        .first()
                    )
                    if existing:
                        if existing.active != active:
                            existing.active = active
                            existing.save(using="fred")
                            updated += 1 if active else 0
                            deactivated += 0 if active else 1
                    else:
                        DioItems.objects.using("fred").create(
                            officeid=pk, formulacode=formulacode, active=active
                        )
                        added += 1

            logger.info(
                f"Updated SKUs for office #{pk}: added={added}, updated={updated}, deactivated={deactivated}"
            )
            return Response(
                {
                    "officeId": pk,
                    "added": added,
                    "updated": updated,
                    "deactivated": deactivated,
                    "success": True,
                },
                status=status.HTTP_200_OK,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error updating SKUs for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeLoadDioView(APIView):
    """
    GET /office/loadDIO/
    Load DIO configuration.
    """

    def get(self, request):
        try:
            office_id = request.query_params.get("office_id")
            if office_id:
                office_id = int(office_id)
                offices = [Office.objects.using("fred").get(pk=office_id)]
            else:
                offices = (
                    Office.objects.using("fred")
                    .filter(dio2=True)
                    .exclude(name__contains="(x)")
                )

            dio_data = []
            for office in offices:
                items = []
                for item in DioItems.objects.using("fred").filter(
                    officeid=office.id, active=True
                ):
                    item_data = {
                        "id": item.id,
                        "formulacode": item.formulacode,
                        "active": item.active,
                    }
                    try:
                        med = Medication.objects.using("fred").get(
                            formulacode=item.formulacode
                        )
                        item_data["medication"] = {
                            "ndc": med.ndc,
                            "formula": med.formula,
                            "brand_name": med.brand_name,
                            "dosage": med.dosage,
                            "size": med.size,
                        }
                    except Medication.DoesNotExist:
                        item_data["medication"] = None
                    items.append(item_data)

                dio_data.append(
                    {
                        "officeId": office.id,
                        "officeName": office.name,
                        "dio2Enabled": office.dio2,
                        "virtualInventoryEnabled": office.virtualinventoryenabled,
                        "viStatus": office.vi_status,
                        "replenishmentOptout": office.replenishmentoptout,
                        "itemCount": len(items),
                        "items": items,
                    }
                )

            return Response(
                {"officeCount": len(dio_data), "offices": dio_data},
                status=status.HTTP_200_OK,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": "Office not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error loading DIO: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSaveDioShipmentView(APIView):
    """
    POST /office/savedioshipment/
    Save DIO shipment.
    """

    def post(self, request):
        try:
            office_id = request.data.get("officeId")
            if not office_id:
                return Response(
                    {"error": "officeId is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office_id = int(office_id)
            Office.objects.using("fred").get(pk=office_id)

            user_id = request.query_params.get("user_id", 0)
            items = request.data.get("items", [])
            tracking = request.data.get("tracking")
            carrier = request.data.get("carrier")
            notes = request.data.get("notes")
            processed_items = []

            with transaction.atomic(using="fred"):
                for item in items:
                    formulacode = item.get("formulacode")
                    if not formulacode:
                        continue
                    dio_item, created = DioItems.objects.using("fred").get_or_create(
                        officeid=office_id,
                        formulacode=formulacode,
                        defaults={"active": True},
                    )
                    processed_items.append(
                        {
                            "formulacode": formulacode,
                            "qty": item.get("qty", 0),
                            "lot": item.get("lot"),
                            "expiration": item.get("expiration"),
                            "dioItemId": dio_item.id,
                            "created": created,
                        }
                    )

                log_office_history(
                    office_id=office_id,
                    user_id=int(user_id) if user_id else 0,
                    triggered_action="saveDioShipmentAction",
                    old_data=None,
                    new_data=json.dumps(
                        {
                            "tracking": tracking,
                            "carrier": carrier,
                            "itemCount": len(processed_items),
                        }
                    ),
                )

            logger.info(
                f"Saved DIO shipment for office #{office_id}: {len(processed_items)} items"
            )
            return Response(
                {
                    "success": True,
                    "officeId": office_id,
                    "tracking": tracking,
                    "carrier": carrier,
                    "notes": notes,
                    "itemsProcessed": len(processed_items),
                    "items": processed_items,
                },
                status=status.HTTP_200_OK,
            )

        except Office.DoesNotExist:
            return Response(
                {"error": "Office not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error saving DIO shipment: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeDioOptoutView(APIView):
    """
    GET    /office/dio/optout/{pk}/ - Get opt out status
    POST   /office/dio/optout/{pk}/ - Opt out
    DELETE /office/dio/optout/{pk}/ - Opt back in
    """

    def get(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            return Response(
                {
                    "officeId": pk,
                    "officeName": office.name,
                    "replenishmentOptout": office.replenishmentoptout,
                    "dio2Enabled": office.dio2,
                    "virtualInventoryEnabled": office.virtualinventoryenabled,
                    "viStatus": office.vi_status,
                },
                status=status.HTTP_200_OK,
            )
        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error getting DIO opt out status for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            user_id = request.query_params.get("user_id", 0)

            with transaction.atomic(using="fred"):
                old_value = office.replenishmentoptout
                office.replenishmentoptout = True
                office.save(using="fred")
                log_office_history(
                    office_id=pk,
                    user_id=int(user_id) if user_id else 0,
                    triggered_action="dioOptoutAction",
                    old_data=json.dumps({"replenishmentoptout": old_value}),
                    new_data=json.dumps({"replenishmentoptout": True}),
                )

            logger.info(f"Office #{pk} opted out of DIO")
            return Response(
                {
                    "success": True,
                    "officeId": pk,
                    "replenishmentOptout": True,
                    "message": "Office has been opted out of DIO replenishment",
                },
                status=status.HTTP_200_OK,
            )
        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error opting out of DIO for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            office = Office.objects.using("fred").get(pk=pk)
            user_id = request.query_params.get("user_id", 0)

            with transaction.atomic(using="fred"):
                old_value = office.replenishmentoptout
                office.replenishmentoptout = False
                office.save(using="fred")
                log_office_history(
                    office_id=pk,
                    user_id=int(user_id) if user_id else 0,
                    triggered_action="dioOptinAction",
                    old_data=json.dumps({"replenishmentoptout": old_value}),
                    new_data=json.dumps({"replenishmentoptout": False}),
                )

            logger.info(f"Office #{pk} opted in to DIO")
            return Response(
                {
                    "success": True,
                    "officeId": pk,
                    "replenishmentOptout": False,
                    "message": "Office has been opted back in to DIO replenishment",
                },
                status=status.HTTP_200_OK,
            )
        except Office.DoesNotExist:
            return Response(
                {"error": f"Office with id {pk} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Error opting in to DIO for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OfficeListView",
    "OfficeDetailView",
    "OfficeCreateView",
    "OfficeFastListView",
    "OfficeUsersView",
    "OfficeSalesView",
    "UserOfficesView",
    "OfficeSetUsersView",
    "OfficeSetSalesView",
    "OfficeAddUserView",
    "OfficeViewView",
    "OfficePerformanceView",
    "OfficeContactsView",
    "OfficeMedicationsView",
    "OfficePrescribersView",
    "OfficePatientsView",
    "OfficeRxView",
    "OfficePendingRxView",
    "OfficePendingPaymentsView",
    "OfficeListPaginatedView",
    "OfficeUpdateVendorIdView",
    "OfficeByNetsuiteIdView",
    "OfficeListAltView",
    "OfficeListNewView",
    "OfficeListUpdatedView",
    "OfficeUnassignedPaginatedView",
    "OfficeListWithAddressView",
    "OfficePaidRxsView",
    "OfficeMovePaymentView",
    "OfficeCanPrescribeView",
    "OfficeLeafletView",
    "OfficeQrView",
    "OfficeReportsView",
    "OfficeMergeView",
    "OfficeLeafletSampleView",
    "OfficeSummaryReportView",
    "OfficeInventoryReportView",
    "OfficeEscrowReportView",
    "OfficeSkincareParingsView",
    "OfficeProviderSkincarePairingsView",
    "OfficeDioBySkuView",
    "OfficeUpdateSkusView",
    "OfficeDioOptoutView",
    "OfficeSaveDioShipmentView",
    "OfficeLoadDioView",
]
