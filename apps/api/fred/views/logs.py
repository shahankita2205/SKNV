"""
Logs Views Module

Contains views/viewsets related to audit and logging.

Legacy Controller Mapping: LogsController, FailedfulfilllogController
"""
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q, OuterRef, Exists
from django.db.models.functions import Cast
from django.db.models.fields import CharField
import logging

from fred.models import Failedfulfilllog, Rxfill
from fred.serializers import FredFailedfulfillogSerializer
from fred.views import StandardResultsSetPagination

logger = logging.getLogger(__name__)


class FredFailedfulfillogView(generics.ListCreateAPIView):
    """
    List and Create view for Failed Fulfillment Logs
    
    Migrated from: FailedfulfilllogController
    """
    queryset = Failedfulfilllog.objects.all().using("fred")
    serializer_class = FredFailedfulfillogSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        ffp = self.request.query_params.get('ffp')
        active_param = self.request.query_params.get('active')
        
        if ffp is None and active_param is None:
            return Failedfulfilllog.objects.using("fred")
        
        try:
            queryset = Failedfulfilllog.objects.using("fred")
            
            if ffp:
                queryset = queryset.filter(fulfillmentpartner__icontains=ffp)
            
            if active_param:
                active = active_param.lower() in ['true', '1', 'yes']
                
                if active:
                    matching_rxfills = Rxfill.objects.using("fred").annotate(
                        id_as_string=Cast('id', output_field=CharField())
                    ).filter(
                        id_as_string=OuterRef('rxfillid'),
                        status='other'
                    )
                else:
                    matching_rxfills = Rxfill.objects.using("fred").annotate(
                        id_as_string=Cast('id', output_field=CharField())
                    ).filter(
                        id_as_string=OuterRef('rxfillid')
                    ).exclude(status='other')
                
                queryset = queryset.annotate(
                    has_matching_rxfill=Exists(matching_rxfills)
                ).filter(has_matching_rxfill=True)
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error fetching filtered failed fulfillment logs: {str(e)}", exc_info=True)
            return Failedfulfilllog.objects.none()


class FredFailedfulfillogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update, and Delete view for Failed Fulfillment Logs
    """
    queryset = Failedfulfilllog.objects.all().using("fred")
    serializer_class = FredFailedfulfillogSerializer


__all__ = [
    'FredFailedfulfillogView',
    'FredFailedfulfillogDetailView',
]