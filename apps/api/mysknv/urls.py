from django.urls import path
from .views import (
    ActivitylogView,
    ActivitylogDetailView,
    AddressView,
    AddressDetailView,
    AutheventView,
    AutheventDetailView,
    BaseelementView,
    BaseelementDetailView,
    ClindiffView,
    ClindiffDetailView,
    ClindiffviewView,
    ClindiffviewDetailView,
    CoachingreportView,
    CoachingreportDetailView,
    CoachingreportinprogressView,
    CoachingreportinprogressDetailView,
    CoachingreportsignatureView,
    CoachingreportsignatureDetailView,
    CommercialMedicationView,
    CommercialMedicationDetailView,
    CommercialProductView,
    CommercialProductDetailView,
    CommercialProductIngredientView,
    CommercialProductIngredientDetailView,
    CompanyView,
    CompanyDetailView,
    ConcernView,
    ConcernDetailView,
    ConditionsView,
    ConditionsDetailView,
    ConsentSignatureView,
    ConsentSignatureDetailView,
    CorrectorRequestView,
    CorrectorRequestDetailView,
    CosmeticView,
    CosmeticDetailView,
    CosmeticLeafletView,
    CosmeticLeafletDetailView,
    DermacodeView,
    DermacodeDetailView,
    DermacodeCosmeticView,
    DermacodeCosmeticDetailView,
    DermacodeprintoutView,
    DermacodeprintoutDetailView,
    DispenseView,
    DispenseDetailView,
    DispenseItemView,
    DispenseItemDetailView,
    DispenseItemDeletionView,
    DispenseItemDeletionDetailView,
    EducatedpersonView,
    EducatedpersonDetailView,
    EducatedPersonSignatureView,
    EducatedPersonSignatureDetailView,
    EmailListView,
    EmailListDetailView,
    EmployeeView,
    EmployeeDetailView,
    FormulaView,
    FormulaDetailView,
    FormulaIngredientView,
    FormulaIngredientDetailView,
    FormulaPreorderView,
    FormulaPreorderDetailView,
    FormulaRequestView,
    FormulaRequestDetailView,
    FormulaRequestCommentView,
    FormulaRequestCommentDetailView,
    IngredientView,
    IngredientDetailView,
    IngredientConcernView,
    IngredientConcernDetailView,
    InventoryView,
    InventoryDetailView,
    IpwhitelistView,
    IpwhitelistDetailView,
    IssueView,
    IssueDetailView,
    LeafletView,
    LeafletDetailView,
    LeafletIngredientView,
    LeafletIngredientDetailView,
    LegalInfoView,
    LegalInfoDetailView,
    LotNumberView,
    LotNumberDetailView,
    MedSpaSalesDioView,
    MedSpaSalesDioDetailView,
    MedSpaSalesIouView,
    MedSpaSalesIouDetailView,
    MedicationAssessmentView,
    MedicationAssessmentDetailView,
    NewPermissionView,
    NewPermissionDetailView,
    NewSalesResourceView,
    NewSalesResourceDetailView,
    NsEndpointsView,
    NsEndpointsDetailView,
    NsOrderView,
    NsOrderDetailView,
    NsOrderItemView,
    NsOrderItemDetailView,
    NsOrderTrackingView,
    NsOrderTrackingDetailView,
    OfficeView,
    OfficeDetailView,
    OfficeipaduserView,
    OfficeipaduserDetailView,
    OfficepatientView,
    OfficepatientDetailView,
    OfficePermissionView,
    OfficePermissionDetailView,
    OfficephysicianView,
    OfficephysicianDetailView,
    OfficephysicianexclusionView,
    OfficephysicianexclusionDetailView,
    OutgoingEmailView,
    OutgoingEmailDetailView,
    PatientView,
    PatientDetailView,
    PatientPhysicianView,
    PatientPhysicianDetailView,
    PcdContractView,
    PcdContractDetailView,
    PcinvPcinventoryItemsView,
    PcinvPcinventoryItemsDetailView,
    PermissionView,
    PermissionDetailView,
    PhinxlogView,
    PhinxlogDetailView,
    PhysicianView,
    PhysicianDetailView,
    QuoteView,
    QuoteDetailView,
    RefillReminderView,
    RefillReminderDetailView,
    RefundRequestView,
    RefundRequestDetailView,
    ReplacementMachineRequestView,
    ReplacementMachineRequestDetailView,
    RoleView,
    RoleDetailView,
    RolePermissionView,
    RolePermissionDetailView,
    RxBestMedSpaView,
    RxBestMedSpaDetailView,
    RxBestNumbingDioView,
    RxBestNumbingDioDetailView,
    RxBestPodiatryView,
    RxBestPodiatryDetailView,
    RxBestSellerView,
    RxBestSellerDetailView,
    RxBestSellerCopy1View,
    RxBestSellerCopy1DetailView,
    RxBltView,
    RxBltDetailView,
    RxConsentView,
    RxConsentDetailView,
    SaasContractView,
    SaasContractDetailView,
    SalesContractView,
    SalesContractDetailView,
    SalesOrderView,
    SalesOrderDetailView,
    SalesOrderProductView,
    SalesOrderProductDetailView,
    SalesResourceView,
    SalesResourceDetailView,
    SalesResourceCategoryView,
    SalesResourceCategoryDetailView,
    ShipmentView,
    ShipmentDetailView,
    SkincareCorrectorView,
    SkincareCorrectorDetailView,
    SknvCosmeticLeafletView,
    SknvCosmeticLeafletDetailView,
    SknvRxLeafletView,
    SknvRxLeafletDetailView,
    SmsContractView,
    SmsContractDetailView,
    SubEliteContractView,
    SubEliteContractDetailView,
    SubElitePlusContractView,
    SubElitePlusContractDetailView,
    TokenView,
    TokenDetailView,
    TotalAdlView,
    TotalAdlDetailView,
    TsaContractView,
    TsaContractDetailView,
    UserCompanyView,
    UserCompanyDetailView,
    UserHierarchyView,
    UserHierarchyDetailView,
    UserMetaView,
    UserMetaDetailView,
    UserofficeView,
    UserofficeDetailView,
    UsersView,
    UsersDetailView,
    W9View,
    W9DetailView,
)

urlpatterns = [
    # Activitylog URLs
    path("activitylogs/", ActivitylogView.as_view(), name="activitylog_list"),
    path(
        "activitylogs/<int:pk>/",
        ActivitylogDetailView.as_view(),
        name="activitylog_detail",
    ),
    # Address URLs
    path("addresses/", AddressView.as_view(), name="address_list"),
    path("addresses/<int:pk>/", AddressDetailView.as_view(), name="address_detail"),
    # Authevent URLs
    path("authevents/", AutheventView.as_view(), name="authevent_list"),
    path(
        "authevents/<int:pk>/", AutheventDetailView.as_view(), name="authevent_detail"
    ),
    # Baseelement URLs
    path("baseelements/", BaseelementView.as_view(), name="baseelement_list"),
    path(
        "baseelements/<int:pk>/",
        BaseelementDetailView.as_view(),
        name="baseelement_detail",
    ),
    # Clindiff URLs
    path("clindiffs/", ClindiffView.as_view(), name="clindiff_list"),
    path(
        "clindiffs/<str:formulaCode>/",
        ClindiffDetailView.as_view(),
        name="clindiff_detail",
    ),
    # Clindiffview URLs
    path("clindiffviews/", ClindiffviewView.as_view(), name="clindiffview_list"),
    path(
        "clindiffviews/<int:pk>/",
        ClindiffviewDetailView.as_view(),
        name="clindiffview_detail",
    ),
    # Coachingreport URLs
    path("coachingreports/", CoachingreportView.as_view(), name="coachingreport_list"),
    path(
        "coachingreports/<int:pk>/",
        CoachingreportDetailView.as_view(),
        name="coachingreport_detail",
    ),
    # Coachingreportinprogress URLs
    path(
        "coachingreportsinprogress/",
        CoachingreportinprogressView.as_view(),
        name="coachingreportinprogress_list",
    ),
    path(
        "coachingreportsinprogress/<int:pk>/",
        CoachingreportinprogressDetailView.as_view(),
        name="coachingreportinprogress_detail",
    ),
    # Coachingreportsignature URLs
    path(
        "coachingreportsignatures/",
        CoachingreportsignatureView.as_view(),
        name="coachingreportsignature_list",
    ),
    path(
        "coachingreportsignatures/<int:pk>/",
        CoachingreportsignatureDetailView.as_view(),
        name="coachingreportsignature_detail",
    ),
    # CommercialMedication URLs
    path(
        "commercialmedications/",
        CommercialMedicationView.as_view(),
        name="commercialmedication_list",
    ),
    path(
        "commercialmedications/<int:pk>/",
        CommercialMedicationDetailView.as_view(),
        name="commercialmedication_detail",
    ),
    # CommercialProduct URLs
    path(
        "commercialproducts/",
        CommercialProductView.as_view(),
        name="commercialproduct_list",
    ),
    path(
        "commercialproducts/<int:pk>/",
        CommercialProductDetailView.as_view(),
        name="commercialproduct_detail",
    ),
    # CommercialProductIngredient URLs
    path(
        "commercialproductingredients/",
        CommercialProductIngredientView.as_view(),
        name="commercialproductingredient_list",
    ),
    path(
        "commercialproductingredients/<int:ingredientId>/<int:commercialProductId>/",
        CommercialProductIngredientDetailView.as_view(),
        name="commercialproductingredient_detail",
    ),
    # Company URLs
    path("companies/", CompanyView.as_view(), name="company_list"),
    path("companies/<int:pk>/", CompanyDetailView.as_view(), name="company_detail"),
    # Concern URLs
    path("concerns/", ConcernView.as_view(), name="concern_list"),
    path("concerns/<int:pk>/", ConcernDetailView.as_view(), name="concern_detail"),
    # Conditions URLs
    path("conditions/", ConditionsView.as_view(), name="conditions_list"),
    path(
        "conditions/<int:pk>/", ConditionsDetailView.as_view(), name="conditions_detail"
    ),
    # ConsentSignature URLs
    path(
        "consentsignatures/",
        ConsentSignatureView.as_view(),
        name="consentsignature_list",
    ),
    path(
        "consentsignatures/<int:pk>/",
        ConsentSignatureDetailView.as_view(),
        name="consentsignature_detail",
    ),
    # CorrectorRequest URLs
    path(
        "correctorrequests/",
        CorrectorRequestView.as_view(),
        name="correctorrequest_list",
    ),
    path(
        "correctorrequests/<int:pk>/",
        CorrectorRequestDetailView.as_view(),
        name="correctorrequest_detail",
    ),
    # Cosmetic URLs
    path("cosmetics/", CosmeticView.as_view(), name="cosmetic_list"),
    path("cosmetics/<int:pk>/", CosmeticDetailView.as_view(), name="cosmetic_detail"),
    # CosmeticLeaflet URLs
    path(
        "cosmeticleaflets/", CosmeticLeafletView.as_view(), name="cosmeticleaflet_list"
    ),
    path(
        "cosmeticleaflets/<str:baseCode>/",
        CosmeticLeafletDetailView.as_view(),
        name="cosmeticleaflet_detail",
    ),
    # Dermacode URLs
    path("dermacodes/", DermacodeView.as_view(), name="dermacode_list"),
    path(
        "dermacodes/<int:pk>/", DermacodeDetailView.as_view(), name="dermacode_detail"
    ),
    # DermacodeCosmetic URLs
    path(
        "dermacodecosmetics/",
        DermacodeCosmeticView.as_view(),
        name="dermacodecosmetic_list",
    ),
    path(
        "dermacodecosmetics/<int:dermacodeId>/<str:baseCode>/",
        DermacodeCosmeticDetailView.as_view(),
        name="dermacodecosmetic_detail",
    ),
    # Dermacodeprintout URLs
    path(
        "dermacodeprintouts/",
        DermacodeprintoutView.as_view(),
        name="dermacodeprintout_list",
    ),
    path(
        "dermacodeprintouts/<int:pk>/",
        DermacodeprintoutDetailView.as_view(),
        name="dermacodeprintout_detail",
    ),
    # Dispense URLs
    path("dispenses/", DispenseView.as_view(), name="dispense_list"),
    path("dispenses/<int:pk>/", DispenseDetailView.as_view(), name="dispense_detail"),
    # DispenseItem URLs
    path("dispenseitems/", DispenseItemView.as_view(), name="dispenseitem_list"),
    path(
        "dispenseitems/<int:pk>/",
        DispenseItemDetailView.as_view(),
        name="dispenseitem_detail",
    ),
    # DispenseItemDeletion URLs
    path(
        "dispenseitemdeletions/",
        DispenseItemDeletionView.as_view(),
        name="dispenseitemdeletion_list",
    ),
    path(
        "dispenseitemdeletions/<int:pk>/",
        DispenseItemDeletionDetailView.as_view(),
        name="dispenseitemdeletion_detail",
    ),
    # Educatedperson URLs
    path("educatedpersons/", EducatedpersonView.as_view(), name="educatedperson_list"),
    path(
        "educatedpersons/<int:pk>/",
        EducatedpersonDetailView.as_view(),
        name="educatedperson_detail",
    ),
    # EducatedPersonSignature URLs
    path(
        "educatedpersonsignatures/",
        EducatedPersonSignatureView.as_view(),
        name="educatedpersonsignature_list",
    ),
    path(
        "educatedpersonsignatures/<int:educatedPersonId>/",
        EducatedPersonSignatureDetailView.as_view(),
        name="educatedpersonsignature_detail",
    ),
    # EmailList URLs
    path("emaillists/", EmailListView.as_view(), name="emaillist_list"),
    path(
        "emaillists/<int:pk>/", EmailListDetailView.as_view(), name="emaillist_detail"
    ),
    # Employee URLs
    path("employees/", EmployeeView.as_view(), name="employee_list"),
    path("employees/<int:pk>/", EmployeeDetailView.as_view(), name="employee_detail"),
    # Formula URLs
    path("formulas/", FormulaView.as_view(), name="formula_list"),
    path("formulas/<int:pk>/", FormulaDetailView.as_view(), name="formula_detail"),
    # FormulaIngredient URLs
    path(
        "formulaingredients/",
        FormulaIngredientView.as_view(),
        name="formulaingredient_list",
    ),
    path(
        "formulaingredients/<str:formulaCode>/",
        FormulaIngredientDetailView.as_view(),
        name="formulaingredient_detail",
    ),
    # FormulaPreorder URLs
    path(
        "formulapreorders/", FormulaPreorderView.as_view(), name="formulapreorder_list"
    ),
    path(
        "formulapreorders/<int:pk>/",
        FormulaPreorderDetailView.as_view(),
        name="formulapreorder_detail",
    ),
    # FormulaRequest URLs
    path("formularequests/", FormulaRequestView.as_view(), name="formularequest_list"),
    path(
        "formularequests/<int:pk>/",
        FormulaRequestDetailView.as_view(),
        name="formularequest_detail",
    ),
    # FormulaRequestComment URLs
    path(
        "formularequestcomments/",
        FormulaRequestCommentView.as_view(),
        name="formularequestcomment_list",
    ),
    path(
        "formularequestcomments/<int:pk>/",
        FormulaRequestCommentDetailView.as_view(),
        name="formularequestcomment_detail",
    ),
    # Ingredient URLs
    path("ingredients/", IngredientView.as_view(), name="ingredient_list"),
    path(
        "ingredients/<int:pk>/",
        IngredientDetailView.as_view(),
        name="ingredient_detail",
    ),
    # IngredientConcern URLs
    path(
        "ingredientconcerns/",
        IngredientConcernView.as_view(),
        name="ingredientconcern_list",
    ),
    path(
        "ingredientconcerns/<int:ingredientId>/<int:concernId>/",
        IngredientConcernDetailView.as_view(),
        name="ingredientconcern_detail",
    ),
    # Inventory URLs
    path("inventories/", InventoryView.as_view(), name="inventory_list"),
    path(
        "inventories/<int:pk>/", InventoryDetailView.as_view(), name="inventory_detail"
    ),
    # Ipwhitelist URLs
    path("ipwhitelists/", IpwhitelistView.as_view(), name="ipwhitelist_list"),
    path(
        "ipwhitelists/<int:pk>/",
        IpwhitelistDetailView.as_view(),
        name="ipwhitelist_detail",
    ),
    # Issue URLs
    path("issues/", IssueView.as_view(), name="issue_list"),
    path("issues/<int:pk>/", IssueDetailView.as_view(), name="issue_detail"),
    # Leaflet URLs
    path("leaflets/", LeafletView.as_view(), name="leaflet_list"),
    path("leaflets/<int:pk>/", LeafletDetailView.as_view(), name="leaflet_detail"),
    # LeafletIngredient URLs
    path(
        "leafletingredients/",
        LeafletIngredientView.as_view(),
        name="leafletingredient_list",
    ),
    path(
        "leafletingredients/<int:leafletId>/<int:ingredientId>/",
        LeafletIngredientDetailView.as_view(),
        name="leafletingredient_detail",
    ),
    # LegalInfo URLs
    path("legalinfos/", LegalInfoView.as_view(), name="legalinfo_list"),
    path(
        "legalinfos/<int:pk>/", LegalInfoDetailView.as_view(), name="legalinfo_detail"
    ),
    # LotNumber URLs
    path("lotnumbers/", LotNumberView.as_view(), name="lotnumber_list"),
    path(
        "lotnumbers/<int:pk>/", LotNumberDetailView.as_view(), name="lotnumber_detail"
    ),
    # MedSpaSalesDio URLs
    path("medspasalesdios/", MedSpaSalesDioView.as_view(), name="medspasalesdio_list"),
    path(
        "medspasalesdios/<int:pk>/",
        MedSpaSalesDioDetailView.as_view(),
        name="medspasalesdio_detail",
    ),
    # MedSpaSalesIou URLs
    path("medspasalesious/", MedSpaSalesIouView.as_view(), name="medspasalesiou_list"),
    path(
        "medspasalesious/<int:pk>/",
        MedSpaSalesIouDetailView.as_view(),
        name="medspasalesiou_detail",
    ),
    # MedicationAssessment URLs
    path(
        "medicationassessments/",
        MedicationAssessmentView.as_view(),
        name="medicationassessment_list",
    ),
    path(
        "medicationassessments/<int:pk>/",
        MedicationAssessmentDetailView.as_view(),
        name="medicationassessment_detail",
    ),
    # NewPermission URLs
    path("newpermissions/", NewPermissionView.as_view(), name="newpermission_list"),
    path(
        "newpermissions/<int:pk>/",
        NewPermissionDetailView.as_view(),
        name="newpermission_detail",
    ),
    # NewSalesResource URLs
    path(
        "newsalesresources/",
        NewSalesResourceView.as_view(),
        name="newsalesresource_list",
    ),
    path(
        "newsalesresources/<int:pk>/",
        NewSalesResourceDetailView.as_view(),
        name="newsalesresource_detail",
    ),
    # NsEndpoints URLs
    path("nsendpoints/", NsEndpointsView.as_view(), name="nsendpoints_list"),
    path(
        "nsendpoints/<int:pk>/",
        NsEndpointsDetailView.as_view(),
        name="nsendpoints_detail",
    ),
    # NsOrder URLs
    path("nsorders/", NsOrderView.as_view(), name="nsorder_list"),
    path("nsorders/<int:pk>/", NsOrderDetailView.as_view(), name="nsorder_detail"),
    # NsOrderItem URLs
    path("nsorderitems/", NsOrderItemView.as_view(), name="nsorderitem_list"),
    path(
        "nsorderitems/<int:pk>/",
        NsOrderItemDetailView.as_view(),
        name="nsorderitem_detail",
    ),
    # NsOrderTracking URLs
    path(
        "nsordertrackings/", NsOrderTrackingView.as_view(), name="nsordertracking_list"
    ),
    path(
        "nsordertrackings/<int:pk>/",
        NsOrderTrackingDetailView.as_view(),
        name="nsordertracking_detail",
    ),
    # Office URLs
    path("offices/", OfficeView.as_view(), name="office_list"),
    path("offices/<int:pk>/", OfficeDetailView.as_view(), name="office_detail"),
    # Officeipaduser URLs
    path("officeipadusers/", OfficeipaduserView.as_view(), name="officeipaduser_list"),
    path(
        "officeipadusers/<int:officeId>/<int:userId>/",
        OfficeipaduserDetailView.as_view(),
        name="officeipaduser_detail",
    ),
    # Officepatient URLs
    path("officepatients/", OfficepatientView.as_view(), name="officepatient_list"),
    path(
        "officepatients/<int:officeId>/<int:patientId>/",
        OfficepatientDetailView.as_view(),
        name="officepatient_detail",
    ),
    # OfficePermission URLs
    path(
        "officepermissions/",
        OfficePermissionView.as_view(),
        name="officepermission_list",
    ),
    path(
        "officepermissions/<int:pk>/",
        OfficePermissionDetailView.as_view(),
        name="officepermission_detail",
    ),
    # Officephysician URLs
    path(
        "officephysicians/", OfficephysicianView.as_view(), name="officephysician_list"
    ),
    path(
        "officephysicians/<int:officeId>/<int:physicianId>/",
        OfficephysicianDetailView.as_view(),
        name="officephysician_detail",
    ),
    # Officephysicianexclusion URLs
    path(
        "officephysicianexclusions/",
        OfficephysicianexclusionView.as_view(),
        name="officephysicianexclusion_list",
    ),
    path(
        "officephysicianexclusions/<int:officeId>/<int:physicianId>/",
        OfficephysicianexclusionDetailView.as_view(),
        name="officephysicianexclusion_detail",
    ),
    # OutgoingEmail URLs
    path("outgoingemails/", OutgoingEmailView.as_view(), name="outgoingemail_list"),
    path(
        "outgoingemails/<int:pk>/",
        OutgoingEmailDetailView.as_view(),
        name="outgoingemail_detail",
    ),
    # Patient URLs
    path("patients/", PatientView.as_view(), name="patient_list"),
    path("patients/<int:pk>/", PatientDetailView.as_view(), name="patient_detail"),
    # PatientPhysician URLs
    path(
        "patientphysicians/",
        PatientPhysicianView.as_view(),
        name="patientphysician_list",
    ),
    path(
        "patientphysicians/<int:patientId>/<int:physicianId>/",
        PatientPhysicianDetailView.as_view(),
        name="patientphysician_detail",
    ),
    # PcdContract URLs
    path("pcdcontracts/", PcdContractView.as_view(), name="pcdcontract_list"),
    path(
        "pcdcontracts/<int:pk>/",
        PcdContractDetailView.as_view(),
        name="pcdcontract_detail",
    ),
    # PcinvPcinventoryItems URLs
    path(
        "pcinvpcinventoryitems/",
        PcinvPcinventoryItemsView.as_view(),
        name="pcinvpcinventoryitems_list",
    ),
    path(
        "pcinvpcinventoryitems/<int:pk>/",
        PcinvPcinventoryItemsDetailView.as_view(),
        name="pcinvpcinventoryitems_detail",
    ),
    # Permission URLs
    path("permissions/", PermissionView.as_view(), name="permission_list"),
    path(
        "permissions/<int:pk>/",
        PermissionDetailView.as_view(),
        name="permission_detail",
    ),
    # Phinxlog URLs
    path("phinxlogs/", PhinxlogView.as_view(), name="phinxlog_list"),
    path(
        "phinxlogs/<int:version>/", PhinxlogDetailView.as_view(), name="phinxlog_detail"
    ),
    # Physician URLs
    path("physicians/", PhysicianView.as_view(), name="physician_list"),
    path(
        "physicians/<int:pk>/", PhysicianDetailView.as_view(), name="physician_detail"
    ),
    # Quote URLs
    path("quotes/", QuoteView.as_view(), name="quote_list"),
    path("quotes/<int:pk>/", QuoteDetailView.as_view(), name="quote_detail"),
    # RefillReminder URLs
    path("refillreminders/", RefillReminderView.as_view(), name="refillreminder_list"),
    path(
        "refillreminders/<int:pk>/",
        RefillReminderDetailView.as_view(),
        name="refillreminder_detail",
    ),
    # RefundRequest URLs
    path("refundrequests/", RefundRequestView.as_view(), name="refundrequest_list"),
    path(
        "refundrequests/<int:pk>/",
        RefundRequestDetailView.as_view(),
        name="refundrequest_detail",
    ),
    # ReplacementMachineRequest URLs
    path(
        "replacementmachinerequests/",
        ReplacementMachineRequestView.as_view(),
        name="replacementmachinerequest_list",
    ),
    path(
        "replacementmachinerequests/<int:pk>/",
        ReplacementMachineRequestDetailView.as_view(),
        name="replacementmachinerequest_detail",
    ),
    # Role URLs
    path("roles/", RoleView.as_view(), name="role_list"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role_detail"),
    # RolePermission URLs
    path("rolepermissions/", RolePermissionView.as_view(), name="rolepermission_list"),
    path(
        "rolepermissions/<int:roleId>/<int:permissionId>/",
        RolePermissionDetailView.as_view(),
        name="rolepermission_detail",
    ),
    # RxBestMedSpa URLs
    path("rxbestmedspas/", RxBestMedSpaView.as_view(), name="rxbestmedspa_list"),
    path(
        "rxbestmedspas/<int:pk>/",
        RxBestMedSpaDetailView.as_view(),
        name="rxbestmedspa_detail",
    ),
    # RxBestNumbingDio URLs
    path(
        "rxbestnumbingdios/",
        RxBestNumbingDioView.as_view(),
        name="rxbestnumbingdio_list",
    ),
    path(
        "rxbestnumbingdios/<int:pk>/",
        RxBestNumbingDioDetailView.as_view(),
        name="rxbestnumbingdio_detail",
    ),
    # RxBestPodiatry URLs
    path("rxbestpodiatries/", RxBestPodiatryView.as_view(), name="rxbestpodiatry_list"),
    path(
        "rxbestpodiatries/<int:pk>/",
        RxBestPodiatryDetailView.as_view(),
        name="rxbestpodiatry_detail",
    ),
    # RxBestSeller URLs
    path("rxbestsellers/", RxBestSellerView.as_view(), name="rxbestseller_list"),
    path(
        "rxbestsellers/<int:pk>/",
        RxBestSellerDetailView.as_view(),
        name="rxbestseller_detail",
    ),
    # RxBestSellerCopy1 URLs
    path(
        "rxbestsellercopies1/",
        RxBestSellerCopy1View.as_view(),
        name="rxbestsellercopy1_list",
    ),
    path(
        "rxbestsellercopies1/<int:pk>/",
        RxBestSellerCopy1DetailView.as_view(),
        name="rxbestsellercopy1_detail",
    ),
    # RxBlt URLs
    path("rxblts/", RxBltView.as_view(), name="rxblt_list"),
    path("rxblts/<int:pk>/", RxBltDetailView.as_view(), name="rxblt_detail"),
    # RxConsent URLs
    path("rxconsents/", RxConsentView.as_view(), name="rxconsent_list"),
    path(
        "rxconsents/<int:pk>/", RxConsentDetailView.as_view(), name="rxconsent_detail"
    ),
    # SaasContract URLs
    path("saascontracts/", SaasContractView.as_view(), name="saascontract_list"),
    path(
        "saascontracts/<int:pk>/",
        SaasContractDetailView.as_view(),
        name="saascontract_detail",
    ),
    # SalesContract URLs
    path("salescontracts/", SalesContractView.as_view(), name="salescontract_list"),
    path(
        "salescontracts/<int:pk>/",
        SalesContractDetailView.as_view(),
        name="salescontract_detail",
    ),
    # SalesOrder URLs
    path("salesorders/", SalesOrderView.as_view(), name="salesorder_list"),
    path(
        "salesorders/<int:pk>/",
        SalesOrderDetailView.as_view(),
        name="salesorder_detail",
    ),
    # SalesOrderProduct URLs
    path(
        "salesorderproducts/",
        SalesOrderProductView.as_view(),
        name="salesorderproduct_list",
    ),
    path(
        "salesorderproducts/<int:pk>/",
        SalesOrderProductDetailView.as_view(),
        name="salesorderproduct_detail",
    ),
    # SalesResource URLs
    path("salesresources/", SalesResourceView.as_view(), name="salesresource_list"),
    path(
        "salesresources/<int:pk>/",
        SalesResourceDetailView.as_view(),
        name="salesresource_detail",
    ),
    # SalesResourceCategory URLs
    path(
        "salesresourcecategories/",
        SalesResourceCategoryView.as_view(),
        name="salesresourcecategory_list",
    ),
    path(
        "salesresourcecategories/<int:pk>/",
        SalesResourceCategoryDetailView.as_view(),
        name="salesresourcecategory_detail",
    ),
    # Shipment URLs
    path("shipments/", ShipmentView.as_view(), name="shipment_list"),
    path("shipments/<int:pk>/", ShipmentDetailView.as_view(), name="shipment_detail"),
    # SkincareCorrector URLs
    path(
        "skincarecorrectors/",
        SkincareCorrectorView.as_view(),
        name="skincarecorrector_list",
    ),
    path(
        "skincarecorrectors/<int:pk>/",
        SkincareCorrectorDetailView.as_view(),
        name="skincarecorrector_detail",
    ),
    # SknvCosmeticLeaflet URLs
    path(
        "sknvcosmeticleaflets/",
        SknvCosmeticLeafletView.as_view(),
        name="sknvcosmeticleaflet_list",
    ),
    path(
        "sknvcosmeticleaflets/<int:pk>/",
        SknvCosmeticLeafletDetailView.as_view(),
        name="sknvcosmeticleaflet_detail",
    ),
    # SknvRxLeaflet URLs
    path("sknvrxleaflets/", SknvRxLeafletView.as_view(), name="sknvrxleaflet_list"),
    path(
        "sknvrxleaflets/<int:pk>/",
        SknvRxLeafletDetailView.as_view(),
        name="sknvrxleaflet_detail",
    ),
    # SmsContract URLs
    path("smscontracts/", SmsContractView.as_view(), name="smscontract_list"),
    path(
        "smscontracts/<int:pk>/",
        SmsContractDetailView.as_view(),
        name="smscontract_detail",
    ),
    # SubEliteContract URLs
    path(
        "subelitecontracts/",
        SubEliteContractView.as_view(),
        name="subelitecontract_list",
    ),
    path(
        "subelitecontracts/<int:pk>/",
        SubEliteContractDetailView.as_view(),
        name="subelitecontract_detail",
    ),
    # SubElitePlusContract URLs
    path(
        "subelitepluscontracts/",
        SubElitePlusContractView.as_view(),
        name="subelitepluscontract_list",
    ),
    path(
        "subelitepluscontracts/<int:pk>/",
        SubElitePlusContractDetailView.as_view(),
        name="subelitepluscontract_detail",
    ),
    # Token URLs
    path("tokens/", TokenView.as_view(), name="token_list"),
    path("tokens/<int:pk>/", TokenDetailView.as_view(), name="token_detail"),
    # TotalAdl URLs
    path("totaladls/", TotalAdlView.as_view(), name="totaladl_list"),
    path("totaladls/<int:pk>/", TotalAdlDetailView.as_view(), name="totaladl_detail"),
    # TsaContract URLs
    path("tsacontracts/", TsaContractView.as_view(), name="tsacontract_list"),
    path(
        "tsacontracts/<int:pk>/",
        TsaContractDetailView.as_view(),
        name="tsacontract_detail",
    ),
    # UserCompany URLs
    path("usercompanies/", UserCompanyView.as_view(), name="usercompany_list"),
    path(
        "usercompanies/<int:userId>/<int:companyId>/",
        UserCompanyDetailView.as_view(),
        name="usercompany_detail",
    ),
    # UserHierarchy URLs
    path("userhierarchies/", UserHierarchyView.as_view(), name="userhierarchy_list"),
    path(
        "userhierarchies/<int:parentId>/<int:childId>/",
        UserHierarchyDetailView.as_view(),
        name="userhierarchy_detail",
    ),
    # UserMeta URLs
    path("usermetas/", UserMetaView.as_view(), name="usermeta_list"),
    path(
        "usermetas/<int:userId>/", UserMetaDetailView.as_view(), name="usermeta_detail"
    ),
    # Useroffice URLs
    path("useroffices/", UserofficeView.as_view(), name="useroffice_list"),
    path(
        "useroffices/<int:userId>/<int:officeId>/",
        UserofficeDetailView.as_view(),
        name="useroffice_detail",
    ),
    # Users URLs
    path("users/", UsersView.as_view(), name="users_list"),
    path("users/<int:pk>/", UsersDetailView.as_view(), name="users_detail"),
    # W9 URLs
    path("w9s/", W9View.as_view(), name="w9_list"),
    path("w9s/<int:pk>/", W9DetailView.as_view(), name="w9_detail"),
]
