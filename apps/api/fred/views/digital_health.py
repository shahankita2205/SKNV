"""
Digital Health Views Module

Contains views related to digital health features.

Legacy Controller Mapping: DigitalHealthController

Views:
    - DHSettingsView: GET /digital-health/settings/
    - UpdateDHSettingsView: POST /digital-health/settings/update/
    - DHCouponsView: GET /digital-health/coupons/
    - CreateDHCouponView: POST /digital-health/coupons/create/
    - UpdateDHCouponView: PUT /digital-health/coupons/<pk>/
    - DeleteDHCouponView: DELETE /digital-health/coupons/<pk>/delete/
    - FeedbacksView: GET /feedbacks/
"""

import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from fred.models.digital_health import DHSettings, DHCoupons
from fred.serializers.digital_health import (
    DHSettingsListSerializer,
    DHSettingsUpdateItemSerializer,
    DHCouponListSerializer,
    DHCouponCreateSerializer,
    DHCouponUpdateSerializer,
    DHCouponCreateResponseSerializer,
    DHCouponUpdateResponseSerializer,
    DHCouponDeleteResponseSerializer,
    DigitalHealthService,
    DigitalHealthServiceException,
    DigitalHealthErrorCodes,
)

logger = logging.getLogger(__name__)


# =============================================================================
# DH SETTINGS VIEWS
# =============================================================================


class DHSettingsView(APIView):
    """
    GET /digital-health/settings/

    List all digital health settings.

    Response:
        200: List of settings
        500: {"error": "Internal server error"}
    """

    def get(self, request):
        try:
            queryset = DHSettings.objects.all().order_by("id")
            serializer = DHSettingsListSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as exc:
            logger.exception("Error fetching DH settings")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateDHSettingsView(APIView):
    """
    POST /digital-health/settings/update/

    Update multiple digital health settings.

    Request Body:
        [
            {"key": 1, "enabled": true, "description": "..."},
            {"key": 2, "enabled": false, "description": "..."}
        ]

    Response:
        200: {"success": true, "message": "All settings updated successfully"}
        400: {"error": "Invalid data", "details": {...}}
        404: {"error": "...", "code": 18006}
        500: {"error": "Internal server error"}
    """

    def post(self, request):
        serializer = DHSettingsUpdateItemSerializer(data=request.data, many=True)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            DigitalHealthService.update_dh_settings(serializer.validated_data, request.user)

            return Response(
                {"success": True, "message": "All settings updated successfully"},
                status=status.HTTP_200_OK,
            )
        except DigitalHealthServiceException as e:
            return Response(
                {"error": e.message, "code": e.code},
                status=status.HTTP_404_NOT_FOUND
                if e.code == DigitalHealthErrorCodes.ERROR_SETTING_NOT_FOUND
                else status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as exc:
            logger.exception("Error updating DH settings")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# DH COUPONS VIEWS
# =============================================================================


class DHCouponsView(APIView):
    """
    GET /digital-health/coupons/

    List all digital health coupons (excluding trashed).

    Response:
        200: {"success": true, "data": [...]}
        500: {"error": "Internal server error"}
    """

    def get(self, request):
        try:
            coupons = DigitalHealthService.get_dh_coupons()
            serializer = DHCouponListSerializer(coupons, many=True)
            return Response(
                {"success": True, "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            logger.exception("Error fetching DH coupons")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateDHCouponView(APIView):
    """
    POST /digital-health/coupons/create/

    Create a new digital health coupon.

    Request Body:
        {
            "code": "SUMMER20",
            "discount_type": "percent",
            "amount": 20,
            "status": "active",
            ...
        }

    Response:
        201: {"success": true, "data": {"coupon_id": 1, "code": "...", "message": "..."}}
        400: {"error": "Invalid data", "details": {...}}
        422: {"error": "...", "code": 18002}
        500: {"error": "Internal server error"}
    """

    def post(self, request):
        serializer = DHCouponCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": "Invalid data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            coupon = serializer.save()
            response_serializer = DHCouponCreateResponseSerializer({
                "coupon_id": coupon.coupon_id,
                "code": coupon.code,
                "message": "Coupon created successfully",
            })
            return Response(
                {"success": True, "data": response_serializer.data},
                status=status.HTTP_201_CREATED,
            )
        except DigitalHealthServiceException as e:
            return Response(
                {"error": e.message, "code": e.code},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            logger.exception("Error creating DH coupon")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateDHCouponView(APIView):
    """
    PUT /digital-health/coupons/<pk>/

    Update an existing digital health coupon.

    Response:
        200: {"success": true, "data": {"coupon_id": 1, "message": "..."}}
        400: {"error": "Invalid data", "details": {...}}
        404: {"error": "Coupon not found"}
        422: {"error": "...", "code": 18004}
        500: {"error": "Internal server error"}
    """

    def put(self, request, pk):
        try:
            coupon = DHCoupons.objects.filter(coupon_id=pk).first()
            if not coupon:
                return Response(
                    {"error": "Coupon not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = DHCouponUpdateSerializer(
                instance=coupon, data=request.data, partial=True, context={"coupon_id": pk}
            )

            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                updated_coupon = serializer.save()
                response_serializer = DHCouponUpdateResponseSerializer({
                    "coupon_id": updated_coupon.coupon_id,
                    "message": "Coupon updated successfully",
                })
                return Response(
                    {"success": True, "data": response_serializer.data},
                    status=status.HTTP_200_OK,
                )
            except DigitalHealthServiceException as e:
                return Response(
                    {"error": e.message, "code": e.code},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
        except Exception as e:
            logger.exception(f"Error updating DH coupon #{pk}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteDHCouponView(APIView):
    """
    DELETE /digital-health/coupons/<pk>/delete/

    Soft delete a coupon (moves to trash).

    Response:
        200: {"success": true, "message": "Coupon deleted successfully"}
        404: {"error": "Coupon not found", "code": 18001}
        422: {"error": "...", "code": 18005}
        500: {"error": "Internal server error"}
    """

    def delete(self, request, pk):
        try:
            result = DigitalHealthService.delete_dh_coupon(pk)
            response_serializer = DHCouponDeleteResponseSerializer(result)
            return Response(
                {"success": True, "message": response_serializer.data["message"]},
                status=status.HTTP_200_OK,
            )
        except DigitalHealthServiceException as e:
            status_code = (
                status.HTTP_404_NOT_FOUND
                if e.code == DigitalHealthErrorCodes.ERROR_COUPON_NOT_FOUND
                else status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            return Response({"error": e.message, "code": e.code}, status=status_code)
        except Exception as e:
            logger.exception(f"Error deleting DH coupon #{pk}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# =============================================================================
# FEEDBACKS VIEW
# =============================================================================


class FeedbacksView(APIView):
    """
    GET /feedbacks/

    Fetch feedbacks from external digital health API.

    Response:
        200: Feedbacks data from external API
        500: {"error": "Failed to fetch feedbacks"}
    """

    def get(self, request):
        service = DigitalHealthService()
        result = service.get_feedbacks()

        if result is False:
            return Response(
                {"error": "Failed to fetch feedbacks"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(result, status=status.HTTP_200_OK)


__all__ = [
    "DHSettingsView",
    "UpdateDHSettingsView",
    "DHCouponsView",
    "CreateDHCouponView",
    "UpdateDHCouponView",
    "DeleteDHCouponView",
    "FeedbacksView",
]
