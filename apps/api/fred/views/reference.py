"""
Reference Views Module

Contains views/viewsets related to lookup/reference data.

Legacy Controller Mapping: StateController, AddressController, FaqController
"""
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.views import APIView
from fred.models import Faq
from fred.serializers import FredFaqSerializer
import json
import logging
from django.utils import timezone

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
        return getattr(self.request.user, 'role', None)

    def get(self, request):
        """Get all FAQs - equivalent to getAction/listAction"""
        try:
            faqs = Faq.objects.all()
            serializer = FredFaqSerializer(faqs, many=True)
            return JsonResponse(serializer.data, safe=False)
        except Exception as e:
            logger.error(f"Error retrieving FAQs: {str(e)}")
            return JsonResponse(
                {"error": "Internal Server Error"}, 
                status=500
            )

    def post(self, request):
        """Add FAQ - equivalent to addAction"""
        try:
            data = request.data if hasattr(request, 'data') else json.loads(request.body)
            
            # Build FAQ data matching your model fields
            faq_data = {}
            
            if 'category' in data:
                faq_data['category'] = data.get('category', '').lower()
            if 'question' in data:
                faq_data['question'] = data.get('question')
            if 'answer' in data:
                faq_data['answer'] = data.get('answer')
            
            # Set created timestamp
            faq_data['created'] = timezone.now()
            
            serializer = FredFaqSerializer(data=faq_data)
            
            if serializer.is_valid():
                faq = serializer.save()
                
                # Log the creation
                logger.info(
                    f"User {request.user.id} created FAQ #{faq.id}"
                )
                
                return JsonResponse({"id": faq.id}, status=201)
            else:
                return JsonResponse(
                    {"error": serializer.errors}, 
                    status=422
                )
                
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"}, 
                status=400
            )
        except Exception as e:
            logger.error(f"Error creating FAQ: {str(e)}")
            return JsonResponse(
                {"error": "Unable to create FAQ"}, 
                status=422
            )


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
        return getattr(self.request.user, 'role', None)

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
                return JsonResponse(
                    {"error": "FAQ not found"}, 
                    status=404
                )
            
            serializer = FredFaqSerializer(faq)
            return JsonResponse(serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving FAQ {pk}: {str(e)}")
            return JsonResponse(
                {"error": "Internal Server Error"}, 
                status=500
            )

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
                return JsonResponse(
                    {"error": "FAQ not found"}, 
                    status=404
                )
            
            data = request.data if hasattr(request, 'data') else json.loads(request.body)
            role = self.get_user_role()
            
            # Role-based permissions
            allowed_roles = ['faq', 'office', 'sales', 'sales-manager', 'manager', 'admin']
            
            if role not in allowed_roles:
                return JsonResponse(
                    {"error": "Insufficient permissions"}, 
                    status=403
                )
            
            # Only update fields that are provided
            if 'category' in data:
                faq.category = data['category']
            if 'question' in data:
                faq.question = data['question']
            if 'answer' in data:
                faq.answer = data['answer']
            
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
                return JsonResponse(
                    {"error": "FAQ not found"}, 
                    status=404
                )
            
            faq_id = faq.id
            faq.delete()
            
            # Log the deletion
            logger.info(
                f"User {request.user.id} deleted FAQ #{faq_id}"
            )
            
            return JsonResponse({"success": True}, status=204)
            
        except Exception as e:
            logger.error(f"Error deleting FAQ {pk}: {str(e)}")
            return JsonResponse(
                {"error": "Unable to delete FAQ"}, 
                status=422
            )


__all__ = [
    'FredFaqView',
    'FredFaqDetailView',
]
