"""
Reference Views Module

Contains views/viewsets related to lookup/reference data.

Legacy Controller Mapping: StateController, AddressController, FaqController
"""

from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from fred.models import Faq
from fred.models import reference as reference_model
from fred.serializers import FredFaqSerializer
from fred.serializers import reference
from core.permissions.legacy import legacy_roles
import json
import logging
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import transaction


# TODO: Migrate reference-related views from views.py
logger = logging.getLogger(__name__)


class FredFaqView(APIView):
    """
    Handles list and create operations for FAQs
    GET /faqs/ - List all FAQs
    POST /faqs/ - Create new FAQ
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_role(self):
        """Get user role from request"""
        return getattr(self.request.user, "role", None)

    def get(self, request):
        """Get all FAQs - equivalent to getAction/listAction"""
        try:
            faqs = Faq.objects.all()
            serializer = FredFaqSerializer(faqs, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            logger.error(f"Error retrieving FAQs: {str(e)}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)

    def post(self, request):
        """Add FAQ - equivalent to addAction"""
        try:
            data = (
                request.data if hasattr(request, "data") else json.loads(request.body)
            )

            # Build FAQ data matching your model fields
            faq_data = {}

            if "category" in data:
                faq_data["category"] = data.get("category", "").lower()
            if "question" in data:
                faq_data["question"] = data.get("question")
            if "answer" in data:
                faq_data["answer"] = data.get("answer")

            # Set created timestamp
            faq_data["created"] = timezone.now()

            serializer = FredFaqSerializer(data=faq_data)

            if serializer.is_valid():
                faq = serializer.save()

                # Log the creation
                logger.info(f"User {request.user.id} created FAQ #{faq.id}")

                return JsonResponse({"id": faq.id}, status=201)
            else:
                return JsonResponse({"error": serializer.errors}, status=422)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error creating FAQ: {str(e)}")
            return JsonResponse({"error": "Unable to create FAQ"}, status=422)


class FredFaqDetailView(APIView):
    """
    Handles individual FAQ operations
    GET /faqs/<id>/ - Get one FAQ
    PUT/PATCH /faqs/<id>/ - Update FAQ
    DELETE /faqs/<id>/ - Delete FAQ
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_user_role(self):
        """Get user role from request"""
        return getattr(self.request.user, "role", None)

    def get_object(self, pk):
        """Helper to get FAQ object"""
        try:
            return Faq.objects.get(pk=pk)
        except Faq.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get one FAQ - equivalent to getOneAction"""
        try:
            faq = self.get_object(pk)
            if faq is None:
                return JsonResponse({"error": "FAQ not found"}, status=404)

            serializer = FredFaqSerializer(faq)
            return JsonResponse(serializer.data)

        except Exception as e:
            logger.error(f"Error retrieving FAQ {pk}: {str(e)}")
            return JsonResponse({"error": "Internal Server Error"}, status=500)

    def put(self, request, pk):
        """Update FAQ - equivalent to updateAction"""
        return self._update(request, pk)

    def patch(self, request, pk):
        """Partial update FAQ - equivalent to updateAction"""
        return self._update(request, pk)

    def _update(self, request, pk):
        """Shared update logic"""
        try:
            faq = self.get_object(pk)
            if faq is None:
                return JsonResponse({"error": "FAQ not found"}, status=404)

            data = (
                request.data if hasattr(request, "data") else json.loads(request.body)
            )
            role = self.get_user_role()

            # Role-based permissions
            allowed_roles = [
                "faq",
                "office",
                "sales",
                "sales-manager",
                "manager",
                "admin",
            ]

            if role not in allowed_roles:
                return JsonResponse({"error": "Insufficient permissions"}, status=403)

            # Only update fields that are provided
            if "category" in data:
                faq.category = data["category"]
            if "question" in data:
                faq.question = data["question"]
            if "answer" in data:
                faq.answer = data["answer"]

            faq.save()

            logger.info(f"User {request.user.id} updated FAQ #{pk}")

            return JsonResponse({"error": False})

        except json.JSONDecodeError:
            return JsonResponse({"error": True}, status=400)
        except Exception as e:
            logger.error(f"Error updating FAQ {pk}: {str(e)}")
            return JsonResponse({"error": True}, status=400)

    def delete(self, request, pk):
        """Delete FAQ - equivalent to deleteAction"""
        try:
            faq = self.get_object(pk)
            if faq is None:
                return JsonResponse({"error": "FAQ not found"}, status=404)

            faq_id = faq.id
            faq.delete()

            # Log the deletion
            logger.info(f"User {request.user.id} deleted FAQ #{faq_id}")

            return JsonResponse({"success": True}, status=204)

        except Exception as e:
            logger.error(f"Error deleting FAQ {pk}: {str(e)}")
            return JsonResponse({"error": "Unable to delete FAQ"}, status=422)


__all__ = [
    "FredFaqView",
    "FredFaqDetailView",
]


class AddressCreateView(APIView):
    def get_permissions(self):
        method_perms = {
            "POST": [legacy_roles("admin", "pharmacist", "doctor", "office")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]

    """
    Create Address record -
    POST /address/create/

    Expected payload:
    {
        "address1":
        "address2":
        "city":
        "state":
        "zip":
        "created":
        "type":
        "zip4":
        "latlong":
    }
    """

    def post(self, request):
        try:
            # Serialize and validate the input data
            serializer = reference.AddressModelSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic(using="fred"):
                address = serializer.save()

                # Log successful creation
                logger.info(f"Address created successfully: ID {address.id}")

                return Response(
                    {
                        "message": "Address created successfully",
                        "id": address.id,  # Return ID like the original function
                    },
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            logger.error(f"Unexpected error creating address: {e}")
            return Response(
                {"error": "An error occurred while creating the address"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddressGetAllView(APIView):
    def get_permissions(self):
        method_perms = {
            "GET": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]

    """
    Get all address records -
    GET /address/
    """

    def get(self, request):
        try:
            with transaction.atomic(using="fred"):
                addresses = reference_model.Address.objects.all().order_by("id")
                return Response(
                    {
                        "message": "Address created successfully",
                        "values": list(
                            addresses.values()
                        ),  # Return ID like the original function
                    },
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.error(f"Unexpected error creating address: {e}")
            return Response(
                {"error": "An error occurred while getting the address"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddressOneView(APIView):
    def get_permissions(self):
        method_perms = {
            "GET": [legacy_roles("admin")],
            "PUT": [legacy_roles("admin")],
            "DELETE": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]

    """
    Get one address record by id -
    GET /address/{address_id}
    """

    def get(self, request, address_id):
        if not address_id or not address_id.strip():
            return Response(
                {"error": "Expected 'address_id' integer in request url"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            address_data = reference.AddressModelSerializer.get_address_by_id(
                address_id.strip()
            )
            if address_data:
                return Response(
                    {
                        "message": "Successfully retreived address",
                        "value": address_data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": f"Address with id {address_id} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logger.error(f"Unexpected error getting address: {e}")
            return Response(
                {"error": "An error occurred while getting the address"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    """
    Update Address Record
    PUT /address/{address_id}

    Expected payload (all optional):
    {
        "address1":
        "address2":
        "city":
        "state":
        "zip":
        "created":
        "type":
        "zip4":
        "latlong":
    }
    """

    def put(self, request, address_id):
        try:
            # Serialize and validate the input data
            serializer = reference.AddressModelSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not address_id or not address_id.strip():
                return Response(
                    {"error": "Expected 'address_id' integer in request url"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update address record within a transaction
            with transaction.atomic(using="fred"):
                address = reference_model.Address.objects.get(id=address_id.strip())
                for attribute, value in request.data.items():
                    setattr(address, attribute, value)

                address.full_clean()
                address.save()

                # Log successful creation
                logger.info(f"Address updated successfully: ID {address.id}")

                return Response(
                    {
                        "message": "Address updated successfully",
                        "id": address.id,  # Return ID like the original function
                    },
                    status=status.HTTP_200_OK,
                )
        except reference_model.Address.DoesNotExist:
            return Response(
                {"error": f"Address with id {address_id} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating address: {e}")
            return Response(
                {"error": "An error occurred while updating the address"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, address_id):
        try:
            if not address_id or not address_id.strip():
                return Response(
                    {"error": "Expected 'address_id' integer in request url"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic(using="fred"):
                address = reference_model.Address.objects.get(id=address_id.strip())

                address.delete()

                # Log successful creation
                logger.info(f"Address deleted successfully: ID {address.id}")

                return Response(
                    {
                        "message": "Address deleted successfully",
                        "id": address.id,  # Return ID like the original function
                    },
                    status=status.HTTP_200_OK,
                )
        except reference_model.Address.DoesNotExist:
            return Response(
                {"error": f"Address with id {address_id} not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating address: {e}")
            return Response(
                {"error": "An error occurred while updating the address"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddressMatchView(APIView):
    """
    Match a record to a given payload
    POST /address/match
    """

    def get(self, request):
        try:
            # Serialize and validate the input data
            serializer = reference.AddressModelSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            logger.error(request.data["address1"])
            logger.error(request.data["address2"])
            logger.error(request.data["zip"])
            logger.error(request.data["type"])
            address_id = serializer.address_match(
                request.data["address1"],
                request.data["address2"],
                request.data["zip"],
                request.data["type"],
            )
            return Response(
                {"address_id": address_id},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Unexpected error updating address: {e}")
            return Response(
                {"error": "An error occurred while updating the address"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AddressMatchAllView(APIView):
    """
    Match a record to a given payload
    POST /address/match-all
    """

    def get(self, request):
        try:
            return_dict = {}
            # Serialize and validate the input data
            serializer = reference.AddressModelSerializer()
            all_addresses = (
                reference_model.Address.objects.filter(id__gt=200000)
                .order_by("id")[:200]
                .values()
            )
            for address in all_addresses:
                logger.error(address["id"])
                matched_id = serializer.address_match(
                    address["address1"].upper(),
                    address["address2"],
                    address["zip"],
                    address["type"],
                )
                return_dict[address["id"]] = matched_id

            return Response(
                {"result": return_dict},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Unexpected error matching all address: {e}")
            return Response(
                {"error": "An error occurred while updating the address"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
