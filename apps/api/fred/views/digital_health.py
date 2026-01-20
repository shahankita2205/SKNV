"""
Digital Health Views Module

Contains views/viewsets related to digital health features.

Legacy Controller Mapping: DigitalHealthController
"""
from venv import logger
from fred.models.digital_health import DHSettings
from fred.serializers.digital_health import DigitalHealthService
from rest_framework import viewsets
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions import HasRole

class DHSettingsView(APIView):
     
     def get(self, request):
        try:
            queryset = DHSettings.objects.all().order_by("id")
            return Response(list(queryset.values()), status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Error fetching DH settings")
            return Response(
                {
                    "success": False,
                    "message": f"Error fetching settings: {str(exc)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   

class UpdateDHSettingsView(APIView):

    def post(self, request):
        try:
            payload = request.data

            if not isinstance(payload, list):
                return Response(
                    {
                        "success": False,
                        "message": "Invalid request. Expected an array of settings."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            for setting in payload:
                if "key" not in setting or "enabled" not in setting:
                    return Response(
                        {
                            "success": False,
                            "message": 'Each setting must have "key" and "enabled" fields.'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            DigitalHealthService.update_dh_settings(payload, request.user)

            return Response(
                {
                    "success": True,
                    "message": "All settings updated successfully"
                },
                status=status.HTTP_200_OK
            )

        except Exception as exc:
            logger.exception("Error updating DH settings")
            return Response(
                {
                    "success": False,
                    "message": f"Error updating settings: {str(exc)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DHCouponsView(APIView):
    """
    GET /digitalhealth/coupons
    Roles allowed: admin, manager
    """

    def get(self, request):
        try:
            coupons = DigitalHealthService.get_dh_coupons()
            return Response(
                {
                    "success": True,
                    "data": coupons
                },
                status=status.HTTP_200_OK
            )
        except Exception as exc:
            logger.exception("Error fetching DH coupons")
            return Response(
                {
                    "success": False,
                    "message": f"Error fetching coupons: {str(exc)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateDHCouponView(APIView):

    def post(self, request):
        try:
            payload = request.data

            if not isinstance(payload, dict):
                return Response(
                    {"success": False, "message": "Invalid request payload"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = DigitalHealthService.create_dh_coupon(payload)

            return Response(
                {"success": True, "data": result},
                status=status.HTTP_201_CREATED,
            )

        except IntegrityError as e:
            error_str = str(e)
            if "coupons_code_key" in error_str or "duplicate" in error_str.lower():
                # Extract code from payload if available
                code = request.data.get("code", "this code")
                return Response(
                    {
                        "success": False,
                        "message": f"A coupon with code '{code}' already exists",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "success": False,
                    "message": f"Database constraint violation: {str(e)}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error creating coupon: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UpdateDHCouponView(APIView):

    def put(self, request, id):
        try:
            payload = request.data

            if not isinstance(payload, dict):
                return Response(
                    {"success": False, "message": "Invalid request payload"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            result = DigitalHealthService.update_dh_coupon(id, payload)

            return Response(
                {"success": True, "data": result},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error updating coupon: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteDHCouponView(APIView):

    def delete(self, request, id):
        try:
            DigitalHealthService.delete_dh_coupon(id)

            return Response(
                {
                    "success": True,
                    "message": "Coupon deleted successfully",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"Error deleting coupon: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )      


class FeedbacksView(APIView):

    def get(self, request):
        service = DigitalHealthService()
        result = service.get_feedbacks()

        if result is False:
            return Response(
                {"success": False, "message": "Failed to fetch feedbacks"},
                status=500,
            )

        return Response(result, status=200)
 
        
__all__ = [
    "DHSettingsView",
    "UpdateDHSettingsView",
    "DHCouponsView",
    "CreateDHCouponView",
    "UpdateDHCouponView",
    "DeleteDHCouponView",
    "FeedbacksView",
]
