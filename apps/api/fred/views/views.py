from django.conf import settings
from rest_framework import generics, viewsets, status
from django.db import connections, IntegrityError, transaction
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from twilio.rest import Client
from datetime import datetime, timedelta
from twilio.base.exceptions import TwilioRestException
import math
import logging
import re
import secrets

logger = logging.getLogger(__name__)

from fred.models import (
    Address,
    Allergens,
    AuditTable,
    Automatedtasks,
    Deletedoffice,
    Device,
    DioItems,
    Dispenselogs,
    Doctor,
    Featureflag,
    Fee,
    Fulfillmentpartners,
    Ihflogs,
    Ingredient,
    Inhouseeligibility,
    Inventory,
    Logs,
    Logspatient,
    Logsrx,
    Lots,
    Medalignments,
    Medication,
    Medleaflet,
    Office,
    Officeagreementtype,
    Officehistory,
    Officeinfo,
    Officetype,
    Othermedication,
    Outofstockmedication,
    Patient,
    Patientlogs,
    Patientmeta,
    Payment,
    Paymentsnotapproved,
    PcdAgreement,
    PcdFormularyAgreement,
    PcdInboundNdc,
    PcdNormalizedDrugGroup,
    Prepaid,
    Rx,
    Rxfill,
    Rxprint,
    Rxraw,
    Shipment,
    Skincarepairings,
    State,
    Substatus,
    Task,
    Textsent,
    Token,
    Updatedskus,
    Users,
    Userstate,
)

from fred.serializers import (
    DioItemsSkuSerializer,
    FredAddressSerializer,
    FredAllergensSerializer,
    FredAuditTableSerializer,
    FredAutomatedtasksSerializer,
    FredDeletedofficeSerializer,
    FredDeviceSerializer,
    FredDioItemsSerializer,
    FredDispenselogsSerializer,
    FredFeatureflagSerializer,
    FredFeeSerializer,
    FredFulfillmentpartnersSerializer,
    FredIhflogsSerializer,
    FredIngredientSerializer,
    FredInhouseeligibilitySerializer,
    FredInventorySerializer,
    FredLogspatientSerializer,
    FredLogsrxSerializer,
    FredLogsSerializer,
    FredLotsSerializer,
    FredMedalignmentsSerializer,
    FredMedicationSerializer,
    FredMedleafletSerializer,
    FredOfficeSerializer,
    FredOfficeagreementtypeSerializer,
    FredOfficehistorySerializer,
    FredOfficeinfoSerializer,
    FredOfficetypeSerializer,
    FredOthermedicationSerializer,
    FredOutofstockmedicationSerializer,
    FredPatientlogsSerializer,
    FredPatientmetaSerializer,
    FredPatientSerializer,
    FredPaymentSerializer,
    FredPaymentsnotapprovedSerializer,
    FredPcdAgreementSerializer,
    FredPcdFormularyAgreementSerializer,
    FredPcdInboundNdcSerializer,
    FredPcdNormalizedDrugGroupSerializer,
    FredPrepaidSerializer,
    FredRxfillSerializer,
    FredRxprintSerializer,
    FredRxrawSerializer,
    FredRxSerializer,
    FredShipmentSerializer,
    FredSkincarepairingsSerializer,
    FredStateSerializer,
    FredSubstatusSerializer,
    FredTaskSerializer,
    FredTextsentSerializer,
    FredTokenSerializer,
    FredUpdatedskusSerializer,
    FredUsersSerializer,
    FredUserstateSerializer,
    PaymentCreateSerializer,
    PaymentMatchSerializer,
    PaymentResponseSerializer,
    PaymentTransactionSerializer,
    RefillsNoPaymentQuerySerializer,
    RefillsNoPaymentSerializer,
    NewRxNoPaymentQuerySerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000


class FredAddressView(generics.ListCreateAPIView):
    queryset = Address.objects.all().using("fred")
    serializer_class = FredAddressSerializer
    pagination_class = StandardResultsSetPagination


class FredAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all().using("fred")
    serializer_class = FredAddressSerializer


class FredAllergensView(generics.ListCreateAPIView):
    queryset = Allergens.objects.all().using("fred")
    serializer_class = FredAllergensSerializer
    pagination_class = StandardResultsSetPagination


class FredAllergensDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Allergens.objects.all().using("fred")
    serializer_class = FredAllergensSerializer


class FredAuditTableView(generics.ListCreateAPIView):
    queryset = AuditTable.objects.all().using("fred")
    serializer_class = FredAuditTableSerializer
    pagination_class = StandardResultsSetPagination


class FredAuditTableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AuditTable.objects.all().using("fred")
    serializer_class = FredAuditTableSerializer


class FredAutomatedtasksView(generics.ListCreateAPIView):
    queryset = Automatedtasks.objects.all().using("fred")
    serializer_class = FredAutomatedtasksSerializer
    pagination_class = StandardResultsSetPagination


class FredAutomatedtasksDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Automatedtasks.objects.all().using("fred")
    serializer_class = FredAutomatedtasksSerializer


class FredDeletedofficeView(generics.ListCreateAPIView):
    queryset = Deletedoffice.objects.all().using("fred")
    serializer_class = FredDeletedofficeSerializer
    pagination_class = StandardResultsSetPagination


class FredDeletedofficeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deletedoffice.objects.all().using("fred")
    serializer_class = FredDeletedofficeSerializer


class FredDeviceView(generics.ListCreateAPIView):
    queryset = Device.objects.all().using("fred")
    serializer_class = FredDeviceSerializer
    pagination_class = StandardResultsSetPagination


class FredDeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all().using("fred")
    serializer_class = FredDeviceSerializer


class FredDispenselogsView(generics.ListCreateAPIView):
    queryset = Dispenselogs.objects.all().using("fred")
    serializer_class = FredDispenselogsSerializer
    pagination_class = StandardResultsSetPagination


class FredDispenselogsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dispenselogs.objects.all().using("fred")
    serializer_class = FredDispenselogsSerializer


class FredFeatureflagView(generics.ListCreateAPIView):
    queryset = Featureflag.objects.all().using("fred")
    serializer_class = FredFeatureflagSerializer
    pagination_class = StandardResultsSetPagination


class FredFeatureflagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Featureflag.objects.all().using("fred")
    serializer_class = FredFeatureflagSerializer


class FredFeeView(generics.ListCreateAPIView):
    queryset = Fee.objects.all().using("fred")
    serializer_class = FredFeeSerializer
    pagination_class = StandardResultsSetPagination


class FredFeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fee.objects.all().using("fred")
    serializer_class = FredFeeSerializer


class FredFulfillmentpartnersView(generics.ListCreateAPIView):
    queryset = Fulfillmentpartners.objects.all().using("fred")
    serializer_class = FredFulfillmentpartnersSerializer
    pagination_class = StandardResultsSetPagination


class FredFulfillmentpartnersDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fulfillmentpartners.objects.all().using("fred")
    serializer_class = FredFulfillmentpartnersSerializer


class FredIhflogsView(generics.ListCreateAPIView):
    queryset = Ihflogs.objects.all().using("fred")
    serializer_class = FredIhflogsSerializer
    pagination_class = StandardResultsSetPagination


class FredIhflogsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ihflogs.objects.all().using("fred")
    serializer_class = FredIhflogsSerializer


class FredIngredientView(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all().using("fred")
    serializer_class = FredIngredientSerializer
    pagination_class = StandardResultsSetPagination


class FredIngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredient.objects.all().using("fred")
    serializer_class = FredIngredientSerializer


class FredInhouseeligibilityView(generics.ListCreateAPIView):
    queryset = Inhouseeligibility.objects.all().using("fred")
    serializer_class = FredInhouseeligibilitySerializer
    pagination_class = StandardResultsSetPagination


class FredInhouseeligibilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inhouseeligibility.objects.all().using("fred")
    serializer_class = FredInhouseeligibilitySerializer


class FredInventoryView(generics.ListCreateAPIView):
    queryset = Inventory.objects.all().using("fred")
    serializer_class = FredInventorySerializer
    pagination_class = StandardResultsSetPagination


class FredInventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.all().using("fred")
    serializer_class = FredInventorySerializer


class FredLogsView(generics.ListCreateAPIView):
    queryset = Logs.objects.all().using("fred")
    serializer_class = FredLogsSerializer
    pagination_class = StandardResultsSetPagination


class FredLogsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Logs.objects.all().using("fred")
    serializer_class = FredLogsSerializer


class FredLogspatientView(generics.ListCreateAPIView):
    queryset = Logspatient.objects.all().using("fred")
    serializer_class = FredLogspatientSerializer
    pagination_class = StandardResultsSetPagination


class FredLogspatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Logspatient.objects.all().using("fred")
    serializer_class = FredLogspatientSerializer


class FredLogsrxView(generics.ListCreateAPIView):
    queryset = Logsrx.objects.all().using("fred")
    serializer_class = FredLogsrxSerializer
    pagination_class = StandardResultsSetPagination


class FredLogsrxDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Logsrx.objects.all().using("fred")
    serializer_class = FredLogsrxSerializer


class FredLotsView(generics.ListCreateAPIView):
    queryset = Lots.objects.all().using("fred")
    serializer_class = FredLotsSerializer
    pagination_class = StandardResultsSetPagination


class FredLotsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lots.objects.all().using("fred")
    serializer_class = FredLotsSerializer


class FredMedalignmentsView(generics.ListCreateAPIView):
    queryset = Medalignments.objects.all().using("fred")
    serializer_class = FredMedalignmentsSerializer
    pagination_class = StandardResultsSetPagination


class FredMedalignmentsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medalignments.objects.all().using("fred")
    serializer_class = FredMedalignmentsSerializer


class FredMedicationView(generics.ListCreateAPIView):
    queryset = Medication.objects.all().using("fred")
    serializer_class = FredMedicationSerializer
    pagination_class = StandardResultsSetPagination


class FredMedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medication.objects.all().using("fred")
    serializer_class = FredMedicationSerializer


class FredMedleafletView(generics.ListCreateAPIView):
    queryset = Medleaflet.objects.all().using("fred")
    serializer_class = FredMedleafletSerializer
    pagination_class = StandardResultsSetPagination


class FredMedleafletDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medleaflet.objects.all().using("fred")
    serializer_class = FredMedleafletSerializer


class FredOfficeView(generics.ListCreateAPIView):
    queryset = Office.objects.all().using("fred")
    serializer_class = FredOfficeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["netsuiteid", "name", "dhenabled"]


class FredOfficeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Office.objects.all().using("fred")
    serializer_class = FredOfficeSerializer


class FredOfficeagreementtypeView(generics.ListCreateAPIView):
    queryset = Officeagreementtype.objects.all().using("fred")
    serializer_class = FredOfficeagreementtypeSerializer
    pagination_class = StandardResultsSetPagination


class FredOfficeagreementtypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officeagreementtype.objects.all().using("fred")
    serializer_class = FredOfficeagreementtypeSerializer


class FredOfficehistoryView(generics.ListCreateAPIView):
    queryset = Officehistory.objects.all().using("fred")
    serializer_class = FredOfficehistorySerializer
    pagination_class = StandardResultsSetPagination


class FredOfficehistoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officehistory.objects.all().using("fred")
    serializer_class = FredOfficehistorySerializer


class FredOfficeinfoView(generics.ListCreateAPIView):
    queryset = Officeinfo.objects.all().using("fred")
    serializer_class = FredOfficeinfoSerializer
    pagination_class = StandardResultsSetPagination


class FredOfficeinfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officeinfo.objects.all().using("fred")
    serializer_class = FredOfficeinfoSerializer


class FredOfficetypeView(generics.ListCreateAPIView):
    queryset = Officetype.objects.all().using("fred")
    serializer_class = FredOfficetypeSerializer
    pagination_class = StandardResultsSetPagination


class FredOfficetypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officetype.objects.all().using("fred")
    serializer_class = FredOfficetypeSerializer


class FredOthermedicationView(generics.ListCreateAPIView):
    queryset = Othermedication.objects.all().using("fred")
    serializer_class = FredOthermedicationSerializer
    pagination_class = StandardResultsSetPagination


class FredOthermedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Othermedication.objects.all().using("fred")
    serializer_class = FredOthermedicationSerializer


class FredOutofstockmedicationView(generics.ListCreateAPIView):
    queryset = Outofstockmedication.objects.all().using("fred")
    serializer_class = FredOutofstockmedicationSerializer
    pagination_class = StandardResultsSetPagination


class FredOutofstockmedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Outofstockmedication.objects.all().using("fred")
    serializer_class = FredOutofstockmedicationSerializer


class FredPatientView(generics.ListCreateAPIView):
    queryset = Patient.objects.all().using("fred")
    serializer_class = FredPatientSerializer
    pagination_class = StandardResultsSetPagination


class FredPatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all().using("fred")
    serializer_class = FredPatientSerializer


class FredPatientlogsView(generics.ListCreateAPIView):
    queryset = Patientlogs.objects.all().using("fred")
    serializer_class = FredPatientlogsSerializer
    pagination_class = StandardResultsSetPagination


class FredPatientlogsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patientlogs.objects.all().using("fred")
    serializer_class = FredPatientlogsSerializer


class FredPatientmetaView(generics.ListCreateAPIView):
    queryset = Patientmeta.objects.all().using("fred")
    serializer_class = FredPatientmetaSerializer
    pagination_class = StandardResultsSetPagination


class FredPatientmetaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patientmeta.objects.all().using("fred")
    serializer_class = FredPatientmetaSerializer


class FredPaymentView(generics.ListCreateAPIView):
    queryset = Payment.objects.all().using("fred")
    serializer_class = FredPaymentSerializer
    pagination_class = StandardResultsSetPagination


class FredPaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all().using("fred")
    serializer_class = FredPaymentSerializer


class FredPaymentsnotapprovedView(generics.ListCreateAPIView):
    queryset = Paymentsnotapproved.objects.all().using("fred")
    serializer_class = FredPaymentsnotapprovedSerializer
    pagination_class = StandardResultsSetPagination


class FredPaymentsnotapprovedDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Paymentsnotapproved.objects.all().using("fred")
    serializer_class = FredPaymentsnotapprovedSerializer


class FredPcdAgreementView(generics.ListCreateAPIView):
    queryset = PcdAgreement.objects.all().using("fred")
    serializer_class = FredPcdAgreementSerializer
    pagination_class = StandardResultsSetPagination


class FredPcdAgreementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PcdAgreement.objects.all().using("fred")
    serializer_class = FredPcdAgreementSerializer


class FredPcdFormularyAgreementView(generics.ListCreateAPIView):
    queryset = PcdFormularyAgreement.objects.all().using("fred")
    serializer_class = FredPcdFormularyAgreementSerializer
    pagination_class = StandardResultsSetPagination


class FredPcdFormularyAgreementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PcdFormularyAgreement.objects.all().using("fred")
    serializer_class = FredPcdFormularyAgreementSerializer


class FredPcdInboundNdcView(generics.ListCreateAPIView):
    queryset = PcdInboundNdc.objects.all().using("fred")
    serializer_class = FredPcdInboundNdcSerializer
    pagination_class = StandardResultsSetPagination


class FredPcdInboundNdcDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PcdInboundNdc.objects.all().using("fred")
    serializer_class = FredPcdInboundNdcSerializer


class FredPcdNormalizedDrugGroupView(generics.ListCreateAPIView):
    queryset = PcdNormalizedDrugGroup.objects.all().using("fred")
    serializer_class = FredPcdNormalizedDrugGroupSerializer
    pagination_class = StandardResultsSetPagination


class FredPcdNormalizedDrugGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PcdNormalizedDrugGroup.objects.all().using("fred")
    serializer_class = FredPcdNormalizedDrugGroupSerializer


class FredPrepaidView(generics.ListCreateAPIView):
    queryset = Prepaid.objects.all().using("fred")
    serializer_class = FredPrepaidSerializer
    pagination_class = StandardResultsSetPagination


class FredPrepaidDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prepaid.objects.all().using("fred")
    serializer_class = FredPrepaidSerializer


class FredRxView(generics.ListCreateAPIView):
    queryset = Rx.objects.all().using("fred")
    serializer_class = FredRxSerializer
    pagination_class = StandardResultsSetPagination


class FredRxDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rx.objects.all().using("fred")
    serializer_class = FredRxSerializer


class FredRxfillView(generics.ListCreateAPIView):
    queryset = Rxfill.objects.all().using("fred")
    serializer_class = FredRxfillSerializer
    pagination_class = StandardResultsSetPagination


class FredRxfillDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxfill.objects.all().using("fred")
    serializer_class = FredRxfillSerializer


class FredRxprintView(generics.ListCreateAPIView):
    queryset = Rxprint.objects.all().using("fred")
    serializer_class = FredRxprintSerializer
    pagination_class = StandardResultsSetPagination


class FredRxprintDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxprint.objects.all().using("fred")
    serializer_class = FredRxprintSerializer


class FredRxrawView(generics.ListCreateAPIView):
    queryset = Rxraw.objects.all().using("fred")
    serializer_class = FredRxrawSerializer
    pagination_class = StandardResultsSetPagination


class FredRxrawDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxraw.objects.all().using("fred")
    serializer_class = FredRxrawSerializer


class FredShipmentView(generics.ListCreateAPIView):
    queryset = Shipment.objects.all().using("fred")
    serializer_class = FredShipmentSerializer
    pagination_class = StandardResultsSetPagination


class FredShipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shipment.objects.all().using("fred")
    serializer_class = FredShipmentSerializer


class FredSkincarepairingsView(generics.ListCreateAPIView):
    queryset = Skincarepairings.objects.all().using("fred")
    serializer_class = FredSkincarepairingsSerializer
    pagination_class = StandardResultsSetPagination


class FredSkincarepairingsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Skincarepairings.objects.all().using("fred")
    serializer_class = FredSkincarepairingsSerializer


class FredStateView(generics.ListCreateAPIView):
    queryset = State.objects.all().using("fred")
    serializer_class = FredStateSerializer
    pagination_class = StandardResultsSetPagination


class FredStateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.all().using("fred")
    serializer_class = FredStateSerializer


class FredSubstatusView(generics.ListCreateAPIView):
    queryset = Substatus.objects.all().using("fred")
    serializer_class = FredSubstatusSerializer
    pagination_class = StandardResultsSetPagination


class FredSubstatusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Substatus.objects.all().using("fred")
    serializer_class = FredSubstatusSerializer


class FredTaskView(generics.ListCreateAPIView):
    queryset = Task.objects.all().using("fred")
    serializer_class = FredTaskSerializer
    pagination_class = StandardResultsSetPagination


class FredTaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all().using("fred")
    serializer_class = FredTaskSerializer


class FredTextsentView(generics.ListCreateAPIView):
    queryset = Textsent.objects.all().using("fred")
    serializer_class = FredTextsentSerializer
    pagination_class = StandardResultsSetPagination


class FredTextsentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Textsent.objects.all().using("fred")
    serializer_class = FredTextsentSerializer


class FredTokenView(generics.ListCreateAPIView):
    queryset = Token.objects.all().using("fred")
    serializer_class = FredTokenSerializer
    pagination_class = StandardResultsSetPagination


class FredTokenDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Token.objects.all().using("fred")
    serializer_class = FredTokenSerializer


class FredUpdatedskusView(generics.ListCreateAPIView):
    queryset = Updatedskus.objects.all().using("fred")
    serializer_class = FredUpdatedskusSerializer
    pagination_class = StandardResultsSetPagination


class FredUpdatedskusDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Updatedskus.objects.all().using("fred")
    serializer_class = FredUpdatedskusSerializer


class FredUsersView(generics.ListCreateAPIView):
    queryset = Users.objects.all().using("fred")
    serializer_class = FredUsersSerializer
    pagination_class = StandardResultsSetPagination


class FredUsersDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all().using("fred")
    serializer_class = FredUsersSerializer


class FredUserstateView(generics.ListCreateAPIView):
    queryset = Userstate.objects.all().using("fred")
    serializer_class = FredUserstateSerializer
    pagination_class = StandardResultsSetPagination


class FredUserstateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Userstate.objects.all().using("fred")
    serializer_class = FredUserstateSerializer


class FredDioItemsView(generics.ListCreateAPIView):
    queryset = DioItems.objects.all().using("fred")
    serializer_class = FredDioItemsSerializer
    pagination_class = StandardResultsSetPagination


class FredDioItemsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DioItems.objects.all().using("fred")
    serializer_class = FredDioItemsSerializer


class DioItemsSkuPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


class DioItemsSkuView(generics.ListAPIView, generics.UpdateAPIView):
    """
    API endpoint for retrieving dio items SKU data filtered by netsuiteid
    Requires 'netsuiteid' query parameter
    """

    serializer_class = DioItemsSkuSerializer
    pagination_class = DioItemsSkuPagination

    def validate_netsuiteid(self, netsuiteid):
        """Validate the netsuiteid parameter"""
        if not netsuiteid:
            raise ValidationError("netsuiteid parameter is required")

        # Remove any whitespace
        netsuiteid = str(netsuiteid).strip()

        # Check if netsuiteid contains only numeric characters
        if not re.match(r"^[0-9]+$", netsuiteid):
            raise ValidationError("netsuiteid parameter must be numeric")

        try:
            netsuiteid_int = int(netsuiteid)
            if netsuiteid_int < 1:
                raise ValidationError("netsuiteid must be greater than 0")
            return netsuiteid_int
        except ValueError:
            raise ValidationError("netsuiteid parameter must be a valid integer")

    def validate_page(self, page_str):
        """Validate the page parameter"""
        try:
            page = int(page_str)
            if page < 1:
                raise ValidationError("Page number must be greater than 0")
            return page
        except (ValueError, TypeError):
            raise ValidationError("Page parameter must be a valid integer")

    def get_queryset(self):
        return None

    def list(self, request, *args, **kwargs):
        try:
            # Validate input parameters
            netsuiteid_param = request.query_params.get("netsuiteid", None)
            page_param = request.query_params.get("page", "1")

            netsuiteid = self.validate_netsuiteid(netsuiteid_param)
            page = self.validate_page(page_param)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # SQL query based on your requirements
        base_query = """
        SELECT
            di.formulacode AS sku,
            di.active
        FROM dio_items di
        JOIN office o ON o.id = di.officeid
        WHERE o.netsuiteid = %s
        ORDER BY di.formulacode ASC
        """

        # Parameters for the query
        params = [netsuiteid]

        # Execute queries with proper error handling
        try:
            with connections["fred"].cursor() as cursor:
                # Get total count
                count_query = (
                    f"SELECT COUNT(*) as total_count FROM ({base_query}) as subquery"
                )
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()[0]

                # Calculate pagination with safety checks
                page_size = self.pagination_class.page_size
                if page_size <= 0:
                    page_size = 100  # fallback

                offset = (page - 1) * page_size
                total_pages = (
                    math.ceil(total_count / page_size) if total_count > 0 else 1
                )

                # Validate page number against total pages
                if page > total_pages and total_count > 0:
                    return Response(
                        {
                            "error": f"Page {page} does not exist. Total pages: {total_pages}"
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Add pagination to query
                paginated_query = f"{base_query} LIMIT %s OFFSET %s"
                paginated_params = params + [page_size, offset]

                # Execute main query
                cursor.execute(paginated_query, paginated_params)
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        except Exception as e:
            # Log the error (you should use proper logging here)
            print(f"Database error: {e}")
            return Response(
                {"error": "An error occurred while retrieving data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Serialize the data
        serializer = self.get_serializer(results, many=True)

        # Build pagination URLs
        next_page = None
        previous_page = None

        if page < total_pages:
            next_page = self._build_page_url(request, page + 1, netsuiteid)

        if page > 1:
            previous_page = self._build_page_url(request, page - 1, netsuiteid)

        return Response(
            {
                "count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "next": next_page,
                "previous": previous_page,
                "results": serializer.data,
            }
        )

    def _build_page_url(self, request, page_num, netsuiteid):
        """Helper method to build pagination URLs safely"""
        base_url = request.build_absolute_uri().split("?")[0]
        url = f"{base_url}?page={page_num}&netsuiteid={netsuiteid}"
        return url

    def patch(self, request, *args, **kwargs):
        """
        Update active status for dio items by netsuiteid and formulacode
        Expects JSON payload: {"formulacode": "SKU123", "active": true/false}
        """
        try:
            # Validate netsuiteid (reuse existing method)
            netsuiteid_param = request.query_params.get("netsuiteid", None)
            netsuiteid = self.validate_netsuiteid(netsuiteid_param)

            # Validate request data
            formulacode = request.data.get("formulacode")
            active = request.data.get("active")

            if not formulacode:
                raise ValidationError("formulacode is required in request body")
            if active is None:
                raise ValidationError("active is required in request body")
            if not isinstance(active, bool):
                raise ValidationError("active must be a boolean value")

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Update query
        update_query = """
        UPDATE dio_items 
        SET active = %s 
        WHERE formulacode = %s 
        AND officeid IN (SELECT id FROM office WHERE netsuiteid = %s)
        """

        try:
            with connections["fred"].cursor() as cursor:
                cursor.execute(update_query, [active, formulacode, netsuiteid])
                rows_affected = cursor.rowcount

            if rows_affected == 0:
                return Response(
                    {"error": "No matching record found to update"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {
                    "message": f"Successfully updated {rows_affected} record(s)",
                    "netsuiteid": netsuiteid,
                    "formulacode": formulacode,
                    "active": active,
                }
            )

        except Exception as e:
            print(f"Database error: {e}")
            return Response(
                {"error": "An error occurred while updating data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateFredPaymentView(APIView):
    """
    Create payment record - equivalent to createFredPayment function
    POST /payments/create/

    Expected payload:
    {
        "patientid": 123,
        "officeid": 456,
        "amount": 99.99,
        "txid": "tx_123abc",
        "sqrcid": "sqr_456def",
        "type": "payment",
        "status": "completed",
        "paymentProvider": "stripe",
        "discount": 10.00,
        "shippingcost": 5.99,
        "couponDiscountMap": {"SAVE10": 10.00}
    }
    """

    def post(self, request):
        """
        Create a new payment record
        """
        try:
            # Serialize and validate the input data
            serializer = PaymentCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create payment record within a transaction
            with transaction.atomic(using="fred"):
                payment = serializer.save()

                # Prepare response data
                response_serializer = PaymentResponseSerializer(payment)

                # Log successful creation
                logger.info(
                    f"Payment created successfully: ID {payment.id}, TX {payment.txid}"
                )

                return Response(
                    {
                        "message": "Payment created successfully",
                        "payment": response_serializer.data,
                        "id": payment.id,  # Return ID like the original function
                    },
                    status=status.HTTP_201_CREATED,
                )

        except IntegrityError as e:
            logger.error(f"Database integrity error creating payment: {e}")
            return Response(
                {"error": "Database constraint violation", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Unexpected error creating payment: {e}")
            return Response(
                {"error": "An error occurred while creating the payment"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateFredPaymentTransactionView(APIView):
    """
    Alternative endpoint that accepts transaction object structure
    POST /payments/create-transaction/

    Expected payload (transaction object):
    {
        "transaction": {
            "patientid": 123,
            "officeid": 456,
            "amount": 99.99,
            "txid": "tx_123abc",
            "sqrcid": "sqr_456def",
            "type": "payment",
            "status": "completed",
            "paymentProvider": "stripe",
            "discount": 10.00,
            "shippingcost": 5.99,
            "couponDiscountMap": {"SAVE10": 10.00}
        }
    }
    """

    def post(self, request):
        """
        Create payment from transaction object (matches original function signature)
        """
        try:
            transaction_data = request.data.get("transaction")
            if not transaction_data:
                return Response(
                    {"error": "Missing 'transaction' object in request body"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate transaction data
            transaction_serializer = PaymentTransactionSerializer(data=transaction_data)
            if not transaction_serializer.is_valid():
                return Response(
                    {
                        "error": "Invalid transaction data",
                        "details": transaction_serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create payment using the validated data
            payment_serializer = PaymentCreateSerializer(data=transaction_data)
            if not payment_serializer.is_valid():
                return Response(
                    {
                        "error": "Invalid payment data",
                        "details": payment_serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create payment record
            with transaction.atomic(using="fred"):
                payment = payment_serializer.save()

                # Return in format similar to original function (returns rows array)
                response_data = {
                    "id": payment.id,
                    "patientid": payment.patientid,
                    "officeid": payment.officeid,
                    "amount": payment.amount,
                    "txid": payment.txid,
                    "created": payment.created.isoformat() if payment.created else None,
                }

                logger.info(
                    f"Payment transaction created: ID {payment.id}, TX {payment.txid}"
                )

                return Response(
                    {
                        "rows": [
                            response_data
                        ],  # Match original function return format
                        "success": True,
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            logger.error(f"Error creating payment transaction: {e}")
            return Response(
                {"error": "An error occurred while creating the payment transaction"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BulkCreatePaymentsView(APIView):
    """
    Bulk create payments (useful for batch processing)
    POST /payments/bulk-create/

    Expected payload:
    {
        "payments": [
            {
                "patientid": 123,
                "officeid": 456,
                "amount": 99.99,
                ...
            },
            {
                "patientid": 124,
                "officeid": 456,
                "amount": 199.99,
                ...
            }
        ]
    }
    """

    def post(self, request):
        """
        Create multiple payment records in bulk
        """
        try:
            payments_data = request.data.get("payments", [])
            if not payments_data or not isinstance(payments_data, list):
                return Response(
                    {"error": "Expected 'payments' array in request body"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            created_payments = []
            errors = []

            with transaction.atomic(using="fred"):
                for i, payment_data in enumerate(payments_data):
                    serializer = PaymentCreateSerializer(data=payment_data)
                    if serializer.is_valid():
                        try:
                            payment = serializer.save()
                            created_payments.append(
                                {"index": i, "id": payment.id, "txid": payment.txid}
                            )
                        except Exception as e:
                            errors.append({"index": i, "error": str(e)})
                    else:
                        errors.append(
                            {
                                "index": i,
                                "error": "Validation failed",
                                "details": serializer.errors,
                            }
                        )

                # If any errors occurred, rollback the transaction
                if errors:
                    transaction.set_rollback(True, using="fred")
                    return Response(
                        {
                            "error": "Bulk create failed due to validation errors",
                            "errors": errors,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            logger.info(f"Bulk created {len(created_payments)} payments successfully")

            return Response(
                {
                    "message": f"Successfully created {len(created_payments)} payments",
                    "created_payments": created_payments,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error in bulk payment creation: {e}")
            return Response(
                {"error": "An error occurred during bulk payment creation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendManualPaymentTextView(APIView):
    """
    Send a payment text with DH url based on given Fill ID
    POST /rxfill/manual-payment-text/

    Expected payload:
    {
        "fillid": 1
    }
    """

    def post(self, request):
        """
        Get necessary payment text info
        """
        try:
            fillid = request.data.get("fillid", int)
            if not fillid or not isinstance(fillid, int):
                return Response(
                    {"error": "Expected 'fillid' integer in request body"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """
            Get a pay token for the rxfill if one exists
            """
            rxfill_token = Token.objects.filter(
                recordid=fillid, type__exact="pay", recordtype__exact="fill"
            ).exclude(status__exact="inactive")

            """
            Get the rxfill information
            """
            try:
                rxfill = Rxfill.objects.get(id=fillid)
            except Rxfill.DoesNotExist:
                return Response(
                    {"error": f"RxFill with id {fillid} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """
            Get the Rx Information
            """
            try:
                rx = Rx.objects.get(id=rxfill.rxid)
            except Rx.DoesNotExist:
                return Response(
                    {"error": f"Rx with id {rxfill.rxid} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """
            Get the Patient Information
            """
            try:
                patient = Patient.objects.get(id=rx.patientid)
            except Patient.DoesNotExist:
                return Response(
                    {"error": f"Patient with id {rx.patientid} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """
            Get the Medication information
            """
            try:
                medication = Medication.objects.get(ndc__exact=rx.medicationid)
            except Medication.DoesNotExist:
                return Response(
                    {"error": f"Medication with NDC {rx.medicationid} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """
            Get the fee of the medication
            """
            try:
                fee = Fee.objects.get(ndc__exact=medication.ndc)
            except Fee.DoesNotExist:
                return Response(
                    {"error": f"Fee with NDC {medication.ndc} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """
            Get the Office of the Rx
            """
            try:
                office = Office.objects.get(id=rx.officeid)
            except Office.DoesNotExist:
                return Response(
                    {"error": f"Office with id {rx.officeid} not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            """
            If the token does not exist, we need to create one, which will require some more information.
            """
            if not rxfill_token:
                token = Token(
                    token=secrets.token_urlsafe(8),
                    status="active",
                    type="pay",
                    recordtype="fill",
                    recordid=rxfill.id,
                    amount=rx.qty * fee.fee / 100,
                    created=timezone.now(),
                )
                token.save()
            else:
                token = rxfill_token[0]

            """
            Decide the verbiage of the text to send
            """
            dh_url = f"{settings.DH_APP_URL}/rx/{token.token}"
            msg = f"Your SKNV prescription is ready to ship. Please use this secure link to pay for your Rx and confirm your shipping address: {dh_url}"

            if rxfill.type == "newrx" and office.name is not None:
                msg = f"Your SKNV prescription from {office.name} is ready to ship. Please use this secure link to pay for your Rx and confirm your shipping address: {dh_url}"
            elif rxfill.type == "refill" and office.name is not None:
                msg = f"It’s time to refill your SKNV prescription from {office.name}. If you would like your refill, please use this secure link to pay & confirm your shipping address: {dh_url}"
            elif rxfill.type == "refill" and office.name is None:
                msg = f"It’s time to refill your SKNV prescription. If you would like your refill, please use this secure link to pay & confirm your shipping address: {dh_url}"

            """
            Send Text
            """
            try:
                text_sent_token = secrets.token_urlsafe().replace("_", "0")
                account_sid = settings.TWILIO_ACCOUNT_SID
                auth_token = settings.TWILIO_AUTH_TOKEN
                client = Client(account_sid, auth_token)

                twilio_message = client.messages.create(
                    from_=f"{settings.TWILIO_FROM_NUMBER}",
                    body=message,
                    to=phone,
                    status_callback=f"{settings.FRED_API}/text/update/{text_sent_token}",
                )
            except TwilioRestException as e:
                logger.error(f"Twilio REST API error: {e.code} - {e.msg}")

                # Handle specific Twilio error codes
                # Error codes reference: https://www.twilio.com/docs/api/errors

                # Unsubscribed/opted-out errors
                if e.code in [
                    21610,
                    21614,
                ]:  # 21610: unsubscribed, 21614: invalid for region
                    return Response(
                        {
                            "error": "Phone number cannot receive messages",
                            "details": e.msg,
                            "phone": phone,
                            "twilio_error_code": e.code,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Invalid phone number errors
                elif e.code in [21211, 21401, 21612, 21614]:
                    return Response(
                        {
                            "error": "Invalid phone number",
                            "details": e.msg,
                            "phone": phone,
                            "twilio_error_code": e.code,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Authentication/authorization errors
                elif e.code in [20003, 20005]:
                    return Response(
                        {
                            "error": "Twilio authentication failed",
                            "details": "Invalid Twilio credentials or permissions",
                            "twilio_error_code": e.code,
                        },
                        status=status.HTTP_503_SERVICE_UNAVAILABLE,
                    )

                # Rate limiting
                elif e.code == 20429:
                    return Response(
                        {
                            "error": "Rate limit exceeded",
                            "details": e.msg,
                            "twilio_error_code": e.code,
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )

                # Insufficient balance
                elif e.code == 21606:
                    return Response(
                        {
                            "error": "Insufficient Twilio account balance",
                            "details": e.msg,
                            "twilio_error_code": e.code,
                        },
                        status=status.HTTP_402_PAYMENT_REQUIRED,
                    )

                # Generic Twilio errors (4xx client errors vs 5xx server errors)
                elif 400 <= e.status < 500:
                    return Response(
                        {
                            "error": "Invalid request to Twilio",
                            "details": e.msg,
                            "twilio_error_code": e.code,
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    # Server-side Twilio errors
                    return Response(
                        {
                            "error": "Twilio service error",
                            "details": e.msg,
                            "twilio_error_code": e.code,
                        },
                        status=status.HTTP_502_BAD_GATEWAY,
                    )

            except Exception as e:
                logger.error(f"Unexpected error sending SMS: {e}")
                return Response(
                    {
                        "error": "Unexpected error sending SMS",
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            """
            Create TextSent Object in Fred DB
            """
            try:
                text_sent = Textsent(
                    patientid=patient.id,
                    rxid=rx.id,
                    type="payment-confirmation",
                    phonenumber=patient.phone,
                    sid=message.sid,
                    status=message.status,
                    message=(
                        message.error_message
                        if message.error_message is not None
                        else "The API request to send a message was successful and the message is queued to be sent out."
                    ),
                    token=text_sent_token,
                    datecreated=timezone.now(),
                    datemodified=None,
                )
                text_sent.save()
            except Exception as e:
                return Response(
                    {"error": f"Failed to create Textsent record"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "message": "Successfully sent message",
                    "textsentid": text_sent.id,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error in Manual Payment Text: {e}")
            return Response(
                {
                    "error": "An error occurred during manual payment text",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetCyberSourceCustomerView(APIView):
    """
    Get CyberSource customer ID from transaction ID
    POST /cybersource/get-customer/

    Expected payload:
    {
        "transaction_id": "67890123456789"
    }

    Response:
    {
        "transaction_id": "67890123456789",
        "customer_id": "customer_12345",
        "success": true,
        "message": "Customer ID retrieved successfully"
    }
    """

    def post(self, request):
        """
        Get customer ID from CyberSource transaction
        """
        try:
            # Import CyberSource SDK components
            try:
                from CyberSource import TransactionDetailsApi
                from CyberSource.rest import ApiException
                from .Configuration import configuration

            except ImportError as e:
                logger.error(f"CyberSource SDK not available: {e}")
                return Response(
                    {
                        "error": "CyberSource integration not configured",
                        "details": "Please install CyberSource SDK and configure credentials",
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # Import serializers
            from .serializers import (
                CyberSourceTransactionRequestSerializer,
                CyberSourceCustomerResponseSerializer,
            )

            # Validate input
            request_serializer = CyberSourceTransactionRequestSerializer(
                data=request.data
            )
            if not request_serializer.is_valid():
                return Response(
                    {
                        "error": "Invalid request data",
                        "details": request_serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transaction_id = request_serializer.validated_data["transaction_id"]

            # Call CyberSource API
            try:
                api_instance = TransactionDetailsApi(merchant_config=configuration)
                api_response, api_status, body = api_instance.get_transaction(
                    transaction_id
                )

                # Convert to dict
                if hasattr(api_response, "to_dict"):
                    response_dict = api_response.to_dict()
                elif hasattr(api_response, "__dict__"):
                    response_dict = api_response.__dict__
                else:
                    logger.warning(
                        f"Unexpected response format for transaction {transaction_id}"
                    )
                    return Response(
                        {
                            "transaction_id": transaction_id,
                            "customer_id": None,
                            "success": False,
                            "message": "Unexpected response format from CyberSource",
                        },
                        status=status.HTTP_200_OK,
                    )

                # Extract token_information.customer.id
                customer_id = None
                if (
                    "token_information" in response_dict
                    and isinstance(response_dict["token_information"], dict)
                    and "customer" in response_dict["token_information"]
                    and isinstance(response_dict["token_information"]["customer"], dict)
                    and "id" in response_dict["token_information"]["customer"]
                ):
                    customer_id = response_dict["token_information"]["customer"]["id"]
                    customer_id = str(customer_id).strip() if customer_id else None

                # Prepare response
                if customer_id:
                    response_data = {
                        "transaction_id": transaction_id,
                        "customer_id": customer_id,
                        "success": True,
                        "message": "Customer ID retrieved successfully",
                    }
                    logger.info(
                        f"Retrieved customer ID {customer_id} for transaction {transaction_id}"
                    )
                else:
                    response_data = {
                        "transaction_id": transaction_id,
                        "customer_id": None,
                        "success": False,
                        "message": "No customer ID found in transaction",
                    }
                    logger.warning(
                        f"No customer ID found for transaction {transaction_id}"
                    )

                response_serializer = CyberSourceCustomerResponseSerializer(
                    data=response_data
                )
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(response_data, status=status.HTTP_200_OK)

            except ApiException as e:
                logger.error(
                    f"CyberSource API error for transaction {transaction_id}: {e.status} - {e.reason}"
                )

                # Handle different error codes
                if e.status == 404:
                    return Response(
                        {
                            "transaction_id": transaction_id,
                            "customer_id": None,
                            "success": False,
                            "message": "Transaction not found",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                elif e.status == 401:
                    return Response(
                        {
                            "error": "Authentication failed",
                            "message": "Invalid CyberSource credentials",
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                elif e.status == 403:
                    return Response(
                        {
                            "error": "Access denied",
                            "message": "Insufficient permissions to access transaction",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                else:
                    return Response(
                        {
                            "error": "CyberSource API error",
                            "message": f"Status: {e.status}, Reason: {e.reason}",
                        },
                        status=status.HTTP_502_BAD_GATEWAY,
                    )

        except Exception as e:
            logger.error(f"Unexpected error in GetCyberSourceCustomerView: {e}")
            return Response(
                {
                    "error": "An error occurred while retrieving customer information",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetCyberSourceCustomerFromTransactionIdView(APIView):
    """
    Get CyberSource customer ID from transaction ID (alternative endpoint with transaction_id in URL)
    GET /cybersource/transaction/{transaction_id}/customer/

    Response:
    {
        "transaction_id": "67890123456789",
        "customer_id": "customer_12345",
        "success": true
    }
    """

    def get(self, request, transaction_id):
        """
        Get customer ID from CyberSource transaction using transaction_id from URL
        """
        try:
            # Import CyberSource SDK components
            try:
                from CyberSource import TransactionDetailsApi
                from CyberSource.rest import ApiException
                from .Configuration import configuration

            except ImportError as e:
                logger.error(f"CyberSource SDK not available: {e}")
                return Response(
                    {
                        "error": "CyberSource integration not configured",
                        "details": "Please install CyberSource SDK and configure credentials",
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # Validate transaction_id from URL
            if not transaction_id or not transaction_id.strip():
                return Response(
                    {"error": "Transaction ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            transaction_id = transaction_id.strip()

            # Call CyberSource API
            try:
                api_instance = TransactionDetailsApi(merchant_config=configuration)
                api_response, api_status, body = api_instance.get_transaction(
                    transaction_id
                )

                # Convert to dict
                if hasattr(api_response, "to_dict"):
                    response_dict = api_response.to_dict()
                elif hasattr(api_response, "__dict__"):
                    response_dict = api_response.__dict__
                else:
                    return Response(
                        {
                            "transaction_id": transaction_id,
                            "customer_id": None,
                            "success": False,
                            "message": "Unexpected response format from CyberSource",
                        }
                    )

                # Extract customer ID
                customer_id = None
                if (
                    "token_information" in response_dict
                    and isinstance(response_dict["token_information"], dict)
                    and "customer" in response_dict["token_information"]
                    and isinstance(response_dict["token_information"]["customer"], dict)
                    and "id" in response_dict["token_information"]["customer"]
                ):
                    customer_id = response_dict["token_information"]["customer"]["id"]
                    customer_id = str(customer_id).strip() if customer_id else None

                # Return response
                if customer_id:
                    logger.info(
                        f"Retrieved customer ID {customer_id} for transaction {transaction_id}"
                    )
                    return Response(
                        {
                            "transaction_id": transaction_id,
                            "customer_id": customer_id,
                            "success": True,
                        }
                    )
                else:
                    logger.warning(
                        f"No customer ID found for transaction {transaction_id}"
                    )
                    return Response(
                        {
                            "transaction_id": transaction_id,
                            "customer_id": None,
                            "success": False,
                            "message": "No customer ID found in transaction",
                        }
                    )

            except ApiException as e:
                logger.error(
                    f"CyberSource API error for transaction {transaction_id}: {e.status} - {e.reason}"
                )

                if e.status == 404:
                    return Response(
                        {
                            "transaction_id": transaction_id,
                            "customer_id": None,
                            "success": False,
                            "message": "Transaction not found",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
                else:
                    return Response(
                        {
                            "error": "CyberSource API error",
                            "message": f"Status: {e.status}, Reason: {e.reason}",
                        },
                        status=status.HTTP_502_BAD_GATEWAY,
                    )

        except Exception as e:
            logger.error(
                f"Unexpected error in GetCyberSourceCustomerFromTransactionIdView: {e}"
            )
            return Response(
                {"error": "An error occurred while retrieving customer information"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MatchPaymentToRxFillView(APIView):
    """
    Match a payment to an RxFill and update statuses
    POST /payments/match-to-rxfill/

    Expected payload:
    {
        "payment_id": 123,
        "rxfill_id": 456,
        "medication_id": "00002-1234-56",  # optional, for validation
        "qty": 1  # optional, defaults to 1. Valid values: 1, 2, 3
    }

    Qty behavior:
    - qty = 1 (default): Standard single order
    - qty = 2: Sets rxfill.istwoqty = True
    - qty = 3: Sets rxfill.isbulk = True
    """

    def post(self, request):
        try:
            serializer = PaymentMatchSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment_id = request.data.get("payment_id")
            rxfill_id = request.data.get("rxfill_id")
            medication_id = request.data.get("medication_id")
            qty = request.data.get("qty", 1)

            if qty not in [1, 2, 3]:
                return Response(
                    {"error": "qty must be 1, 2, or 3"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic(using="fred"):
                # Get the RxFill record
                try:
                    rxfill = (
                        Rxfill.objects.using("fred")
                        .select_for_update()
                        .get(id=rxfill_id)
                    )
                except Rxfill.DoesNotExist:
                    return Response(
                        {"error": f"RxFill with id {rxfill_id} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Get the Payment record
                try:
                    payment = (
                        Payment.objects.using("fred")
                        .select_for_update()
                        .get(id=payment_id)
                    )
                except Payment.DoesNotExist:
                    return Response(
                        {"error": f"Payment with id {payment_id} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # Get the Rx record for validation
                try:
                    rx = Rx.objects.using("fred").get(id=rxfill.rxid)
                except Rx.DoesNotExist:
                    return Response(
                        {"error": f"Rx with id {rxfill.rxid} not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                if payment.status == "matched":
                    # Check if it's matched to a different RxFill
                    existing_rxfill = (
                        Rxfill.objects.using("fred")
                        .filter(paymentid=payment.id)
                        .first()
                    )

                    if existing_rxfill and existing_rxfill.id != rxfill_id:
                        return Response(
                            {
                                "error": f"Payment {payment_id} is already matched to RxFill {existing_rxfill.id}",
                                "existing_rxfill_id": existing_rxfill.id,
                            },
                            status=status.HTTP_409_CONFLICT,
                        )

                # Validate Rx status
                if rx.status != "ok":
                    return Response(
                        {
                            "error": f"Rx status is '{rx.status}', must be 'ok' to match payment"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Validate medication if provided
                if medication_id and rx.medicationid != medication_id:
                    return Response(
                        {"error": "Medication ID does not match Rx"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Check if RxFill is in paymentHold status and has no payment linked
                if rxfill.status == "paymentHold" and rxfill.paymentid is None:
                    # Check if medication exists
                    try:
                        medication = Medication.objects.using("fred").get(
                            ndc=rx.medicationid
                        )
                        rxfill.status = "toFill"
                    except Medication.DoesNotExist:
                        rxfill.status = "medNotFound"
                        logger.warning(
                            f"Medication {rx.medicationid} not found for RxFill {rxfill_id}"
                        )

                    # Link payment to rxfill
                    rxfill.paymentid = payment.id

                    if qty == 2:
                        rxfill.istwoqty = True
                        rxfill.isbulk = False  # Ensure isbulk is False for qty=2
                        logger.info(f"Setting istwoqty=True for RxFill {rxfill_id}")
                    elif qty == 3:
                        rxfill.isbulk = True
                        rxfill.istwoqty = False  # Ensure istwoqty is False for qty=3
                        logger.info(f"Setting isbulk=True for RxFill {rxfill_id}")
                    else:  # qty == 1
                        rxfill.istwoqty = False
                        rxfill.isbulk = False

                    # Update the qty field on rxfill
                    rxfill.qty = qty

                    rxfill.save(using="fred")

                    # Update payment status to matched
                    payment.status = "matched"
                    payment.save(using="fred")

                    logger.info(
                        f"Matched Payment {payment_id} to RxFill {rxfill_id}, "
                        f"status: {rxfill.status}, qty: {qty}, "
                        f"istwoqty: {rxfill.istwoqty}, isbulk: {rxfill.isbulk}"
                    )

                    return Response(
                        {
                            "message": "Payment matched to RxFill successfully",
                            "rxfill_id": rxfill.id,
                            "rxfill_status": rxfill.status,
                            "payment_id": payment.id,
                            "payment_status": payment.status,
                            "qty": qty,
                            "istwoqty": rxfill.istwoqty,
                            "isbulk": rxfill.isbulk,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            "error": f"RxFill is not eligible for payment matching. Status: {rxfill.status}, "
                            f"Current payment_id: {rxfill.paymentid}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:
            logger.error(f"Error matching payment to rxfill: {e}")
            return Response(
                {"error": "An error occurred while matching payment to rxfill"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SendCustomSMSView(APIView):
    """
    Send a custom SMS message to a phone number
    POST /sms/send/

    Expected payload:
    {
        "phone": "+1234567890",
        "message": "Your custom message here",
        "patient_id": 123,  # optional
        "rx_id": 456,       # optional
        "type": "custom"    # optional, defaults to "custom"
    }
    """

    def post(self, request):
        try:
            phone = request.data.get("phone")
            message = request.data.get("message")
            patient_id = request.data.get("patient_id")
            rx_id = request.data.get("rx_id")
            msg_type = request.data.get("type", "custom")

            # Validation
            if not phone or not message:
                return Response(
                    {"error": "phone and message are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate phone number format (basic validation)
            phone = str(phone).strip()
            if not phone.startswith("+"):
                return Response(
                    {
                        "error": "Phone number must include country code (e.g., +1234567890)"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate message length (Twilio has a 1600 character limit)
            if len(message) > 1600:
                return Response(
                    {"error": "Message exceeds maximum length of 1600 characters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Send via Twilio
            try:
                text_sent_token = secrets.token_urlsafe().replace("_", "0")
                account_sid = settings.TWILIO_ACCOUNT_SID
                auth_token = settings.TWILIO_AUTH_TOKEN
                client = Client(account_sid, auth_token)

                twilio_message = client.messages.create(
                    from_=f"{settings.TWILIO_FROM_NUMBER}",
                    body=message,
                    to=phone,
                    status_callback=f"{settings.FRED_API}/text/update/{text_sent_token}",
                )
            except Exception as e:
                logger.error(f"Twilio API error: {e}")
                return Response(
                    {"error": "Failed to send SMS via Twilio", "details": str(e)},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            # Create TextSent record
            try:
                text_sent = Textsent(
                    patientid=patient_id,
                    rxid=rx_id,
                    type=msg_type,
                    phonenumber=phone,
                    sid=twilio_message.sid,
                    status=twilio_message.status,
                    message=(
                        twilio_message.error_message
                        if twilio_message.error_message is not None
                        else "Message queued successfully"
                    ),
                    token=text_sent_token,
                    datecreated=timezone.now(),
                    datemodified=None,
                )
                text_sent.save(using="fred")
            except Exception as e:
                logger.error(f"Failed to create Textsent record: {e}")
                # SMS was sent but we couldn't log it - still return success
                return Response(
                    {
                        "message": "SMS sent successfully but failed to log",
                        "sid": twilio_message.sid,
                        "status": twilio_message.status,
                        "warning": "Database logging failed",
                    },
                    status=status.HTTP_201_CREATED,
                )

            logger.info(
                f"Custom SMS sent successfully: SID {twilio_message.sid}, to {phone}"
            )

            return Response(
                {
                    "message": "SMS sent successfully",
                    "textsent_id": text_sent.id,
                    "sid": twilio_message.sid,
                    "status": twilio_message.status,
                    "phone": phone,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Unexpected error sending custom SMS: {e}")
            return Response(
                {"error": "An error occurred while sending SMS", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RefillsNoPaymentPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = "limit"
    max_page_size = 5000

    def get_paginated_response(self, data):
        return Response(
            {
                "data": data,
                "pagination": {
                    "current_page": self.page.number,
                    "total_pages": self.page.paginator.num_pages,
                    "total_records": self.page.paginator.count,
                    "per_page": self.page_size,
                    "has_more": self.page.has_next(),
                },
                "filters": getattr(self, "filters_data", {}),
            }
        )


class NoPaymentBaseView(generics.ListAPIView):
    """
    Base class for retrieving prescriptions with no payment
    Handles common logic for both newrx and refills
    """

    serializer_class = RefillsNoPaymentSerializer
    pagination_class = RefillsNoPaymentPagination

    rx_type = None
    include_refills_condition = False
    calculate_fill_numbers = False

    def get_queryset(self):
        """Returns None as we're using raw SQL queries"""
        return None

    def list(self, request, *args, **kwargs):
        """Override list method to handle raw SQL queries and custom formatting"""
        try:
            query_serializer = self.get_query_serializer()(data=request.query_params)
            if not query_serializer.is_valid():
                return Response(
                    {"error": "Invalid parameters", "details": query_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_params = query_serializer.validated_data
            days = validated_params["days"]
            page = validated_params["page"]
            limit = validated_params["limit"]

            date_filter = (datetime.now() - timedelta(days=days)).strftime(
                "%Y-%m-%d 00:00:00"
            )
            offset = (page - 1) * limit
            filters_data = {"days": days, "date_from": date_filter}

            main_query = self._build_main_query()
            count_query = self._build_count_query()

            with connections["fred"].cursor() as cursor:
                cursor.execute(count_query, [date_filter])
                total = cursor.fetchone()[0]

                cursor.execute(main_query, [date_filter, limit, offset])
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            fill_numbers = {}
            if self.calculate_fill_numbers:
                fill_numbers = self._calculate_fill_numbers(results)

            formatted_data = self._format_results(results, fill_numbers)
            serializer = self.get_serializer(formatted_data, many=True)
            total_pages = math.ceil(total / limit) if total > 0 else 1

            if page > total_pages and total > 0:
                return Response(
                    {
                        "error": f"Page {page} does not exist. Total pages: {total_pages}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            response_data = {
                "data": serializer.data,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_records": total,
                    "per_page": limit,
                    "has_more": (page * limit) < total,
                },
                "filters": filters_data,
            }

            if self.rx_type == "newrx":
                response_data["type"] = "newrx"

            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            return Response(
                {"error": "An error occurred while retrieving data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_query_serializer(self):
        """Return appropriate query serializer - can be overridden by child classes"""
        if self.rx_type == "newrx":
            return NewRxNoPaymentQuerySerializer
        return RefillsNoPaymentQuerySerializer

    def _build_main_query(self):
        """Build main SQL query based on rx_type"""
        refills_condition = (
            "AND rx.refills > 0" if self.include_refills_condition else ""
        )

        return f"""
            SELECT 
                p.id,
                p.name,
                p.dob,
                p.phone,
                p.email,
                a.city,
                a.state,
                rx.id AS "rxId",
                rxF.created,
                o.id AS "officeId",
                o.name AS "officeName",
                m.indication AS indication,
                rxF.id AS "fillId",
                rxF.status AS "fillStatus",
                rx.virx AS virx,
                po.call_outcome AS "callOutcome",
                po.outreach_attempt AS "outreachAttempt",
                po.call_summary AS "callSummary",
                po.call_back AS "callBack",
                CASE WHEN t.id IS NOT NULL THEN TRUE ELSE FALSE END AS tasked
            FROM rxfill rxF
            INNER JOIN rx ON rx.id = rxF.rxid
            INNER JOIN office o ON o.id = rx.officeid
            INNER JOIN patient p ON p.id = rx.patientid
            INNER JOIN address a ON a.id = p.addressid
            LEFT JOIN medication m ON m.ndc = rx.medicationid
            LEFT JOIN patient_outreach po ON po.rx_fillid = rxF.id
            LEFT JOIN task t 
                ON t.rxid = rx.id
                AND t.patientid = p.id
                AND t.type = 'call-for-payment' 
                AND t.csfillid = rxF.id
            WHERE rx.status = 'ok'
                {refills_condition}
                AND rxF.type = '{self.rx_type}'
                AND rxF.paymentid IS NULL
                AND rxF.created > %s
            ORDER BY rxF.created ASC
            LIMIT %s OFFSET %s
        """

    def _build_count_query(self):
        """Build count SQL query based on rx_type"""
        refills_condition = (
            "AND rx.refills > 0" if self.include_refills_condition else ""
        )

        return f"""
            SELECT COUNT(*) as total
            FROM rxfill rxF
            INNER JOIN rx ON rx.id = rxF.rxid
            WHERE rx.status = 'ok'
                {refills_condition}
                AND rxF.type = '{self.rx_type}'
                AND rxF.paymentid IS NULL
                AND rxF.created > %s
        """

    def _calculate_fill_numbers(self, results):
        """Calculate fill numbers for each rx - only used for refills"""
        fill_numbers = {}

        if not results:
            return fill_numbers

        rx_ids = [row["rxId"] for row in results]
        placeholders = ",".join(["%s"] * len(rx_ids))

        fill_number_query = f"""
        SELECT rf.id as fillId, rf.rxid as rxId, rf.created as fillCreated
        FROM rxfill rf
        WHERE rf.type = '{self.rx_type}'
            AND rf.rxid IN ({placeholders})
        ORDER BY rf.rxid ASC, rf.created ASC
        """

        with connections["fred"].cursor() as cursor:
            cursor.execute(fill_number_query, rx_ids)
            fill_results = cursor.fetchall()
            rx_fill_counts = {}
            for fill in fill_results:
                fill_id, rx_id, fill_created = fill

                if rx_id not in rx_fill_counts:
                    rx_fill_counts[rx_id] = 0

                rx_fill_counts[rx_id] += 1
                fill_numbers[fill_id] = rx_fill_counts[rx_id]

        return fill_numbers

    def _format_results(self, results, fill_numbers):
        """Format raw query results with computed fields"""
        formatted_data = []

        for row in results:
            if row["phone"] and len(str(row["phone"])) >= 10:
                phone = str(row["phone"])
                row["formattedPhone"] = f"{phone[0:3]}-{phone[3:6]}-{phone[6:10]}"
            else:
                row["formattedPhone"] = row["phone"] or ""

            row["formattedDob"] = self._format_date(row["dob"], "%m/%d/%Y")

            if row["created"]:
                if isinstance(row["created"], str):
                    try:
                        created_dt = datetime.strptime(
                            row["created"], "%Y-%m-%d %H:%M:%S"
                        )
                        row["formattedCreated"] = created_dt.strftime("%m/%d/%Y")
                        row["sortableCreated"] = created_dt.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    except:
                        row["formattedCreated"] = row["created"]
                        row["sortableCreated"] = row["created"]
                else:
                    row["formattedCreated"] = row["created"].strftime("%m/%d/%Y")
                    row["sortableCreated"] = row["created"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
            else:
                row["formattedCreated"] = "N/A"
                row["sortableCreated"] = ""

            row["formattedLocation"] = f"{row['city'] or ''}, {row['state'] or ''}"

            row["fillNumber"] = (
                fill_numbers.get(row["fillId"]) if fill_numbers else None
            )

            row["fillType"] = self._determine_fill_type(
                row.get("virx", False), row.get("fillStatus", "")
            )

            formatted_data.append(row)

        return formatted_data

    def _format_date(self, date_value, format_str):
        """Helper method to format dates consistently"""
        if not date_value:
            return "N/A"

        if isinstance(date_value, str):
            try:
                dob_str = str(date_value).strip()
                if " " in dob_str:
                    dob_dt = datetime.strptime(dob_str, "%Y-%m-%d %H:%M:%S")
                elif "-" in dob_str:
                    dob_dt = datetime.strptime(dob_str, "%Y-%m-%d")
                elif len(dob_str) == 8 and dob_str.isdigit():
                    dob_dt = datetime.strptime(dob_str, "%Y%m%d")
                else:
                    return dob_str
                return dob_dt.strftime(format_str)
            except:
                return date_value
        else:
            return date_value.strftime(format_str)

    def _determine_fill_type(self, virx, fill_status):
        """Determine fill type based on virx and fill status"""
        if virx:
            return "MSC"
        elif fill_status in [
            "dispensedInOffice",
            "verifyInOfficeDispenseNoLot",
            "verifyInOfficeDispenseNoOffice",
        ]:
            return "DIO"
        else:
            return "DTP"


class RefillsNoPaymentView(NoPaymentBaseView):
    """
    API endpoint for retrieving refills with no payment
    GET /refills-no-payment/?days=30&page=1&limit=5000

    Query Parameters:
    - days: Number of days to look back (default: 30, min: 1, max: 365)
    - page: Page number (default: 1)
    - limit: Records per page (default: 1000, max: 5000)
    """

    rx_type = "refill"
    include_refills_condition = True
    calculate_fill_numbers = True


class NewRxNoPaymentView(NoPaymentBaseView):
    """
    API endpoint for retrieving new prescriptions with no payment
    GET /newrx-no-payment/?days=30&page=1&limit=5000

    Query Parameters:
    - days: Number of days to look back (default: 30, min: 1, max: 365)
    - page: Page number (default: 1)
    - limit: Records per page (default: 1000, max: 5000)
    """

    rx_type = "newrx"
    include_refills_condition = False
    calculate_fill_numbers = False
