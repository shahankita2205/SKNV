from rest_framework import generics
from django.shortcuts import get_object_or_404
from .models import (
    Activitylog,
    Address,
    Authevent,
    Baseelement,
    Clindiff,
    Clindiffview,
    Coachingreport,
    Coachingreportinprogress,
    Coachingreportsignature,
    Commercialmedication,
    Commercialproduct,
    Commercialproductingredient,
    Company,
    Concern,
    Conditions,
    Consentsignature,
    Correctorrequest,
    Cosmetic,
    Cosmeticleaflet,
    Dermacode,
    Dermacodecosmetic,
    Dermacodeprintout,
    Dispense,
    Dispenseitem,
    Dispenseitemdeletion,
    Educatedperson,
    Educatedpersonsignature,
    Emaillist,
    Employee,
    Formula,
    Formulaingredient,
    Formulapreorder,
    Formularequest,
    Formularequestcomment,
    Ingredient,
    Ingredientconcern,
    Inventory,
    Ipwhitelist,
    Issue,
    Leaflet,
    LeafletIngredient,
    Legalinfo,
    Lotnumber,
    Medspasalesdio,
    Medspasalesiou,
    Medicationassessment,
    Newpermission,
    Newsalesresource,
    Nsendpoints,
    Nsorder,
    Nsorderitem,
    Nsordertracking,
    Office,
    Officeipaduser,
    Officepatient,
    Officepermission,
    Officephysician,
    Officephysicianexclusion,
    Outgoingemail,
    Patient,
    Patientphysician,
    Pcdcontract,
    PcinvPcinventoryItems,
    Permission,
    Phinxlog,
    Physician,
    Quote,
    Refillreminder,
    Refundrequest,
    Replacementmachinerequest,
    Role,
    RolePermission,
    Rxbestmedspa,
    Rxbestnumbingdio,
    Rxbestpodiatry,
    Rxbestseller,
    RxbestsellerCopy1,
    Rxblt,
    Rxconsent,
    Saascontract,
    Salescontract,
    Salesorder,
    Salesorderproduct,
    Salesresource,
    Salesresourcecategory,
    Shipment,
    Skincarecorrector,
    Sknvcosmeticleaflet,
    Sknvrxleaflet,
    Smscontract,
    Subelitecontract,
    Subelitepluscontract,
    Token,
    Totaladl,
    Tsacontract,
    Usercompany,
    Userhierarchy,
    Usermeta,
    Useroffice,
    Users,
    W9,
)
from .serializers import (
    MySKNVActivitylogSerializer,
    MySKNVAddressSerializer,
    MySKNVAutheventSerializer,
    MySKNVBaseelementSerializer,
    MySKNVClindiffSerializer,
    MySKNVClindiffviewSerializer,
    MySKNVCoachingreportSerializer,
    MySKNVCoachingreportinprogressSerializer,
    MySKNVCoachingreportsignatureSerializer,
    MySKNVCommercialMedicationSerializer,
    MySKNVCommercialProductSerializer,
    MySKNVCommercialProductIngredientSerializer,
    MySKNVCompanySerializer,
    MySKNVConcernSerializer,
    MySKNVConditionsSerializer,
    MySKNVConsentSignatureSerializer,
    MySKNVCorrectorRequestSerializer,
    MySKNVCosmeticSerializer,
    MySKNVCosmeticLeafletSerializer,
    MySKNVDermacodeSerializer,
    MySKNVDermacodeCosmeticSerializer,
    MySKNVDermacodePrintoutSerializer,
    MySKNVDispenseSerializer,
    MySKNVDispenseItemSerializer,
    MySKNVDispenseItemDeletionSerializer,
    MySKNVEducatedpersonSerializer,
    MySKNVEducatedPersonSignatureSerializer,
    MySKNVEmailListSerializer,
    MySKNVEmployeeSerializer,
    MySKNVFormulaSerializer,
    MySKNVFormulaIngredientSerializer,
    MySKNVFormulaPreorderSerializer,
    MySKNVFormulaRequestSerializer,
    MySKNVFormulaRequestCommentSerializer,
    MySKNVIngredientSerializer,
    MySKNVIngredientConcernSerializer,
    MySKNVInventorySerializer,
    MySKNVIpwhitelistSerializer,
    MySKNVIssueSerializer,
    MySKNVLeafletSerializer,
    MySKNVLeafletIngredientSerializer,
    MySKNVLegalInfoSerializer,
    MySKNVLotNumberSerializer,
    MySKNVMedSpaSalesDioSerializer,
    MySKNVMedSpaSalesIouSerializer,
    MySKNVMedicationAssessmentSerializer,
    MySKNVNewPermissionSerializer,
    MySKNVNewSalesResourceSerializer,
    MySKNVNsEndpointsSerializer,
    MySKNVNsOrderSerializer,
    MySKNVNsOrderItemSerializer,
    MySKNVNsOrderTrackingSerializer,
    MySKNVOfficeSerializer,
    MySKNVOfficeIpaduserSerializer,
    MySKNVOfficePatientSerializer,
    MySKNVOfficePermissionSerializer,
    MySKNVOfficePhysicianSerializer,
    MySKNVOfficePhysicianExclusionSerializer,
    MySKNVOutgoingEmailSerializer,
    MySKNVPatientSerializer,
    MySKNVPatientPhysicianSerializer,
    MySKNVPcdContractSerializer,
    MySKNVPcinvPcinventoryItemsSerializer,
    MySKNVPermissionSerializer,
    MySKNVPhinxlogSerializer,
    MySKNVPhysicianSerializer,
    MySKNVQuoteSerializer,
    MySKNVRefillReminderSerializer,
    MySKNVRefundRequestSerializer,
    MySKNVReplacementMachineRequestSerializer,
    MySKNVRoleSerializer,
    MySKNVRolePermissionSerializer,
    MySKNVRxBestMedSpaSerializer,
    MySKNVRxBestNumbingDioSerializer,
    MySKNVRxBestPodiatrySerializer,
    MySKNVRxBestSellerSerializer,
    MySKNVRxBestSellerCopy1Serializer,
    MySKNVRxBltSerializer,
    MySKNVRxConsentSerializer,
    MySKNVSaasContractSerializer,
    MySKNVSalesContractSerializer,
    MySKNVSalesOrderSerializer,
    MySKNVSalesOrderProductSerializer,
    MySKNVSalesResourceSerializer,
    MySKNVSalesResourceCategorySerializer,
    MySKNVShipmentSerializer,
    MySKNVSkincareCorrectorSerializer,
    MySKNVSknvCosmeticLeafletSerializer,
    MySKNVSknvRxLeafletSerializer,
    MySKNVSmsContractSerializer,
    MySKNVSubEliteContractSerializer,
    MySKNVSubElitePlusContractSerializer,
    MySKNVTokenSerializer,
    MySKNVTotalAdlSerializer,
    MySKNVTsaContractSerializer,
    MySKNVUserCompanySerializer,
    MySKNVUserHierarchySerializer,
    MySKNVUserMetaSerializer,
    MySKNVUserOfficeSerializer,
    MySKNVUsersSerializer,
    MySKNVW9Serializer,
)


# Activitylog views
class ActivitylogView(generics.ListCreateAPIView):
    queryset = Activitylog.objects.all().using("mysknv")
    serializer_class = MySKNVActivitylogSerializer


class ActivitylogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Activitylog.objects.all().using("mysknv")
    serializer_class = MySKNVActivitylogSerializer


# Address views
class AddressView(generics.ListCreateAPIView):
    queryset = Address.objects.all().using("mysknv")
    serializer_class = MySKNVAddressSerializer


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all().using("mysknv")
    serializer_class = MySKNVAddressSerializer


# Authevent views
class AutheventView(generics.ListCreateAPIView):
    queryset = Authevent.objects.all().using("mysknv")
    serializer_class = MySKNVAutheventSerializer


class AutheventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Authevent.objects.all().using("mysknv")
    serializer_class = MySKNVAutheventSerializer


# Baseelement views
class BaseelementView(generics.ListCreateAPIView):
    queryset = Baseelement.objects.all().using("mysknv")
    serializer_class = MySKNVBaseelementSerializer


class BaseelementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Baseelement.objects.all().using("mysknv")
    serializer_class = MySKNVBaseelementSerializer


# Clindiff views
class ClindiffView(generics.ListCreateAPIView):
    queryset = Clindiff.objects.all().using("mysknv")
    serializer_class = MySKNVClindiffSerializer


class ClindiffDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clindiff.objects.all().using("mysknv")
    serializer_class = MySKNVClindiffSerializer
    lookup_field = "formulaCode"


# Clindiffview views
class ClindiffviewView(generics.ListCreateAPIView):
    queryset = Clindiffview.objects.all().using("mysknv")
    serializer_class = MySKNVClindiffviewSerializer


class ClindiffviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clindiffview.objects.all().using("mysknv")
    serializer_class = MySKNVClindiffviewSerializer


# Coachingreport views
class CoachingreportView(generics.ListCreateAPIView):
    queryset = Coachingreport.objects.all().using("mysknv")
    serializer_class = MySKNVCoachingreportSerializer


class CoachingreportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coachingreport.objects.all().using("mysknv")
    serializer_class = MySKNVCoachingreportSerializer


# Coachingreportinprogress views
class CoachingreportinprogressView(generics.ListCreateAPIView):
    queryset = Coachingreportinprogress.objects.all().using("mysknv")
    serializer_class = MySKNVCoachingreportinprogressSerializer


class CoachingreportinprogressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coachingreportinprogress.objects.all().using("mysknv")
    serializer_class = MySKNVCoachingreportinprogressSerializer


# Coachingreportsignature views
class CoachingreportsignatureView(generics.ListCreateAPIView):
    queryset = Coachingreportsignature.objects.all().using("mysknv")
    serializer_class = MySKNVCoachingreportsignatureSerializer


class CoachingreportsignatureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coachingreportsignature.objects.all().using("mysknv")
    serializer_class = MySKNVCoachingreportsignatureSerializer


# Commercialmedication views
class CommercialMedicationView(generics.ListCreateAPIView):
    queryset = Commercialmedication.objects.all().using("mysknv")
    serializer_class = MySKNVCommercialMedicationSerializer


class CommercialMedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Commercialmedication.objects.all().using("mysknv")
    serializer_class = MySKNVCommercialMedicationSerializer


# Commercialproduct views
class CommercialProductView(generics.ListCreateAPIView):
    queryset = Commercialproduct.objects.all().using("mysknv")
    serializer_class = MySKNVCommercialProductSerializer


class CommercialProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Commercialproduct.objects.all().using("mysknv")
    serializer_class = MySKNVCommercialProductSerializer


# Commercialproductingredient views
class CommercialProductIngredientView(generics.ListCreateAPIView):
    queryset = Commercialproductingredient.objects.all().using("mysknv")
    serializer_class = MySKNVCommercialProductIngredientSerializer


class CommercialProductIngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Commercialproductingredient.objects.all().using("mysknv")
    serializer_class = MySKNVCommercialProductIngredientSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        ingredient_id = self.kwargs.get("ingredientId")
        commercial_product_id = self.kwargs.get("commercialProductId")
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            ingredientId=ingredient_id,
            commercialProductId=commercial_product_id,
        )
        self.check_object_permissions(self.request, obj)
        return obj


# Company views
class CompanyView(generics.ListCreateAPIView):
    queryset = Company.objects.all().using("mysknv")
    serializer_class = MySKNVCompanySerializer


class CompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all().using("mysknv")
    serializer_class = MySKNVCompanySerializer


# Concern views
class ConcernView(generics.ListCreateAPIView):
    queryset = Concern.objects.all().using("mysknv")
    serializer_class = MySKNVConcernSerializer


class ConcernDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Concern.objects.all().using("mysknv")
    serializer_class = MySKNVConcernSerializer


# Conditions views
class ConditionsView(generics.ListCreateAPIView):
    queryset = Conditions.objects.all().using("mysknv")
    serializer_class = MySKNVConditionsSerializer


class ConditionsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Conditions.objects.all().using("mysknv")
    serializer_class = MySKNVConditionsSerializer


# Consentsignature views
class ConsentSignatureView(generics.ListCreateAPIView):
    queryset = Consentsignature.objects.all().using("mysknv")
    serializer_class = MySKNVConsentSignatureSerializer


class ConsentSignatureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Consentsignature.objects.all().using("mysknv")
    serializer_class = MySKNVConsentSignatureSerializer


# Correctorrequest views
class CorrectorRequestView(generics.ListCreateAPIView):
    queryset = Correctorrequest.objects.all().using("mysknv")
    serializer_class = MySKNVCorrectorRequestSerializer


class CorrectorRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Correctorrequest.objects.all().using("mysknv")
    serializer_class = MySKNVCorrectorRequestSerializer


# Cosmetic views
class CosmeticView(generics.ListCreateAPIView):
    queryset = Cosmetic.objects.all().using("mysknv")
    serializer_class = MySKNVCosmeticSerializer


class CosmeticDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cosmetic.objects.all().using("mysknv")
    serializer_class = MySKNVCosmeticSerializer


# Cosmeticleaflet views
class CosmeticLeafletView(generics.ListCreateAPIView):
    queryset = Cosmeticleaflet.objects.all().using("mysknv")
    serializer_class = MySKNVCosmeticLeafletSerializer


class CosmeticLeafletDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cosmeticleaflet.objects.all().using("mysknv")
    serializer_class = MySKNVCosmeticLeafletSerializer
    lookup_field = "baseCode"


# Dermacode views
class DermacodeView(generics.ListCreateAPIView):
    queryset = Dermacode.objects.all().using("mysknv")
    serializer_class = MySKNVDermacodeSerializer


class DermacodeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dermacode.objects.all().using("mysknv")
    serializer_class = MySKNVDermacodeSerializer


# Dermacodecosmetic views
class DermacodeCosmeticView(generics.ListCreateAPIView):
    queryset = Dermacodecosmetic.objects.all().using("mysknv")
    serializer_class = MySKNVDermacodeCosmeticSerializer


class DermacodeCosmeticDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dermacodecosmetic.objects.all().using("mysknv")
    serializer_class = MySKNVDermacodeCosmeticSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        dermacode_id = self.kwargs.get("dermacodeId")
        base_code = self.kwargs.get("baseCode")
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            dermacodeId=dermacode_id,
            baseCode=base_code,
        )
        self.check_object_permissions(self.request, obj)
        return obj


# Dermacodeprintout views
class DermacodeprintoutView(generics.ListCreateAPIView):
    queryset = Dermacodeprintout.objects.all().using("mysknv")
    serializer_class = MySKNVDermacodePrintoutSerializer


class DermacodeprintoutDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dermacodeprintout.objects.all().using("mysknv")
    serializer_class = MySKNVDermacodePrintoutSerializer


# Dispense views
class DispenseView(generics.ListCreateAPIView):
    queryset = Dispense.objects.all().using("mysknv")
    serializer_class = MySKNVDispenseSerializer


class DispenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dispense.objects.all().using("mysknv")
    serializer_class = MySKNVDispenseSerializer


# Dispenseitem views
class DispenseItemView(generics.ListCreateAPIView):
    queryset = Dispenseitem.objects.all().using("mysknv")
    serializer_class = MySKNVDispenseItemSerializer


class DispenseItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dispenseitem.objects.all().using("mysknv")
    serializer_class = MySKNVDispenseItemSerializer


# Dispenseitemdeletion views
class DispenseItemDeletionView(generics.ListCreateAPIView):
    queryset = Dispenseitemdeletion.objects.all().using("mysknv")
    serializer_class = MySKNVDispenseItemDeletionSerializer


class DispenseItemDeletionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dispenseitemdeletion.objects.all().using("mysknv")
    serializer_class = MySKNVDispenseItemDeletionSerializer


# Educatedperson views
class EducatedpersonView(generics.ListCreateAPIView):
    queryset = Educatedperson.objects.all().using("mysknv")
    serializer_class = MySKNVEducatedpersonSerializer


class EducatedpersonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Educatedperson.objects.all().using("mysknv")
    serializer_class = MySKNVEducatedpersonSerializer


# Educatedpersonsignature views
class EducatedPersonSignatureView(generics.ListCreateAPIView):
    queryset = Educatedpersonsignature.objects.all().using("mysknv")
    serializer_class = MySKNVEducatedPersonSignatureSerializer


class EducatedPersonSignatureDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Educatedpersonsignature.objects.all().using("mysknv")
    serializer_class = MySKNVEducatedPersonSignatureSerializer

    lookup_field = "educatedPersonId"


# Emaillist views
class EmailListView(generics.ListCreateAPIView):
    queryset = Emaillist.objects.all().using("mysknv")
    serializer_class = MySKNVEmailListSerializer


class EmailListDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Emaillist.objects.all().using("mysknv")
    serializer_class = MySKNVEmailListSerializer


# Employee views
class EmployeeView(generics.ListCreateAPIView):
    queryset = Employee.objects.all().using("mysknv")
    serializer_class = MySKNVEmployeeSerializer


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all().using("mysknv")
    serializer_class = MySKNVEmployeeSerializer


# Formula views
class FormulaView(generics.ListCreateAPIView):
    queryset = Formula.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaSerializer


class FormulaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Formula.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaSerializer


# Formulaingredient views
class FormulaIngredientView(generics.ListCreateAPIView):
    queryset = Formulaingredient.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaIngredientSerializer


class FormulaIngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Formulaingredient.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaIngredientSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        formula_code = self.kwargs.get("formulaCode")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, formulaCode=formula_code)
        self.check_object_permissions(self.request, obj)
        return obj


# Formulapreorder views
class FormulaPreorderView(generics.ListCreateAPIView):
    queryset = Formulapreorder.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaPreorderSerializer


class FormulaPreorderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Formulapreorder.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaPreorderSerializer


# Formularequest views
class FormulaRequestView(generics.ListCreateAPIView):
    queryset = Formularequest.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaRequestSerializer


class FormulaRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Formularequest.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaRequestSerializer


# Formularequestcomment views
class FormulaRequestCommentView(generics.ListCreateAPIView):
    queryset = Formularequestcomment.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaRequestCommentSerializer


class FormulaRequestCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Formularequestcomment.objects.all().using("mysknv")
    serializer_class = MySKNVFormulaRequestCommentSerializer


# Ingredient views
class IngredientView(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all().using("mysknv")
    serializer_class = MySKNVIngredientSerializer


class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredient.objects.all().using("mysknv")
    serializer_class = MySKNVIngredientSerializer


# Ingredientconcern views
class IngredientConcernView(generics.ListCreateAPIView):
    queryset = Ingredientconcern.objects.all().using("mysknv")
    serializer_class = MySKNVIngredientConcernSerializer


class IngredientConcernDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredientconcern.objects.all().using("mysknv")
    serializer_class = MySKNVIngredientConcernSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        ingredient_id = self.kwargs.get("ingredientId")
        concern_id = self.kwargs.get("concernId")
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset, ingredientId=ingredient_id, concernId=concern_id
        )
        self.check_object_permissions(self.request, obj)
        return obj


# Inventory views
class InventoryView(generics.ListCreateAPIView):
    queryset = Inventory.objects.all().using("mysknv")
    serializer_class = MySKNVInventorySerializer


class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.all().using("mysknv")
    serializer_class = MySKNVInventorySerializer


# Ipwhitelist views
class IpwhitelistView(generics.ListCreateAPIView):
    queryset = Ipwhitelist.objects.all().using("mysknv")
    serializer_class = MySKNVIpwhitelistSerializer


class IpwhitelistDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ipwhitelist.objects.all().using("mysknv")
    serializer_class = MySKNVIpwhitelistSerializer


# Issue views
class IssueView(generics.ListCreateAPIView):
    queryset = Issue.objects.all().using("mysknv")
    serializer_class = MySKNVIssueSerializer


class IssueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Issue.objects.all().using("mysknv")
    serializer_class = MySKNVIssueSerializer


# Leaflet views
class LeafletView(generics.ListCreateAPIView):
    queryset = Leaflet.objects.all().using("mysknv")
    serializer_class = MySKNVLeafletSerializer


class LeafletDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Leaflet.objects.all().using("mysknv")
    serializer_class = MySKNVLeafletSerializer


# LeafletIngredient views
class LeafletIngredientView(generics.ListCreateAPIView):
    queryset = LeafletIngredient.objects.all().using("mysknv")
    serializer_class = MySKNVLeafletIngredientSerializer


class LeafletIngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeafletIngredient.objects.all().using("mysknv")
    serializer_class = MySKNVLeafletIngredientSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        leaflet_id = self.kwargs.get("leafletId")
        ingredient_id = self.kwargs.get("ingredientId")
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset, leafletId=leaflet_id, ingredientId=ingredient_id
        )
        self.check_object_permissions(self.request, obj)
        return obj


# Legalinfo views
class LegalInfoView(generics.ListCreateAPIView):
    queryset = Legalinfo.objects.all().using("mysknv")
    serializer_class = MySKNVLegalInfoSerializer


class LegalInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Legalinfo.objects.all().using("mysknv")
    serializer_class = MySKNVLegalInfoSerializer


# Lotnumber views
class LotNumberView(generics.ListCreateAPIView):
    queryset = Lotnumber.objects.all().using("mysknv")
    serializer_class = MySKNVLotNumberSerializer


class LotNumberDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lotnumber.objects.all().using("mysknv")
    serializer_class = MySKNVLotNumberSerializer


# Medspasalesdio views
class MedSpaSalesDioView(generics.ListCreateAPIView):
    queryset = Medspasalesdio.objects.all().using("mysknv")
    serializer_class = MySKNVMedSpaSalesDioSerializer


class MedSpaSalesDioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medspasalesdio.objects.all().using("mysknv")
    serializer_class = MySKNVMedSpaSalesDioSerializer


# Medspasalesiou views
class MedSpaSalesIouView(generics.ListCreateAPIView):
    queryset = Medspasalesiou.objects.all().using("mysknv")
    serializer_class = MySKNVMedSpaSalesIouSerializer


class MedSpaSalesIouDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medspasalesiou.objects.all().using("mysknv")
    serializer_class = MySKNVMedSpaSalesIouSerializer


# Medicationassessment views
class MedicationAssessmentView(generics.ListCreateAPIView):
    queryset = Medicationassessment.objects.all().using("mysknv")
    serializer_class = MySKNVMedicationAssessmentSerializer


class MedicationAssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medicationassessment.objects.all().using("mysknv")
    serializer_class = MySKNVMedicationAssessmentSerializer


# Newpermission views
class NewPermissionView(generics.ListCreateAPIView):
    queryset = Newpermission.objects.all().using("mysknv")
    serializer_class = MySKNVNewPermissionSerializer


class NewPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Newpermission.objects.all().using("mysknv")
    serializer_class = MySKNVNewPermissionSerializer


# Newsalesresource views
class NewSalesResourceView(generics.ListCreateAPIView):
    queryset = Newsalesresource.objects.all().using("mysknv")
    serializer_class = MySKNVNewSalesResourceSerializer


class NewSalesResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Newsalesresource.objects.all().using("mysknv")
    serializer_class = MySKNVNewSalesResourceSerializer


# Nsendpoints views
class NsEndpointsView(generics.ListCreateAPIView):
    queryset = Nsendpoints.objects.all().using("mysknv")
    serializer_class = MySKNVNsEndpointsSerializer


class NsEndpointsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Nsendpoints.objects.all().using("mysknv")
    serializer_class = MySKNVNsEndpointsSerializer


# Nsorder views
class NsOrderView(generics.ListCreateAPIView):
    queryset = Nsorder.objects.all().using("mysknv")
    serializer_class = MySKNVNsOrderSerializer


class NsOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Nsorder.objects.all().using("mysknv")
    serializer_class = MySKNVNsOrderSerializer


# Nsorderitem views
class NsOrderItemView(generics.ListCreateAPIView):
    queryset = Nsorderitem.objects.all().using("mysknv")
    serializer_class = MySKNVNsOrderItemSerializer


class NsOrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Nsorderitem.objects.all().using("mysknv")
    serializer_class = MySKNVNsOrderItemSerializer


# Nsordertracking views
class NsOrderTrackingView(generics.ListCreateAPIView):
    queryset = Nsordertracking.objects.all().using("mysknv")
    serializer_class = MySKNVNsOrderTrackingSerializer


class NsOrderTrackingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Nsordertracking.objects.all().using("mysknv")
    serializer_class = MySKNVNsOrderTrackingSerializer


# Office views
class OfficeView(generics.ListCreateAPIView):
    queryset = Office.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeSerializer


class OfficeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Office.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeSerializer


# Officeipaduser views
class OfficeipaduserView(generics.ListCreateAPIView):
    queryset = Officeipaduser.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeIpaduserSerializer


class OfficeipaduserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officeipaduser.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeIpaduserSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        user_id = self.kwargs.get("userId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, userId=user_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Officepatient views
class OfficepatientView(generics.ListCreateAPIView):
    queryset = Officepatient.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePatientSerializer


class OfficepatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officepatient.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePatientSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        patient_id = self.kwargs.get("patientId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, patientId=patient_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Officepermission views
class OfficePermissionView(generics.ListCreateAPIView):
    queryset = Officepermission.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePermissionSerializer


class OfficePermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officepermission.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePermissionSerializer


# Officephysician views
class OfficephysicianView(generics.ListCreateAPIView):
    queryset = Officephysician.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianSerializer


class OfficephysicianDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officephysician.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        physician_id = self.kwargs.get("physicianId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, physicianId=physician_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Officephysicianexclusion views
class OfficephysicianexclusionView(generics.ListCreateAPIView):
    queryset = Officephysicianexclusion.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianExclusionSerializer


class OfficephysicianexclusionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officephysicianexclusion.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianExclusionSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        physician_id = self.kwargs.get("physicianId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, physicianId=physician_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Outgoingemail views
class OutgoingEmailView(generics.ListCreateAPIView):
    queryset = Outgoingemail.objects.all().using("mysknv")
    serializer_class = MySKNVOutgoingEmailSerializer


class OutgoingEmailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Outgoingemail.objects.all().using("mysknv")
    serializer_class = MySKNVOutgoingEmailSerializer


# Patient views
class PatientView(generics.ListCreateAPIView):
    queryset = Patient.objects.all().using("mysknv")
    serializer_class = MySKNVPatientSerializer


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all().using("mysknv")
    serializer_class = MySKNVPatientSerializer


# Patientphysician views
class PatientPhysicianView(generics.ListCreateAPIView):
    queryset = Patientphysician.objects.all().using("mysknv")
    serializer_class = MySKNVPatientPhysicianSerializer


class PatientPhysicianDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patientphysician.objects.all().using("mysknv")
    serializer_class = MySKNVPatientPhysicianSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        patient_id = self.kwargs.get("patientId")
        physician_id = self.kwargs.get("physicianId")
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset, patientId=patient_id, physicianId=physician_id
        )
        self.check_object_permissions(self.request, obj)
        return obj


# Pcdcontract views
class PcdContractView(generics.ListCreateAPIView):
    queryset = Pcdcontract.objects.all().using("mysknv")
    serializer_class = MySKNVPcdContractSerializer


class PcdContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pcdcontract.objects.all().using("mysknv")
    serializer_class = MySKNVPcdContractSerializer


# PcinvPcinventoryItems views
class PcinvPcinventoryItemsView(generics.ListCreateAPIView):
    queryset = PcinvPcinventoryItems.objects.all().using("mysknv")
    serializer_class = MySKNVPcinvPcinventoryItemsSerializer


class PcinvPcinventoryItemsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PcinvPcinventoryItems.objects.all().using("mysknv")
    serializer_class = MySKNVPcinvPcinventoryItemsSerializer


# Permission views
class PermissionView(generics.ListCreateAPIView):
    queryset = Permission.objects.all().using("mysknv")
    serializer_class = MySKNVPermissionSerializer


class PermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Permission.objects.all().using("mysknv")
    serializer_class = MySKNVPermissionSerializer


# Phinxlog views
class PhinxlogView(generics.ListCreateAPIView):
    queryset = Phinxlog.objects.all().using("mysknv")
    serializer_class = MySKNVPhinxlogSerializer


class PhinxlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Phinxlog.objects.all().using("mysknv")
    serializer_class = MySKNVPhinxlogSerializer
    lookup_field = "version"


# Physician views
class PhysicianView(generics.ListCreateAPIView):
    queryset = Physician.objects.all().using("mysknv")
    serializer_class = MySKNVPhysicianSerializer


class PhysicianDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Physician.objects.all().using("mysknv")
    serializer_class = MySKNVPhysicianSerializer


# Quote views
class QuoteView(generics.ListCreateAPIView):
    queryset = Quote.objects.all().using("mysknv")
    serializer_class = MySKNVQuoteSerializer


class QuoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quote.objects.all().using("mysknv")
    serializer_class = MySKNVQuoteSerializer


# Refillreminder views
class RefillReminderView(generics.ListCreateAPIView):
    queryset = Refillreminder.objects.all().using("mysknv")
    serializer_class = MySKNVRefillReminderSerializer


class RefillReminderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Refillreminder.objects.all().using("mysknv")
    serializer_class = MySKNVRefillReminderSerializer


# Refundrequest views
class RefundRequestView(generics.ListCreateAPIView):
    queryset = Refundrequest.objects.all().using("mysknv")
    serializer_class = MySKNVRefundRequestSerializer


class RefundRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Refundrequest.objects.all().using("mysknv")
    serializer_class = MySKNVRefundRequestSerializer


# Replacementmachinerequest views
class ReplacementMachineRequestView(generics.ListCreateAPIView):
    queryset = Replacementmachinerequest.objects.all().using("mysknv")
    serializer_class = MySKNVReplacementMachineRequestSerializer


class ReplacementMachineRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Replacementmachinerequest.objects.all().using("mysknv")
    serializer_class = MySKNVReplacementMachineRequestSerializer


# Role views
class RoleView(generics.ListCreateAPIView):
    queryset = Role.objects.all().using("mysknv")
    serializer_class = MySKNVRoleSerializer


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all().using("mysknv")
    serializer_class = MySKNVRoleSerializer


# RolePermission views
class RolePermissionView(generics.ListCreateAPIView):
    queryset = RolePermission.objects.all().using("mysknv")
    serializer_class = MySKNVRolePermissionSerializer


class RolePermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RolePermission.objects.all().using("mysknv")
    serializer_class = MySKNVRolePermissionSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        role_id = self.kwargs.get("roleId")
        permission_id = self.kwargs.get("permissionId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, roleId=role_id, permissionId=permission_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Rxbestmedspa views
class RxBestMedSpaView(generics.ListCreateAPIView):
    queryset = Rxbestmedspa.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestMedSpaSerializer


class RxBestMedSpaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxbestmedspa.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestMedSpaSerializer


# Rxbestnumbingdio views
class RxBestNumbingDioView(generics.ListCreateAPIView):
    queryset = Rxbestnumbingdio.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestNumbingDioSerializer


class RxBestNumbingDioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxbestnumbingdio.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestNumbingDioSerializer


# Rxbestpodiatry views
class RxBestPodiatryView(generics.ListCreateAPIView):
    queryset = Rxbestpodiatry.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestPodiatrySerializer


class RxBestPodiatryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxbestpodiatry.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestPodiatrySerializer


# Rxbestseller views
class RxBestSellerView(generics.ListCreateAPIView):
    queryset = Rxbestseller.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestSellerSerializer


class RxBestSellerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxbestseller.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestSellerSerializer


# RxbestsellerCopy1 views
class RxBestSellerCopy1View(generics.ListCreateAPIView):
    queryset = RxbestsellerCopy1.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestSellerCopy1Serializer


class RxBestSellerCopy1DetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RxbestsellerCopy1.objects.all().using("mysknv")
    serializer_class = MySKNVRxBestSellerCopy1Serializer


# Rxblt views
class RxBltView(generics.ListCreateAPIView):
    queryset = Rxblt.objects.all().using("mysknv")
    serializer_class = MySKNVRxBltSerializer


class RxBltDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxblt.objects.all().using("mysknv")
    serializer_class = MySKNVRxBltSerializer


# Rxconsent views
class RxConsentView(generics.ListCreateAPIView):
    queryset = Rxconsent.objects.all().using("mysknv")
    serializer_class = MySKNVRxConsentSerializer


class RxConsentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rxconsent.objects.all().using("mysknv")
    serializer_class = MySKNVRxConsentSerializer


# Saascontract views
class SaasContractView(generics.ListCreateAPIView):
    queryset = Saascontract.objects.all().using("mysknv")
    serializer_class = MySKNVSaasContractSerializer


class SaasContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Saascontract.objects.all().using("mysknv")
    serializer_class = MySKNVSaasContractSerializer


# Salescontract views
class SalesContractView(generics.ListCreateAPIView):
    queryset = Salescontract.objects.all().using("mysknv")
    serializer_class = MySKNVSalesContractSerializer


class SalesContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Salescontract.objects.all().using("mysknv")
    serializer_class = MySKNVSalesContractSerializer


# Salesorder views
class SalesOrderView(generics.ListCreateAPIView):
    queryset = Salesorder.objects.all().using("mysknv")
    serializer_class = MySKNVSalesOrderSerializer


class SalesOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Salesorder.objects.all().using("mysknv")
    serializer_class = MySKNVSalesOrderSerializer


# Salesorderproduct views
class SalesOrderProductView(generics.ListCreateAPIView):
    queryset = Salesorderproduct.objects.all().using("mysknv")
    serializer_class = MySKNVSalesOrderProductSerializer


class SalesOrderProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Salesorderproduct.objects.all().using("mysknv")
    serializer_class = MySKNVSalesOrderProductSerializer


# Salesresource views
class SalesResourceView(generics.ListCreateAPIView):
    queryset = Salesresource.objects.all().using("mysknv")
    serializer_class = MySKNVSalesResourceSerializer


class SalesResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Salesresource.objects.all().using("mysknv")
    serializer_class = MySKNVSalesResourceSerializer


# Salesresourcecategory views
class SalesResourceCategoryView(generics.ListCreateAPIView):
    queryset = Salesresourcecategory.objects.all().using("mysknv")
    serializer_class = MySKNVSalesResourceCategorySerializer


class SalesResourceCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Salesresourcecategory.objects.all().using("mysknv")
    serializer_class = MySKNVSalesResourceCategorySerializer


# Shipment views
class ShipmentView(generics.ListCreateAPIView):
    queryset = Shipment.objects.all().using("mysknv")
    serializer_class = MySKNVShipmentSerializer


class ShipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shipment.objects.all().using("mysknv")
    serializer_class = MySKNVShipmentSerializer


# Skincarecorrector views
class SkincareCorrectorView(generics.ListCreateAPIView):
    queryset = Skincarecorrector.objects.all().using("mysknv")
    serializer_class = MySKNVSkincareCorrectorSerializer


class SkincareCorrectorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Skincarecorrector.objects.all().using("mysknv")
    serializer_class = MySKNVSkincareCorrectorSerializer


# Sknvcosmeticleaflet views
class SknvCosmeticLeafletView(generics.ListCreateAPIView):
    queryset = Sknvcosmeticleaflet.objects.all().using("mysknv")
    serializer_class = MySKNVSknvCosmeticLeafletSerializer


class SknvCosmeticLeafletDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sknvcosmeticleaflet.objects.all().using("mysknv")
    serializer_class = MySKNVSknvCosmeticLeafletSerializer


# Sknvrxleaflet views
class SknvRxLeafletView(generics.ListCreateAPIView):
    queryset = Sknvrxleaflet.objects.all().using("mysknv")
    serializer_class = MySKNVSknvRxLeafletSerializer


class SknvRxLeafletDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sknvrxleaflet.objects.all().using("mysknv")
    serializer_class = MySKNVSknvRxLeafletSerializer


# Smscontract views
class SmsContractView(generics.ListCreateAPIView):
    queryset = Smscontract.objects.all().using("mysknv")
    serializer_class = MySKNVSmsContractSerializer


class SmsContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Smscontract.objects.all().using("mysknv")
    serializer_class = MySKNVSmsContractSerializer


# Subelitecontract views
class SubEliteContractView(generics.ListCreateAPIView):
    queryset = Subelitecontract.objects.all().using("mysknv")
    serializer_class = MySKNVSubEliteContractSerializer


class SubEliteContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subelitecontract.objects.all().using("mysknv")
    serializer_class = MySKNVSubEliteContractSerializer


# Subelitepluscontract views
class SubElitePlusContractView(generics.ListCreateAPIView):
    queryset = Subelitepluscontract.objects.all().using("mysknv")
    serializer_class = MySKNVSubElitePlusContractSerializer


class SubElitePlusContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subelitepluscontract.objects.all().using("mysknv")
    serializer_class = MySKNVSubElitePlusContractSerializer


# Token views
class TokenView(generics.ListCreateAPIView):
    queryset = Token.objects.all().using("mysknv")
    serializer_class = MySKNVTokenSerializer


class TokenDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Token.objects.all().using("mysknv")
    serializer_class = MySKNVTokenSerializer


# Totaladl views
class TotalAdlView(generics.ListCreateAPIView):
    queryset = Totaladl.objects.all().using("mysknv")
    serializer_class = MySKNVTotalAdlSerializer


class TotalAdlDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Totaladl.objects.all().using("mysknv")
    serializer_class = MySKNVTotalAdlSerializer


# Tsacontract views
class TsaContractView(generics.ListCreateAPIView):
    queryset = Tsacontract.objects.all().using("mysknv")
    serializer_class = MySKNVTsaContractSerializer


class TsaContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tsacontract.objects.all().using("mysknv")
    serializer_class = MySKNVTsaContractSerializer


# Usercompany views
class UserCompanyView(generics.ListCreateAPIView):
    queryset = Usercompany.objects.all().using("mysknv")
    serializer_class = MySKNVUserCompanySerializer


class UserCompanyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usercompany.objects.all().using("mysknv")
    serializer_class = MySKNVUserCompanySerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        user_id = self.kwargs.get("userId")
        company_id = self.kwargs.get("companyId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, userId=user_id, companyId=company_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Userhierarchy views
class UserHierarchyView(generics.ListCreateAPIView):
    queryset = Userhierarchy.objects.all().using("mysknv")
    serializer_class = MySKNVUserHierarchySerializer


class UserHierarchyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Userhierarchy.objects.all().using("mysknv")
    serializer_class = MySKNVUserHierarchySerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        parent_id = self.kwargs.get("parentId")
        child_id = self.kwargs.get("childId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, parentId=parent_id, childId=child_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Usermeta views
class UserMetaView(generics.ListCreateAPIView):
    queryset = Usermeta.objects.all().using("mysknv")
    serializer_class = MySKNVUserMetaSerializer


class UserMetaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usermeta.objects.all().using("mysknv")
    serializer_class = MySKNVUserMetaSerializer

    lookup_field = "userId"


# Useroffice views
class UserofficeView(generics.ListCreateAPIView):
    queryset = Useroffice.objects.all().using("mysknv")
    serializer_class = MySKNVUserOfficeSerializer


class UserofficeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Useroffice.objects.all().using("mysknv")
    serializer_class = MySKNVUserOfficeSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        user_id = self.kwargs.get("userId")
        office_id = self.kwargs.get("officeId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, userId=user_id, officeId=office_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Users views
class UsersView(generics.ListCreateAPIView):
    queryset = Users.objects.all().using("mysknv")
    serializer_class = MySKNVUsersSerializer


class UsersDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Users.objects.all().using("mysknv")
    serializer_class = MySKNVUsersSerializer


# W9 views
class W9View(generics.ListCreateAPIView):
    queryset = W9.objects.all().using("mysknv")
    serializer_class = MySKNVW9Serializer


class W9DetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = W9.objects.all().using("mysknv")
    serializer_class = MySKNVW9Serializer
