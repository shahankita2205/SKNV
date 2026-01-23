"""
TextSent Views Module

Contains views related to text message management.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response

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
