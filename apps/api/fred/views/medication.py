# fred/views/medication.py
import csv
import io
from datetime import date
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.db.models import OuterRef, Subquery, Max, Q
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions.legacy import legacy_roles
import json
import logging

logger = logging.getLogger(__name__)

from fred.models import (
    Medication,
    Ingredient,
    Othermedication,
    Outofstockmedication,
    Fee,
)

from fred.serializers import (
    FredMedicationSerializer,
    FredMedicationWithFeeSerializer,
    FredIngredientSerializer,
    FredOthermedicationSerializer,
    FredOutofstockmedicationSerializer,
    NDCResolver,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


# ============================================================================
# ViewSets (Handle all CRUD in one class)
# ============================================================================


class MedicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Medication model - handles all CRUD operations
    Automatically resolves old SKUs to current SKUs using Updatedskus table
    """
    queryset = Medication.objects.all().using("fred")
    serializer_class = FredMedicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "dh_enabled", "ndc", "formulacode"]
    
    def get_permissions(self):
        """
        Map HTTP methods to legacy roles based on old API permissions
        """
        method_perms = {
            "GET": [legacy_roles("admin", "manager", "sales", "sales-manager", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist", "office", "doctor")],
            "POST": [legacy_roles("admin")],
            "PUT": [legacy_roles("admin")],
            "PATCH": [legacy_roles("admin")],
            "DELETE": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]
    
    def get_queryset(self):
        """Override to always use fred database"""
        return Medication.objects.using("fred").all()
    
    def perform_create(self, serializer):
        """Override to save to fred database"""
        serializer.save()
    
    def perform_update(self, serializer):
        """Override to save to fred database"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Override to delete from fred database"""
        instance.delete(using='fred')
    
    @action(detail=False, methods=['post'], permission_classes=[legacy_roles("admin")])
    def load_csv(self, request):
        """
        Bulk load medications from CSV
        POST /medications/load_csv/
        """
        try:
            csv_content = request.data.get('csv', '')
            csv_file = io.StringIO(csv_content)
            csv_reader = csv.reader(csv_file)
            
            created_count = 0
            errors = []
            
            with transaction.atomic(using='fred'):
                for i, row in enumerate(csv_reader):
                    if i == 0:  # Skip header
                        continue
                    
                    if len(row) < 9:
                        errors.append(f"Row {i}: Insufficient columns")
                        continue
                    
                    medication_data = {
                        'formula': row[0],
                        'formulacode': row[1],
                        'ndc': row[2],
                        'size': row[3],
                        'dosage': row[4],
                        'mpn': row[5],
                        'formulashort': row[6],
                        'hwhid': row[7],
                        'nsid': row[8],
                        'status': 'active'
                    }
                    
                    serializer = self.get_serializer(data=medication_data)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                            created_count += 1
                        except IntegrityError:
                            errors.append(f"Row {i}: Already exists")
                    else:
                        errors.append(f"Row {i}: {serializer.errors}")
            
            return Response({
                'success': True,
                'created': created_count,
                'errors': errors
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active medications (dh_enabled=True)
        GET /medications/active/
        """
        medications = self.get_queryset().filter(status='active', dh_enabled=True)
        serializer = self.get_serializer(medications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by_ndc/(?P<ndc>[^/.]+)')
    def by_ndc(self, request, ndc=None):
        """Get medication by NDC (handles dashes and SKU updates)"""
        try:
            current_ndc = NDCResolver.get_current_ndc(ndc)
            
            if current_ndc != ndc:
                logger.info(f"NDC {ndc} resolved to current NDC: {current_ndc}")
            
            medication = NDCResolver.get_medication_by_ndc(ndc)
            
            if medication:
                serializer = self.get_serializer(medication)
                response_data = serializer.data
                
                if current_ndc != ndc:
                    response_data['_ndc_info'] = {
                        'requested_ndc': ndc,
                        'current_ndc': current_ndc,
                        'was_updated': True
                    }
                
                return Response(response_data)
            
            return Response({
                'error': 'Medication not found',
                'requested_ndc': ndc,
                'resolved_ndc': current_ndc
            }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(f"Error retrieving medication by NDC: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='resolve_ndc/(?P<ndc>[^/.]+)')
    def resolve_ndc(self, request, ndc=None):
        """Resolve an NDC to its most current version"""
        try:
            current_ndc = NDCResolver.get_current_ndc(ndc)
            was_updated = current_ndc != ndc
            medication = NDCResolver.get_medication_by_ndc(ndc)
            
            return Response({
                'original_ndc': ndc,
                'current_ndc': current_ndc,
                'was_updated': was_updated,
                'has_medication': medication is not None
            })
            
        except Exception as e:
            logger.error(f"Error resolving NDC: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], permission_classes=[legacy_roles("admin")])
    def toggle_status(self, request, pk=None):
        """Toggle medication status between active/inactive"""
        medication = self.get_object()
        medication.status = 'inactive' if medication.status == 'active' else 'active'
        medication.save(using='fred')
        return Response({'ok': True, 'status': medication.status})
    
    @action(detail=False, methods=['get'], url_path='blacklist_check/(?P<ndc>[^/.]+)/(?P<state>[^/.]+)')
    def blacklist_check(self, request, ndc=None, state=None):
        """Check if medication is blacklisted for a state"""
        try:
            current_ndc = NDCResolver.get_current_ndc(ndc)
            medication = NDCResolver.get_medication_by_ndc(ndc)
            
            if not medication:
                return Response({
                    'error': 'Medication not found',
                    'requested_ndc': ndc,
                    'resolved_ndc': current_ndc
                }, status=status.HTTP_404_NOT_FOUND)
            
            is_blacklisted = medication.is_blacklisted_for_state(state)
            
            return Response({
                'blacklisted': is_blacklisted,
                'state': state,
                'ndc': medication.ndc,
                'requested_ndc': ndc if ndc != medication.ndc else None
            })
            
        except Exception as e:
            logger.error(f"Error checking blacklist: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='dio_blacklist_check/(?P<ndc>[^/.]+)')
    def dio_blacklist_check(self, request, ndc=None):
        """Check if medication is blacklisted for DIO"""
        try:
            current_ndc = NDCResolver.get_current_ndc(ndc)
            medication = NDCResolver.get_medication_by_ndc(ndc)
            
            if not medication:
                return Response({
                    'error': 'Medication not found',
                    'requested_ndc': ndc,
                    'resolved_ndc': current_ndc
                }, status=status.HTTP_404_NOT_FOUND)
            
            is_blacklisted = medication.is_blacklisted_for_dio()
            
            return Response({
                'blacklisted': is_blacklisted,
                'ndc': medication.ndc,
                'requested_ndc': ndc if ndc != medication.ndc else None
            })
            
        except Exception as e:
            logger.error(f"Error checking DIO blacklist: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def with_fees(self, request):
        """Get all medications with fees and ingredients"""
        try:
            latest_med_subquery = Medication.objects.using('fred').filter(
                formulacode=OuterRef('formulacode'),
                dh_enabled=True
            ).values('formulacode').annotate(
                max_id=Max('id')
            ).values('max_id')
            
            medications = self.get_queryset().filter(
                dh_enabled=True,
                id__in=Subquery(latest_med_subquery)
            ).order_by('ndc')
            
            serializer = FredMedicationWithFeeSerializer(medications, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting medications with fees: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IngredientViewSet(viewsets.ModelViewSet):
    """ViewSet for Ingredient model"""
    queryset = Ingredient.objects.all().using("fred")
    serializer_class = FredIngredientSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """Admin only for ingredients"""
        method_perms = {
            "GET": [legacy_roles("admin")],
            "POST": [legacy_roles("admin")],
            "PUT": [legacy_roles("admin")],
            "PATCH": [legacy_roles("admin")],
            "DELETE": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]
    
    def get_queryset(self):
        return Ingredient.objects.using("fred").all()
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete(using='fred')
    
    @action(detail=False, methods=['post'])
    def load_csv(self, request):
        """Bulk load ingredients from CSV"""
        try:
            csv_content = request.data.get('csv', '')
            csv_file = io.StringIO(csv_content)
            csv_reader = csv.reader(csv_file)
            
            created_count = 0
            errors = []
            
            with transaction.atomic(using='fred'):
                for i, row in enumerate(csv_reader):
                    if i == 0:  # Skip header
                        continue
                    
                    if len(row) < 2:
                        errors.append(f"Row {i}: Insufficient columns")
                        continue
                    
                    try:
                        ingredient, created = Ingredient.objects.using('fred').get_or_create(
                            ingredient=row[0],
                            defaults={'description': row[1]}
                        )
                        if created:
                            created_count += 1
                    except IntegrityError:
                        errors.append(f"Row {i}: Already exists")
            
            return Response({
                'success': True,
                'created': created_count,
                'errors': errors
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OtherMedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Other Medication model"""
    queryset = Othermedication.objects.all().using("fred")
    serializer_class = FredOthermedicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["brand_ndc", "branded_name"]  # Fixed field names
    
    def get_permissions(self):
        """All authenticated users can read, admin only for write"""
        method_perms = {
            "GET": [legacy_roles("admin", "manager", "sales", "sales-manager", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist", "office", "doctor")],
            "POST": [legacy_roles("admin")],
            "PUT": [legacy_roles("admin")],
            "PATCH": [legacy_roles("admin")],
            "DELETE": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]
    
    def get_queryset(self):
        return Othermedication.objects.using("fred").all()
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete(using='fred')


class OutOfStockMedicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Out of Stock Medications"""
    queryset = Outofstockmedication.objects.all().using("fred")
    serializer_class = FredOutofstockmedicationSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        """
        Based on old API:
        - getAllOutOfStockMedAction: all roles can view
        - addOutOfStockMedAction: admin only
        - deleteOutofStockMedAction: admin only
        """
        method_perms = {
            "GET": [legacy_roles("admin", "manager", "sales", "sales-manager", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist", "office", "doctor")],
            "POST": [legacy_roles("admin")],
            "PUT": [legacy_roles("admin")],
            "PATCH": [legacy_roles("admin")],
            "DELETE": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]
    
    def get_queryset(self):
        """Only return non-deleted records"""
        return Outofstockmedication.objects.using("fred").filter(isdeleted=False)
    
    def perform_create(self, serializer):
        """Check for duplicates before creating"""
        medication_id = self.request.data.get('medicationid')
        
        existing = Outofstockmedication.objects.using('fred').filter(
            medicationid=medication_id,
            isdeleted=False
        ).first()
        
        if existing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Medication already in out of stock list')
        
        if 'dateadded' not in self.request.data:
            serializer.save(dateadded=date.today())
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.isdeleted = True
        instance.save(using='fred')


# ============================================================================
# Backwards compatibility views
# ============================================================================

class FredMedicationView(generics.ListCreateAPIView):
    queryset = Medication.objects.all().using("fred")
    serializer_class = FredMedicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "dh_enabled", "ndc", "formulacode"]
    
    def get_permissions(self):
        method_perms = {
            "GET": [legacy_roles("admin", "manager", "sales", "sales-manager", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist", "office", "doctor")],
            "POST": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]


class FredMedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medication.objects.all().using("fred")
    serializer_class = FredMedicationSerializer
    
    def get_permissions(self):
        method_perms = {
            "GET": [legacy_roles("admin", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist")],
            "PUT": [legacy_roles("admin")],
            "PATCH": [legacy_roles("admin")],
            "DELETE": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]


class FredIngredientView(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all().using("fred")
    serializer_class = FredIngredientSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_permissions(self):
        return [legacy_roles("admin")()]


class FredIngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredient.objects.all().using("fred")
    serializer_class = FredIngredientSerializer
    
    def get_permissions(self):
        return [legacy_roles("admin")()]


class FredOthermedicationView(generics.ListCreateAPIView):
    queryset = Othermedication.objects.all().using("fred")
    serializer_class = FredOthermedicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["brand_ndc", "branded_name"]  # Fixed field names
    
    def get_permissions(self):
        method_perms = {
            "GET": [legacy_roles("admin", "manager", "sales", "sales-manager", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist", "office", "doctor")],
            "POST": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]


class FredOthermedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Othermedication.objects.all().using("fred")
    serializer_class = FredOthermedicationSerializer
    
    def get_permissions(self):
        method_perms = {
            "GET": [legacy_roles("admin", "manager", "sales", "sales-manager", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist", "office", "doctor")],
            "PUT": [legacy_roles("admin")],
            "PATCH": [legacy_roles("admin")],
            "DELETE": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]


class FredOutofstockmedicationView(generics.ListCreateAPIView):
    queryset = Outofstockmedication.objects.all().using("fred")
    serializer_class = FredOutofstockmedicationSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Outofstockmedication.objects.using("fred").filter(isdeleted=False)
    
    def get_permissions(self):
        method_perms = {
            "GET": [legacy_roles("admin", "manager", "sales", "sales-manager", "tech-support", "planner", "customer-service", "customer-service-manager", "pharmacist", "office", "doctor")],
            "POST": [legacy_roles("admin")],
        }
        perms = method_perms.get(self.request.method, [])
        return [perm() for perm in perms]


class FredOutofstockmedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Outofstockmedication.objects.all().using("fred")
    serializer_class = FredOutofstockmedicationSerializer
    
    def get_queryset(self):
        return Outofstockmedication.objects.using("fred").filter(isdeleted=False)
    
    def get_permissions(self):
        return [legacy_roles("admin")()]


# Export all views
__all__ = [
    'MedicationViewSet',
    'IngredientViewSet',
    'OtherMedicationViewSet',
    'OutOfStockMedicationViewSet',
    'FredMedicationView',
    'FredMedicationDetailView',
    'FredIngredientView',
    'FredIngredientDetailView',
    'FredOthermedicationView',
    'FredOthermedicationDetailView',
    'FredOutofstockmedicationView',
    'FredOutofstockmedicationDetailView',
]