"""
TextSent Views Module

Contains views related to text message management.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse

from fred.serializers.text import TextSentModelSerializer, TextPaginationQuerySerializer
from core.permissions.legacy import legacy_roles

import logging

logger = logging.getLogger(__name__)


class TextSentViewSet(viewsets.ViewSet):

    def get_permissions(self):
        method_perms = {
            "textsent_failed_pc_delivers - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "textsent_failed_no_patient - GET": [
                legacy_roles(
                    "admin",
                    "customer-service",
                    "customer-service-manager",
                    "pharmacist",
                    "manager",
                )
            ],
            "text_incoming - POST": [AllowAny],
            "text_update - POST": [AllowAny],
        }
        perms = method_perms.get(
            f"{self.request.resolver_match.view_name} - {self.request.method}", []
        )
        return [perm() for perm in perms]

    """
    GET /texts/failed-pc-delivers/
    Get paginated undelivered texts for PC delivers offices
    """

    def get_failed_pc_delivers(self, request):
        try:
            input_serializer = TextPaginationQuerySerializer(data=request.GET)
            input_serializer.is_valid(raise_exception=True)
            params = input_serializer.validated_data

            text_serializer = TextSentModelSerializer()
            results = text_serializer.list_paginated_failed_pc_delivers(
                page=params["page"],
                limit=params["limit"],
                search=params.get("search"),
                order=params.get("order", 0),
                orderDir=params.get("orderDir", "asc"),
            )

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error retrieving failed PC delivers texts: {e}")
            return Response(
                {"error": "An error occurred while retrieving failed texts"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    GET /texts/failed-no-patient/
    Get paginated undelivered texts with no associated patient
    """

    def get_failed_no_patient(self, request):
        try:
            input_serializer = TextPaginationQuerySerializer(data=request.GET)
            input_serializer.is_valid(raise_exception=True)
            params = input_serializer.validated_data

            text_serializer = TextSentModelSerializer()
            results = text_serializer.list_paginated_failed_no_patient(
                page=params["page"],
                limit=params["limit"],
                search=params.get("search"),
                order=params.get("order", 0),
                orderDir=params.get("orderDir", "asc"),
            )

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error retrieving failed no-patient texts: {e}")
            return Response(
                {"error": "An error occurred while retrieving failed texts"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    POST /text/incoming
    Handle incoming text messages (Twilio webhook)
    
    Legacy Controller Mapping: TextController::incomingAction
    """
    
    def incoming_action(self, request):
        try:
            twilio_signature = request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
            
            if twilio_signature:
                response = MessagingResponse()
                response.message(
                    "We don't monitor this number. Questions? Please call (800) 646-5040 option 1"
                )
                return HttpResponse(str(response), content_type='text/xml', status=status.HTTP_200_OK)
            else:
                return HttpResponse(status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error processing incoming text: {e}")
            return HttpResponse(status=status.HTTP_200_OK)

    """
    POST /text/update/{token}
    Update text status by token (Twilio status callback)
    
    Legacy Controller Mapping: TextController::updateTextStatusAction
    """
    
    def update_text_status_action(self, request, token):
        try:
            return HttpResponse("OK", status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error updating text status: {e}")
            return HttpResponse("OK", status=status.HTTP_200_OK)
