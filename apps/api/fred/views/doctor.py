"""
Doctor Views

Contains all API views for Doctor endpoints.
Fully migrated from PHP DoctorController.

Views:
    - DoctorListView: GET /doctors/
    - DoctorDetailView: GET /doctors/{id}/
    - DoctorCreateView: POST /doctors/add/
    - DoctorUpdateView: PUT /doctors/{id}/update/
    - DoctorDeleteView: DELETE /doctors/{id}/delete/
    - DoctorFastListView: GET /doctors/fastlist/
    - DoctorListAllView: GET /doctors/list/
    - DoctorNPIsView: GET /doctors/npis/
    - DoctorListPaginatedView: GET /doctors/list-paginated/
"""

import logging

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from fred.models import Doctor
from fred.serializers.doctor import (
    # Read serializers
    DoctorSerializer,
    DoctorListSerializer,
    DoctorFastListSerializer,
    DoctorNPISerializer,
    DoctorWithDetailsSerializer,
    DoctorPaginatedResponseSerializer,
    DoctorFastListResponseSerializer,
    # Write serializers
    DoctorCreateSerializer,
    DoctorUpdateSerializer,
    # Response serializers
    DoctorCreateResponseSerializer,
    DoctorUpdateResponseSerializer,
    # Service and exceptions
    DoctorService,
    DoctorServiceException,
    DoctorErrorCodes,
)

logger = logging.getLogger(__name__)


# =============================================================================
# PAGINATION
# =============================================================================


class DoctorPagination(PageNumberPagination):
    """Pagination for doctor list endpoints"""

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


# =============================================================================
# GENERIC VIEWS (Simple CRUD)
# =============================================================================


class DoctorListView(generics.ListAPIView):
    """
    GET /doctors/

    List all doctors with pagination.

    PHP Equivalent: DoctorController::getAction()
    """

    queryset = Doctor.objects.all().using("fred").order_by("id")
    serializer_class = DoctorListSerializer
    pagination_class = DoctorPagination


class DoctorDetailView(generics.RetrieveAPIView):
    """
    GET /doctors/{id}/

    Get a single doctor by ID.

    PHP Equivalent: DoctorController::getOneAction()
    """

    queryset = Doctor.objects.all().using("fred")
    serializer_class = DoctorSerializer


# =============================================================================
# CUSTOM API VIEWS
# =============================================================================


class DoctorCreateView(APIView):
    """
    POST /doctors/add/

    Create a new doctor.

    PHP Equivalent: DoctorController::addAction()

    Request Body:
        {
            "name": "Dr. John Smith",
            "npi": "1234567890",
            "phone": "555-0123",
            "email": "john@example.com"
        }

    Response:
        201: {"id": 123}
        400: {"error": "Invalid data", "details": {...}}
        422: {"error": "...", "code": 17001}
    """

    def post(self, request):
        serializer = DoctorCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            doctor = serializer.save()
            response_serializer = DoctorCreateResponseSerializer({"id": doctor.id})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except DoctorServiceException as e:
            return Response(
                {"error": e.message, "code": e.code},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            logger.error(f"Unexpected error creating doctor: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DoctorUpdateView(APIView):
    """
    PUT /doctors/{id}/update/

    Update a doctor with role-based field access.

    PHP Equivalent: DoctorController::updateAction()

    Role-based access:
        - admin: Can update name, email, phone, dea, npi, spi, pin
        - others: Can only update pin

    Request Body:
        {
            "name": "Dr. John Smith Updated",
            "pin": "1234"
        }

    Response:
        200: {"error": false}
        400: {"error": "Invalid data", "details": {...}}
        404: {"error": "Doctor not found"}
        422: {"error": "...", "code": 17004}
    """

    def put(self, request, pk):
        # Get doctor
        try:
            doctor = DoctorService.get_one(pk)
        except DoctorServiceException as e:
            return Response(
                {"error": e.message, "code": e.code}, status=status.HTTP_404_NOT_FOUND
            )

        # Get user role from request
        # TODO: Replace with actual auth system role retrieval
        role = getattr(request.user, "role", None)
        if not role:
            role = request.data.get("_role", "admin")  # Fallback for testing

        # Validate and update
        serializer = DoctorUpdateSerializer(
            instance=doctor, data=request.data, partial=True, context={"role": role}
        )

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer.save()
            response_serializer = DoctorUpdateResponseSerializer({"error": False})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except DoctorServiceException as e:
            return Response(
                {"error": e.message, "code": e.code},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating doctor #{pk}: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DoctorDeleteView(APIView):
    """
    DELETE /doctors/{id}/delete/

    Delete a doctor.

    PHP Equivalent: DoctorController::deleteAction()

    Response:
        204: No content
        404: {"error": "Doctor not found"}
        422: {"error": "...", "code": 17005}
    """

    def delete(self, request, pk):
        try:
            DoctorService.delete(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DoctorServiceException as e:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if e.code == DoctorErrorCodes.ERROR_DOCTOR_NOT_FOUND
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            return Response({"error": e.message, "code": e.code}, status=status_code)
        except Exception as e:
            logger.error(f"Unexpected error deleting doctor #{pk}: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DoctorFastListView(APIView):
    """
    GET /doctors/fastlist/

    Get minimal doctor list for dropdowns.
    Returns only id and name fields.

    PHP Equivalent: DoctorController::fastListAction()

    Response:
        200: {"results": [{"id": 1, "name": "Dr. Smith"}, ...]}
    """

    def get(self, request):
        doctors = DoctorService.get_fast_list()
        # Serialize each doctor item
        items_serializer = DoctorFastListSerializer(doctors, many=True)
        # Wrap in response format
        response_serializer = DoctorFastListResponseSerializer(
            {"results": items_serializer.data}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class DoctorListAllView(APIView):
    """
    GET /doctors/list/

    Get all doctors with prescription stats and associated offices.

    PHP Equivalent: DoctorController::listAction()

    Response:
        200: [
            {
                "profile": {...},
                "rxs": {"total": 10, "this_month": 2},
                "offices": [1, 2, 3]
            },
            ...
        ]
    """

    def get(self, request):
        doctors = DoctorService.get_list_with_details()
        serializer = DoctorWithDetailsSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorNPIsView(APIView):
    """
    GET /doctors/npis/

    Get all doctors with valid 10-digit NPIs.

    PHP Equivalent: DoctorController::getAllNPIsAction()

    Response:
        200: [{"id": 1, "name": "Dr. Smith", "npi": "1234567890", "spi": "..."}, ...]
    """

    def get(self, request):
        npis = DoctorService.get_all_npis()
        serializer = DoctorNPISerializer(npis, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorListPaginatedView(APIView):
    """
    GET /doctors/list-paginated/

    Get paginated doctor list for DataTables.

    PHP Equivalent: DoctorController::listPaginatedAction()

    Query Parameters:
        - start: Offset (converted to page number)
        - length: Page size (default: 10)
        - search[value]: Search term
        - order[0][column]: Column index (0=id, 1=name)
        - order[0][dir]: Sort direction (asc/desc)

    Response:
        200: {
            "doctors": [...],
            "firstPage": 1,
            "currentPage": 1,
            "lastPage": 10,
            "recordsFiltered": 100,
            "nextPage": 2,
            "previousPage": null,
            "recordsTotal": 100,
            "limit": 10
        }
    """

    def get(self, request):
        # Parse DataTables parameters
        start = int(request.query_params.get("start", 0))
        length = int(request.query_params.get("length", 10))
        search = request.query_params.get("search[value]", "")
        order_column = int(request.query_params.get("order[0][column]", 0))
        order_dir = request.query_params.get("order[0][dir]", "asc")

        # Convert start/length to page number
        page = (start // length) + 1 if length > 0 else 1

        # Get paginated data
        result = DoctorService.get_paginated(
            page=page,
            limit=length,
            search=search if search else None,
            order_column=order_column,
            order_dir=order_dir,
        )

        serializer = DoctorPaginatedResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
