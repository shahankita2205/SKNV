"""
Office Views Module

Contains views/viewsets related to office/location management.

Legacy Controller Mapping: OfficeController, OfficeTypeController, OfficeAgreementTypeController
"""

from datetime import datetime
import json
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings


from fred.serializers.office import (
    OfficeListSerializer,
    OfficeDetailSerializer,
    OfficeCreateSerializer,
    OfficeUpdateSerializer,
    OfficeCreateResponseSerializer,
    OfficeService,
    OfficeServiceException,
    OfficeErrorCodes,
)
from fred.serializers.officehistory import OfficeHistoryService


logger = logging.getLogger(__name__)


class OfficeListView(APIView):
    """
    API view for listing offices.

    Migrated from PHP: OfficeController::getAction()

    GET /offices/
    """

    def get(self, request):
        """
        Returns list of all offices.

        Response Format (matching PHP):
            [
                {"id": 1, "name": "Office 1", ...},
                {"id": 2, "name": "Office 2", ...},
                ...
            ]
        """
        try:
            logger.info("Fetching all offices")
            offices = OfficeService.get_all()
            serializer = OfficeListSerializer(offices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeDetailView(APIView):
    """
    API view for single office operations.

    Migrated from PHP: OfficeController::getOneAction(), updateAction(), deleteAction()

    GET    /offices/{id}/  - Get office details
    PUT    /offices/{id}/  - Update office
    DELETE /offices/{id}/  - Delete office
    """

    def get(self, request, pk):
        """
        Returns single office with address.

        Migrated from PHP: OfficeController::getOneAction()

        Access Control:
            - doctor/office roles: Can only access offices they belong to
            - other roles: Full access
        """
        try:
            logger.info(f"Fetching office with id: {pk}")

            # TODO: Get role and user_id from authentication
            # For now, allow full access
            role = request.query_params.get("role", "admin")
            user_id = request.query_params.get("user_id")
            user_id = int(user_id) if user_id else None

            result = OfficeService.get_one_with_address(pk, role, user_id)

            if result.get("error"):
                return Response({"error": True}, status=status.HTTP_403_FORBIDDEN)

            return Response(result, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            logger.error(f"Office service error: {e.message}")
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        """
        Updates an office.

        Migrated from PHP: OfficeController::updateAction()

        Role-based field access is enforced by serializer.
        """
        try:
            logger.info(f"Updating office {pk} with data: {request.data}")

            # Get office and old data for history logging
            office = OfficeService.get_one(pk)
            old_data = OfficeListSerializer(office).data

            # TODO: Get role from authentication
            role = request.query_params.get("role", "admin")

            serializer = OfficeUpdateSerializer(
                office, data=request.data, partial=True, context={"role": role}
            )

            if serializer.is_valid():
                updated_office = serializer.save()
                new_data = OfficeListSerializer(updated_office).data

                # Log history if data changed
                # TODO: Get user_id from authentication
                user_id = request.query_params.get("user_id", 0)
                if not OfficeService.check_same(old_data, new_data):
                    OfficeHistoryService.log(
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

        except OfficeServiceException as e:
            logger.error(f"Office service error: {e.message}")
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        """
        Deletes an office.

        Migrated from PHP: OfficeController::deleteAction()
        """
        try:
            logger.info(f"Deleting office with id: {pk}")

            # Get old data for history logging
            office = OfficeService.get_one(pk)
            old_data = OfficeListSerializer(office).data

            # Delete office
            OfficeService.delete(pk)

            # Log history
            # TODO: Get user_id from authentication
            user_id = request.query_params.get("user_id", 0)
            OfficeHistoryService.log(
                office_id=pk,
                user_id=int(user_id) if user_id else 0,
                triggered_action="deleteAction",
                old_data=json.dumps(old_data),
                new_data=None,
            )

            logger.info(f"Office #{pk} has been deleted")
            return Response(status=status.HTTP_204_NO_CONTENT)

        except OfficeServiceException as e:
            logger.error(f"Office service error: {e.message}")
            return Response(
                {"error": e.message, "code": e.code},
                status=(
                    status.HTTP_404_NOT_FOUND
                    if e.code == OfficeErrorCodes.ERROR_OFFICE_NOT_FOUND
                    else status.HTTP_400_BAD_REQUEST
                ),
            )
        except Exception as e:
            logger.error(f"Error deleting office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeCreateView(APIView):
    """
    API view for creating offices.

    Migrated from PHP: OfficeController::addAction()

    POST /offices/add/
    """

    def post(self, request):
        """
        Creates a new office.

        Request Body:
            {
                "addressid": 123,
                "name": "Office Name"
            }

        Response (matching PHP):
            {"id": 456}
        """
        try:
            logger.info(f"Creating new office with data: {request.data}")

            serializer = OfficeCreateSerializer(data=request.data)

            if serializer.is_valid():
                office = serializer.save()

                # Log history
                # TODO: Get user_id from authentication
                user_id = request.query_params.get("user_id", 0)
                new_data = OfficeListSerializer(office).data
                OfficeHistoryService.log(
                    office_id=office.id,
                    user_id=int(user_id) if user_id else 0,
                    triggered_action="addAction",
                    old_data=None,
                    new_data=json.dumps(new_data),
                )

                # Log activity
                logger.info(f"{office.name} (office) has been added")

                response_serializer = OfficeCreateResponseSerializer({"id": office.id})
                return Response(
                    response_serializer.data, status=status.HTTP_201_CREATED
                )

            logger.warning(f"Validation errors: {serializer.errors}")
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        except OfficeServiceException as e:
            logger.error(f"Office service error: {e.message}")
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating office: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeFastListView(APIView):
    """
    API view for fast office list (dropdowns).

    Migrated from PHP: OfficeController::fastListAction()

    GET /offices/fastlist/
    """

    def get(self, request):
        """
        Returns minimal office list for dropdowns.

        Response Format (matching PHP):
            {
                "results": [
                    {"id": 1, "name": "Office 1"},
                    {"id": 2, "name": "Office 2"},
                    ...
                ]
            }
        """
        try:
            logger.info("Fetching fast office list")
            results = OfficeService.get_fast_list()
            return Response({"results": results}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching fast office list: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeUsersView(APIView):
    """
    API view for office users.

    Migrated from PHP: OfficeController::getUsersAction()

    GET /offices/{id}/users/
    """

    def get(self, request, pk):
        """
        Returns list of users for an office.
        """
        try:
            logger.info(f"Fetching users for office {pk}")
            users = OfficeService.get_users(pk)
            return Response(users, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            logger.error(f"Office service error: {e.message}")
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching users for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSalesView(APIView):
    """
    API view for office sales users.

    Migrated from PHP: OfficeController::getSalesAction()

    GET /offices/{id}/sales/
    """

    def get(self, request, pk):
        """
        Returns list of sales users for an office.

        Response Format:
            {
                "assigned": [...],
                "available": [...]
            }
        """
        try:
            logger.info(f"Fetching sales for office {pk}")
            sales = OfficeService.get_sales(pk)
            return Response(sales, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            logger.error(f"Office service error: {e.message}")
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error fetching sales for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserOfficesView(APIView):
    """
    API view for user's offices.

    Migrated from PHP: OfficeController::getUserOfficesAction()

    GET /offices/user/
    """

    def get(self, request):
        """
        Returns list of offices for logged-in user.

        Response Format:
            [
                {"id": 1, "name": "Office 1"},
                {"id": 2, "name": "Office 2"},
                ...
            ]
        """
        try:
            # TODO: Get user_id from authentication
            user_id = request.query_params.get("user_id")
            if not user_id:
                return Response(
                    {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            user_id = int(user_id)
            logger.info(f"Fetching offices for user {user_id}")

            office_ids = OfficeService.get_all_by_user_id(user_id)

            result = []
            for oid in office_ids:
                try:
                    office = OfficeService.get_one(oid)
                    # Remove '(x)' from name (matching PHP)
                    name = office.name.replace(" (x)", "") if office.name else ""
                    result.append({"id": office.id, "name": name})
                except OfficeServiceException:
                    continue

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error fetching user offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSetUsersView(APIView):
    """
    API view to set office users.

    POST /offices/{id}/users/
    """

    def post(self, request, pk):
        """
        Set users for an office.

        Request Body:
            {"users": [1, 2, 3]}
        """
        try:
            user_ids = request.data.get("users", [])

            if not isinstance(user_ids, list):
                return Response(
                    {"error": "users must be a list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office = OfficeService.set_users(pk, user_ids)
            return Response({"success": True}, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error setting users for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSetSalesView(APIView):
    """
    API view to set office sales.

    POST /offices/{id}/sales/
    """

    def post(self, request, pk):
        """
        Set sales for an office.

        Request Body:
            {"sales": [1, 2, 3]}
        """
        try:
            sales_ids = request.data.get("sales", [])

            if not isinstance(sales_ids, list):
                return Response(
                    {"error": "sales must be a list"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office = OfficeService.set_sales(pk, sales_ids)
            return Response({"success": True}, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error setting sales for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeAddUserView(APIView):
    """
    API view to add new user to office.

    POST /offices/addUser/{id}/
    """

    def post(self, request, pk):
        """
        Add new user to office.

        Request Body:
            {
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "office"
            }
        """
        try:
            email = request.data.get("email")
            if not email:
                return Response(
                    {"error": "email is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            result = OfficeService.add_office_user(pk, request.data)
            return Response(result, status=status.HTTP_201_CREATED)

        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding user to office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeViewView(APIView):
    """
    API view for full office view with related records.

    GET /offices/view/{id}/
    """

    def get(self, request, pk):
        """
        Get full office view with all related data.
        """
        try:
            result = OfficeService.get_office_view(pk)
            return Response(result, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting office view {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePerformanceView(APIView):
    """
    API view for office performance metrics.

    GET /offices/performance/{id}/
    """

    def get(self, request, pk):
        """
        Get office performance stats.
        """
        try:
            result = OfficeService.get_performance(pk)
            return Response(result, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(e)
            return Response(
                {"error": str(e), "type": e.__class__.__name__},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeContactsView(APIView):
    """
    API view for office contacts.

    GET /offices/contacts/{id}/
    """

    def get(self, request, pk):
        try:
            contacts = OfficeService.get_contacts(pk)
            return Response(contacts, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting contacts for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeMedicationsView(APIView):
    """
    API view for office medications.

    GET /offices/medications/{id}/
    """

    def get(self, request, pk):
        try:
            start = request.query_params.get("start")
            end = request.query_params.get("end")

            start_dt = datetime.fromisoformat(start) if start else None
            end_dt = datetime.fromisoformat(end) if end else None

            medications = OfficeService.get_medications(pk, start_dt, end_dt)
            return Response(medications, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting medications for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePrescribersView(APIView):
    """
    API view for office prescribers.

    GET /offices/prescribers/{id}/
    """

    def get(self, request, pk):
        try:
            prescribers = OfficeService.get_prescribers(pk)
            return Response(prescribers, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting prescribers for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePatientsView(APIView):
    """
    API view for office patients.

    GET /offices/patients/{id}/
    """

    def get(self, request, pk):
        try:
            patients = OfficeService.get_patients(pk)
            return Response(patients, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting patients for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeRxView(APIView):
    """
    API view for office prescriptions.

    GET /offices/rx/{id}/
    """

    def get(self, request, pk):
        try:
            # 🔹 role (same as PHP $this->crypto->getUserRole())
            role = getattr(request.user, "role", None)
            print("Role is ", role)
            # 🔹 start / end (same as PHP request->get('start'), get('end'))
            start = request.query_params.get("start")
            end = request.query_params.get("end")

            data = OfficeService.get_rx_action(
                office_id=pk,
                role=role,
                start=start,
                end=end,
            )

            return Response(data, status=status.HTTP_200_OK)

        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code},
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
    API view for pending prescriptions.

    GET /offices/pendingrx/{id}/
    """

    def get(self, request, pk):
        try:
            pending = OfficeService.get_pending_rx(pk)
            return Response(pending, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting pending rx for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePendingPaymentsView(APIView):
    """
    API view for pending payments.

    GET /offices/pendingpayments/{id}/
    """

    def get(self, request, pk):
        try:
            pending = OfficeService.get_pending_payments(pk)
            return Response(pending, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting pending payments for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListPaginatedView(APIView):
    """
    API view for paginated office list.

    GET /offices/list-paginated/
    """

    def get(self, request):
        try:
            # ---- Query params ----
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 25))
            search = request.query_params.get("search")
            order_column = int(request.query_params.get("order", 0))
            order_dir = request.query_params.get("orderDir", "asc")

            # ---- User context (PHP crypto equivalent) ----
            user = request.user
            role = getattr(user, "role", None)
            user_id = user.id

            # ---- ROLE → OFFICE IDS (THIS IS YOUR CODE) ----
            office_ids = None

            if role == "sales":
                office_ids = OfficeService.get_office_ids_by_user(user_id)

                if not office_ids:
                    return Response(
                        {
                            "offices": [],
                            "firstPage": 1,
                            "currentPage": page,
                            "lastPage": 1,
                            "recordsFiltered": 0,
                            "nextPage": None,
                            "previousPage": None,
                            "recordsTotal": 0,
                            "limit": limit,
                        },
                        status=status.HTTP_200_OK,
                    )

            elif role == "sales-manager":
                office_ids = list(
                    set(
                        OfficeService.get_office_ids_by_manager(user_id)
                        + OfficeService.get_office_ids_by_user(user_id)
                    )
                )

                if not office_ids:
                    return Response(
                        {
                            "offices": [],
                            "firstPage": 1,
                            "currentPage": page,
                            "lastPage": 1,
                            "recordsFiltered": 0,
                            "nextPage": None,
                            "previousPage": None,
                            "recordsTotal": 0,
                            "limit": limit,
                        },
                        status=status.HTTP_200_OK,
                    )

            # ---- Call PHP-equivalent paginator ----
            data = OfficeService.get_paginated(
                page=page,
                limit=limit,
                search=search,
                order_column=order_column,
                order_dir=order_dir,
                office_ids=office_ids,
            )

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error fetching offices list")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeUpdateVendorIdView(APIView):
    """
    API view to update vendor ID.

    PUT /offices/update-vendor-id/{id}/
    """

    def put(self, request, pk):
        try:
            vendor_id = request.data.get("vendorid")
            if vendor_id is None:
                return Response(
                    {"error": "vendorid is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office = OfficeService.update_vendor_id(pk, int(vendor_id))
            return Response(
                {"success": True, "vendorid": office.vendorid},
                status=status.HTTP_200_OK,
            )
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating vendor ID for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeByNetsuiteIdView(APIView):
    """
    API view to get office by NetSuite ID.

    GET /offices/nsid/
    """

    def get(self, request):
        try:
            nsid = request.query_params.get("id")
            if not nsid:
                return Response(
                    {"error": "id (NetSuite ID) is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            office = OfficeService.get_by_netsuite_id(int(nsid))
            serializer = OfficeDetailSerializer(office)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting office by NetSuite ID: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListAltView(APIView):
    """
    API view for office list (alternate).

    GET /offices/list/
    """

    def get(self, request):
        try:
            include_inactive = (
                request.query_params.get("include_inactive", "false").lower() == "true"
            )
            offices = OfficeService.get_list(include_inactive)
            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting office list: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListNewView(APIView):
    """
    API view for new offices.

    GET /offices/list-new/
    """

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
            offices = OfficeService.get_new_offices(days)
            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting new offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListUpdatedView(APIView):
    """
    API view for updated offices.

    GET /offices/list-updated/
    """

    def get(self, request):
        try:
            days = int(request.query_params.get("days", 30))
            offices = OfficeService.get_updated_offices(days)
            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting updated offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeUnassignedPaginatedView(APIView):
    """
    API view for unassigned offices (paginated).

    GET /offices/unassigned-paginated/
    """

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 10))
            search = request.query_params.get("search", None)

            result = OfficeService.get_unassigned_paginated(page, limit, search)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting unassigned offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeListWithAddressView(APIView):
    """
    API view for office list with address.

    GET /offices/listWithAddress/
    """

    def get(self, request):
        try:
            offices = OfficeService.get_list_with_address()
            return Response(offices, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting office list with address: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficePaidRxsView(APIView):
    """
    API view for paid prescriptions.

    GET /offices/paid-rxs/{id}/
    """

    def get(self, request, pk):
        try:
            paid_rxs = OfficeService.get_paid_rxs(pk)
            return Response(paid_rxs, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting paid rxs for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeMovePaymentView(APIView):
    """
    API view to move payment between offices.

    POST /offices/movePayment/
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

            result = OfficeService.move_payment(
                int(payment_id), int(from_office_id), int(to_office_id)
            )
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error moving payment: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeCanPrescribeView(APIView):
    """
    API view to check if office can prescribe.

    GET /offices/canPrescribe/{id}/
    """

    def get(self, request, pk):
        try:
            result = OfficeService.can_prescribe(pk)
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error checking if office {pk} can prescribe: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeLeafletView(APIView):
    """
    API view for office leaflet.

    GET /offices/leaflet/{id}/
    """

    def get(self, request, pk):
        try:
            leaflet = OfficeService.get_leaflet(pk)
            return Response(leaflet, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting leaflet for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeQrView(APIView):
    """
    API view for office QR code.

    GET /offices/qr/{id}/
    """

    def get(self, request, pk):
        try:
            qr_data = OfficeService.get_qr_code(pk)
            return Response(qr_data, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting QR for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeReportsView(APIView):
    """
    API view for available reports.

    GET /offices/reports/
    """

    def get(self, request):
        try:
            reports = OfficeService.get_reports()
            return Response(reports, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting reports: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeMergeView(APIView):
    """
    API view to merge offices.

    POST /offices/merge/
    """

    def post(self, request):
        try:
            source_office_id = request.data.get("sourceOfficeId")
            target_office_id = request.data.get("targetOfficeId")

            if not all([source_office_id, target_office_id]):
                return Response(
                    {"error": "sourceOfficeId and targetOfficeId are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # TODO: Get user_id from authentication
            user_id = request.query_params.get("user_id", 0)

            result = OfficeService.merge_offices(
                int(source_office_id),
                int(target_office_id),
                int(user_id) if user_id else None,
            )
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error merging offices: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeLeafletSampleView(APIView):
    """
    API view for sample leaflet.

    GET /offices/leafletSample/
    """

    def get(self, request):
        try:
            sample = OfficeService.get_leaflet_sample()
            return Response(sample, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting leaflet sample: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSummaryReportView(APIView):
    """
    API view for summary report.

    POST /office/summaryreport/
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

            report = OfficeService.get_summary_report_data(
                office_id, start_date, end_date
            )
            return Response(report, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting summary report: {e}")
            return Response(
                {"error": True, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeInventoryReportView(APIView):
    """
    API view for inventory report.

    POST /office/inventoryreport/
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

            report = OfficeService.get_inventory_report_data(
                office_id, start_date, end_date
            )
            return Response(report, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting inventory report: {e}")
            return Response(
                {"error": True, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeEscrowReportView(APIView):
    """
    API view for escrow report.

    POST /office/escrowreport/
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

            report = OfficeService.get_escrow_report_data(
                office_id, start_date, end_date
            )
            return Response(report, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting escrow report: {e}")
            return Response(
                {"error": True, "message": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeSkincareParingsView(APIView):
    """
    API view for skincare pairings.

    GET /offices/skincare-pairings/{id}/
    """

    def get(self, request, pk):
        try:
            pairings = OfficeService.get_skincare_pairings(pk)
            return Response(pairings, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting skincare pairings for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class OfficeProviderSkincarePairingsView(APIView):
#     """
#     API view for provider skincare pairings.

#     GET /offices/provider-skincare-pairings/{id}/
#     """

#     def get(self, request, pk):
#         try:
#             pairings = OfficeService.get_provider_skincare_pairings(pk)
#             return Response(pairings, status=status.HTTP_200_OK)
#         except OfficeServiceException as e:
#             return Response(
#                 {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(
#                 f"Error getting provider skincare pairings for office {pk}: {e}"
#             )
#             return Response(
#                 {"error": "An unexpected error occurred"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )
class OfficeProviderSkincarePairingsView(APIView):
    """
    GET /offices/provider-skincare-pairings?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
    """

    def get(self, request):
        try:
            start_date = request.query_params.get("startDate")
            end_date = request.query_params.get("endDate")

            if not start_date or not end_date:
                return Response(
                    {"error": "startDate and endDate are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            pairings = OfficeService.get_provider_skincare_pairings(
                request.user, start_date, end_date
            )
            return Response({"pairings": pairings}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Provider skincare pairings error")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OfficeDioBySkuView(APIView):
    """
    API view for DIO by SKU.

    GET /offices/getdiobysku/{id}/
    """
    def get(self, request, pk):
        try:
            sku = request.query_params.get("sku")
            items = OfficeService.get_dio_by_sku(pk, sku)
            return Response(items, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("DIO by SKU error")
            return Response(
                {
                    "error": True,
                    "message": "Failed to generate inventory report.",
                    "debug": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class OfficeUpdateSkusView(APIView):
    """
    API view to update SKUs.

    PUT /offices/updateskus/{id}/
    """

    def put(self, request, pk):
        try:
            skus = request.data.get("skus", [])

            if not isinstance(skus, list):
                return Response(
                    {"error": "skus must be a list"}, status=status.HTTP_400_BAD_REQUEST
                )

            result = OfficeService.update_skus(pk, skus)
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating SKUs for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# class OfficeLoadDioView(APIView):
#     """
#     API view to load DIO configuration.

#     GET /offices/loadDIO/
#     """

#     def get(self, request):
#         try:
#             office_id = request.query_params.get("office_id")
#             if office_id:
#                 office_id = int(office_id)

#             result = OfficeService.load_dio(office_id)
#             return Response(result, status=status.HTTP_200_OK)
#         except OfficeServiceException as e:
#             return Response(
#                 {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
#             )
#         except Exception as e:
#             logger.error(f"Error loading DIO: {e}")
#             return Response(
#                 {"error": "An unexpected error occurred"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

class OfficeLoadDioView(APIView):
    """
    API view to load DIO configuration.
    GET  /offices/loadDIO/
    POST /offices/loadDIO/
    """

    def get(self, request):
        try:
            office_id = request.query_params.get("office_id")
            if office_id:
                office_id = int(office_id)

            result = OfficeService.load_dio(office_id)
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error loading DIO: {e}")
            return Response(
                {"error": True, "message": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ✅ PHP: loadDIOItemAction
    def post(self, request):
        try:
            office_id = request.data.get("officeid")
            netsuite_id = request.data.get("netsuiteid")
            sku = request.data.get("sku")

            result = OfficeService.load_dio_item(
                office_id=office_id,
                netsuiteid=netsuite_id,
                sku=sku,
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error loading DIO item: {e}")
            return Response(
                {"error": True, "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class OfficeSaveDioShipmentView(APIView):
    """
    API view to save DIO shipment.

    POST /offices/savedioshipment/
    """

    def post(self, request):
        try:
            office_id = request.data.get("officeId")

            if not office_id:
                return Response(
                    {"error": "officeId is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # TODO: Get user_id from authentication
            user_id = request.query_params.get("user_id", 0)

            result = OfficeService.save_dio_shipment(
                int(office_id), request.data, int(user_id) if user_id else None
            )
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error saving DIO shipment: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class SaveDioShipmentView(APIView):
    """
    POST /savedioshipment
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        shipments_saved = 0
        shipment_ids = []
        failed_shipments = []

        payload = request.data
        token = payload.get("token")

        # Token validation (same as PHP)
        if token != settings.NETSUITE_API_TOKEN:
            return Response(
                {
                    "shipmentsLoaded": 0,
                    "loadedShipmentIDs": [],
                    "failedShipments": [
                        {"reason": "Invalid NetSuite token"}
                    ],
                },
                status=status.HTTP_200_OK,
            )

        data = payload.get("data", [])

        with transaction.atomic(using="fred"):
            for shipment in data:
                try:
                    netsuiteid = shipment.get("netsuite ID")
                    sku = shipment.get("item")
                    officename = shipment.get("Name")
                    lotnumber = shipment.get("lot #")
                    qty = shipment.get("qty shipped")
                    sodate = shipment.get("SO Date")
                    sonumber = shipment.get("SO #")
                    ifdate = shipment.get("IF Date")
                    ifnumber = shipment.get("IF #")

                    if OfficeService.shipment_exists(
                        sonumber, ifnumber, sku, netsuiteid, lotnumber
                    ):
                        failed_shipments.append(
                            {
                                "shipmentDetails": shipment,
                                "reason": "DIO Shipment already exists",
                            }
                        )
                        continue

                    new_shipment = OfficeService.objects.using("fred").create(
                        netsuiteid=netsuiteid,
                        sku=sku,
                        officename=officename,
                        lotnumber=lotnumber,
                        qty=qty,
                        sodate=sodate,
                        sonumber=sonumber,
                        ifdate=ifdate,
                        ifnumber=ifnumber,
                    )

                    shipments_saved += 1
                    shipment_ids.append(new_shipment.id)

                except Exception as e:
                    failed_shipments.append(
                        {
                            "shipmentDetails": shipment,
                            "reason": str(e),
                        }
                    )

        return Response(
            {
                "shipmentsLoaded": shipments_saved,
                "loadedShipmentIDs": shipment_ids,
                "failedShipments": failed_shipments,
            },
            status=status.HTTP_200_OK,
        )


class OfficeDioOptoutView(APIView):
    """
    API view for DIO opt out management.

    GET    /offices/dio/optout/{id}/ - Get opt out status
    POST   /offices/dio/optout/{id}/ - Opt out
    DELETE /offices/dio/optout/{id}/ - Opt back in
    """

    def get(self, request, pk):
        """Get DIO opt out status."""
        try:
            result = OfficeService.get_dio_opt_out_status(pk)
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting DIO opt out status for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, pk):
        """Opt out of DIO replenishment."""
        try:
            # TODO: Get user_id from authentication
            user_id = request.query_params.get("user_id", 0)

            result = OfficeService.dio_opt_out(pk, int(user_id) if user_id else None)
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error opting out of DIO for office {pk}: {e}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        """Opt back in to DIO replenishment."""
        try:
            # TODO: Get user_id from authentication
            user_id = request.query_params.get("user_id", 0)

            result = OfficeService.dio_opt_in(pk, int(user_id) if user_id else None)
            return Response(result, status=status.HTTP_200_OK)
        except OfficeServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_400_BAD_REQUEST
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
    "SaveDioShipmentView",
]
