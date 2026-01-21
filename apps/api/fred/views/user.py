"""
User Views Module

Contains views/viewsets related to authentication and user management.

Legacy Controller Mapping: UsersController, SessionController
"""

import json
import logging
import secrets
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions.legacy import legacy_roles
from fred.models import Logs, Office, Payment, Rx, Rxfill, Shipment, Users
from fred.serializers.user import (
    SalesManagerAssignSerializer,
    SalesPerformanceQuerySerializer,
    UserAddSerializer,
    UserListSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserErrorCodes,
    _hash_password,
)
from fred.serializers import FredLogsSerializer
from fred.utils.logs import create_log

logger = logging.getLogger(__name__)


def _get_users_by_role(role, active_only=False):
    users = Users.objects.using("fred").filter(role=role)
    if active_only:
        users = users.filter(status="active")
    return users.order_by("first_name")


def _serialize_users(users):
    return UserListSerializer(users, many=True).data


def _user_full_name(user):
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return name or user.email or f"User #{user.id}"


def _has_error_code(errors, code):
    if isinstance(errors, (list, tuple)):
        return any(_has_error_code(item, code) for item in errors)
    if isinstance(errors, dict):
        return any(_has_error_code(item, code) for item in errors.values())
    return getattr(errors, "code", None) == code


def _user_add_error_response(errors):
    if _has_error_code(errors, "already_exists"):
        return Response(
            {"error": "User already exists", "code": UserErrorCodes.ERROR_ALREADY_EXISTS},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if _has_error_code(errors, "invalid_role"):
        return Response(
            {
                "error": "Invalid user role",
                "code": UserErrorCodes.ERROR_UNABLE_CREATE_USER,
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    if _has_error_code(errors, "unable_create"):
        return Response(
            {
                "error": "Unable to create user",
                "code": UserErrorCodes.ERROR_UNABLE_CREATE_USER,
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    return Response(
        {"error": "Invalid data", "details": errors},
        status=status.HTTP_400_BAD_REQUEST,
    )


def _get_office_ids_by_sales(sales_id):
    office_ids = []
    for office_id, sales in Office.objects.using("fred").values_list("id", "sales"):
        if not sales:
            continue
        try:
            sales_list = json.loads(sales)
        except (TypeError, ValueError):
            continue
        if not isinstance(sales_list, list):
            continue
        if any(str(sales_id) == str(item) for item in sales_list):
            office_ids.append(office_id)
    return office_ids


def _get_rx_count_by_offices(office_ids, start, end, rx_type):
    if not office_ids:
        return 0
    rx_ids = (
        Rx.objects.using("fred")
        .filter(officeid__in=office_ids)
        .values_list("id", flat=True)
    )
    qs = Rxfill.objects.using("fred").filter(rxid__in=rx_ids, type=rx_type)
    if start:
        qs = qs.filter(created__gt=start)
    if end:
        qs = qs.filter(created__lt=end)
    return qs.count()


def _get_shipment_count_by_offices(office_ids, start, end):
    if not office_ids:
        return 0
    rx_ids = (
        Rx.objects.using("fred")
        .filter(officeid__in=office_ids)
        .values_list("id", flat=True)
    )
    shipments = Shipment.objects.using("fred")
    if start:
        shipments = shipments.filter(created__gt=start)
    if end:
        shipments = shipments.filter(created__lt=end)
    shipment_ids = shipments.values_list("id", flat=True)
    return (
        Rxfill.objects.using("fred")
        .filter(rxid__in=rx_ids, shipmentid__in=shipment_ids)
        .count()
    )


def _get_payment_count_by_offices(office_ids, start, end, payment_type):
    if not office_ids:
        return 0
    payments = Payment.objects.using("fred").filter(officeid__in=office_ids)
    if payment_type:
        payments = payments.filter(type=payment_type)
    if start:
        payments = payments.filter(created__gt=start)
    if end:
        payments = payments.filter(created__lt=end)
    return payments.count()


class UserListView(APIView):
    """
    GET /users/

    List all users.

    Migrated from PHP: UsersController::getAction()
    """

    permission_classes = [legacy_roles("admin")]

    def get(self, request):
        try:
            users = Users.objects.using("fred").order_by("id")
            if not users.exists():
                return Response(
                    {
                        "error": "Users table empty",
                        "code": UserErrorCodes.ERROR_USER_NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserDetailView(generics.RetrieveAPIView):
    """
    GET /users/{id}/

    Get a single user by ID.

    Migrated from PHP: UsersController::getOneAction()
    """

    permission_classes = [legacy_roles("admin")]
    queryset = Users.objects.using("fred")
    serializer_class = UserSerializer

    def put(self, request, pk):
        try:
            user = Users.objects.using("fred").get(pk=pk)
        except Users.DoesNotExist:
            return Response(
                {"error": "User not found", "code": UserErrorCodes.ERROR_USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        status_value = serializer.validated_data.get("status")
        if status_value in {"active", "inactive"}:
            user.pass_field = _hash_password(secrets.token_hex(8))
            actor_id = getattr(request.user, "id", None)
            log_message = (
                "User activated"
                if status_value == "active"
                else "User inactivated"
            )
            create_log(actor_id, user.id, "user", "app", log_message)

        try:
            serializer.save()
        except Exception as e:
            logger.error(f"Error updating user {pk}: {e}")
            return Response(
                {
                    "error": "Unable to update user",
                    "code": UserErrorCodes.ERROR_UNABLE_UPDATE_USER,
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return Response(status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            user = Users.objects.using("fred").get(pk=pk)
        except Users.DoesNotExist:
            return Response(
                {"error": "User not found", "code": UserErrorCodes.ERROR_USER_NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            deleted, _ = user.delete(using="fred")
            if not deleted:
                return Response(
                    {
                        "error": "Unable to delete user",
                        "code": UserErrorCodes.ERROR_UNABLE_DELETE_USER,
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
        except Exception as e:
            logger.error(f"Error deleting user {pk}: {e}")
            return Response(
                {
                    "error": "Unable to delete user",
                    "code": UserErrorCodes.ERROR_UNABLE_DELETE_USER,
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        actor_id = getattr(request.user, "id", None)
        create_log(actor_id, pk, "user", "app", f"User #{pk} has been deleted")

        return Response(status=status.HTTP_200_OK)


class UserAddView(APIView):
    """
    POST /users/add/

    Create a new user.

    Migrated from PHP: UsersController::addAction()
    """

    permission_classes = [legacy_roles("admin")]

    def post(self, request):
        serializer = UserAddSerializer(data=request.data)
        if not serializer.is_valid():
            return _user_add_error_response(serializer.errors)

        try:
            user = serializer.save()
        except serializers.ValidationError as exc:
            return _user_add_error_response(exc.detail)

        actor_id = getattr(request.user, "id", None)
        log_message = f"{_user_full_name(user)} has been registered as a {user.role}"
        create_log(actor_id, user.id, "user", "app", log_message)

        return Response({"id": user.id}, status=status.HTTP_201_CREATED)


class UserLogsView(APIView):
    """
    GET /users/logs/{id}/

    Get logs created by a user and logs about a user.

    Migrated from PHP: UsersController::getUserLogsAction()
    """

    permission_classes = [legacy_roles("admin")]

    def get(self, request, pk):
        try:
            by_user = (
                Logs.objects.using("fred")
                .filter(userid=pk)
                .order_by("-id")[:30]
            )
            about_user = Logs.objects.using("fred").filter(recordid=pk).order_by("-id")

            return Response(
                {
                    "byUser": FredLogsSerializer(by_user, many=True).data,
                    "aboutUser": FredLogsSerializer(about_user, many=True).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching user logs: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SalesPerformanceView(APIView):
    """
    GET /users/salesPerformance/

    Get sales performance summary for the given date range.

    Migrated from PHP: UsersController::salesPerformanceAction()
    """

    permission_classes = [legacy_roles("admin", "manager", "sales-manager")]

    def get(self, request):
        query_serializer = SalesPerformanceQuerySerializer(
            data=request.query_params
        )
        if not query_serializer.is_valid():
            return Response(
                {"error": query_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        start = query_serializer.validated_data.get("start")
        end = query_serializer.validated_data.get("end")

        if not start:
            start = timezone.make_aware(datetime(2020, 1, 1), dt_timezone.utc)
        if not end:
            end = timezone.now()

        role = getattr(request.user, "role", None)

        if role == "sales-manager":
            user_id = getattr(request.user, "id", None)
            if not user_id:
                return Response(
                    {"error": "User id is required for sales-manager role"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            sales_list = Users.objects.using("fred").filter(managerid=user_id).order_by(
                "id"
            )
        else:
            sales_list = (
                Users.objects.using("fred")
                .filter(role="sales")
                .order_by("first_name")
            )

        consultants = []
        for sales_user in sales_list:
            office_ids = _get_office_ids_by_sales(sales_user.id)
            if not office_ids:
                continue
            consultants.append(
                {
                    "id": sales_user.id,
                    "name": _user_full_name(sales_user),
                    "newrx": _get_rx_count_by_offices(
                        office_ids, start, end, "newrx"
                    ),
                    "refills": _get_rx_count_by_offices(
                        office_ids, start, end, "refills"
                    ),
                    "correctors": _get_rx_count_by_offices(
                        office_ids, start, end, "correctors"
                    ),
                    "shipments": _get_shipment_count_by_offices(
                        office_ids, start, end
                    ),
                    "payments": _get_payment_count_by_offices(
                        office_ids, start, end, "newrx"
                    ),
                }
            )

        return Response(consultants, status=status.HTTP_200_OK)


class CustomerServiceUsersView(APIView):
    """
    GET /users/customer-service/

    List active customer service users and managers.

    Migrated from PHP: UsersController::listCustomerServiceAction()
    """

    permission_classes = [
        legacy_roles(
            "admin",
            "customer-service",
            "customer-service-manager",
            "manager",
            "pharmacist",
        )
    ]

    def get(self, request):
        try:
            customer_service = _get_users_by_role(
                "customer-service", active_only=True
            )
            customer_service_manager = _get_users_by_role(
                "customer-service-manager", active_only=True
            )

            return Response(
                {
                    "customerService": _serialize_users(customer_service),
                    "customerServiceManager": _serialize_users(
                        customer_service_manager
                    ),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching customer service users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SalesActiveUsersView(APIView):
    """
    GET /users/sales/

    List active sales users.

    Migrated from PHP: UsersController::listSalesActiveAction()
    """

    permission_classes = [legacy_roles("admin", "manager")]

    def get(self, request):
        try:
            sales_users = _get_users_by_role("sales", active_only=True)
            return Response(
                _serialize_users(sales_users),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching sales users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SalesUsersView(APIView):
    """
    GET /users/sales/

    List sales users.

    Migrated from PHP: UsersController::listSalesAction()
    """

    permission_classes = [legacy_roles("admin", "manager")]

    def get(self, request):
        try:
            sales_users = _get_users_by_role("sales")
            return Response(
                _serialize_users(sales_users),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching sales users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SalesManagerUsersView(APIView):
    """
    GET /users/salesmanager/

    List sales manager users.

    Migrated from PHP: UsersController::listSalesManagerAction()
    """

    permission_classes = [legacy_roles("admin", "manager")]

    def get(self, request):
        try:
            sales_managers = _get_users_by_role("sales-manager")
            return Response(
                _serialize_users(sales_managers),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching sales manager users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        serializer = SalesManagerAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": True, "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sales_id = serializer.validated_data["sales"]
        manager_id = serializer.validated_data["manager"]

        try:
            sales_user = Users.objects.using("fred").get(pk=sales_id)
        except Users.DoesNotExist:
            return Response(
                {"error": True, "details": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if sales_user.role != "sales":
            return Response(
                {"error": True, "details": "User is not sales"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager_user = None
        if manager_id is None:
            new_manager_id = None
        else:
            try:
                manager_user = Users.objects.using("fred").get(pk=manager_id)
            except Users.DoesNotExist:
                return Response(
                    {"error": True, "details": "Manager not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if manager_user.role != "sales-manager":
                return Response(
                    {"error": True, "details": "Manager is not sales-manager"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_manager_id = manager_id if sales_user.managerid != manager_id else False

        if new_manager_id is False:
            return Response({"error": True}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sales_user.managerid = manager_id
            sales_user.save(using="fred")
        except Exception as e:
            logger.error(f"Error assigning sales manager: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if manager_user:
            logmsg = (
                f"{_user_full_name(sales_user)} has been assigned to "
                f"{_user_full_name(manager_user)}"
            )
        else:
            logmsg = f"{_user_full_name(sales_user)}'s manager has been removed"
        actor_id = getattr(request.user, "id", None)
        create_log(actor_id, sales_user.id, "user", "app", logmsg)

        return Response({"error": False}, status=status.HTTP_200_OK)


class PharmacistUsersView(APIView):
    """
    GET /users/pharmacist/

    List pharmacists and admins.

    Migrated from PHP: UsersController::listPharmacistAction()
    """

    permission_classes = [
        legacy_roles(
            "admin",
            "manager",
            "pharmacist",
            "customer-service",
            "customer-service-manager",
        )
    ]

    def get(self, request):
        try:
            pharmacists = _get_users_by_role("pharmacist")
            admins = _get_users_by_role("admin")
            return Response(
                {
                    "pharmacist": _serialize_users(pharmacists),
                    "admin": _serialize_users(admins),
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error fetching pharmacist users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PharmacyListUsersView(APIView):
    """
    GET /users/pharmacylist/

    List users in the pharmacy list.

    Migrated from PHP: UsersController::listPharmacyListAction()
    """

    permission_classes = [
        legacy_roles(
            "admin",
            "manager",
            "pharmacist",
            "customer-service",
            "customer-service-manager",
        )
    ]

    def get(self, request):
        try:
            users = Users.objects.using("fred").filter(pharmacylist=True)
            return Response(_serialize_users(users), status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching pharmacy list users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomerServiceListUsersView(APIView):
    """
    GET /users/cslist/

    List users in the customer service list.

    Migrated from PHP: UsersController::listCsListAction()
    """

    permission_classes = [
        legacy_roles(
            "admin",
            "manager",
            "pharmacist",
            "customer-service",
            "customer-service-manager",
        )
    ]

    def get(self, request):
        try:
            users = Users.objects.using("fred").filter(cslist=True)
            return Response(_serialize_users(users), status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching cs list users: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = [
    "UserListView",
    "UserDetailView",
    "UserAddView",
    "UserLogsView",
    "SalesPerformanceView",
    "CustomerServiceUsersView",
    "SalesActiveUsersView",
    "SalesUsersView",
    "SalesManagerUsersView",
    "PharmacistUsersView",
    "PharmacyListUsersView",
    "CustomerServiceListUsersView",
]
