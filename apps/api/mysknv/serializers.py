from rest_framework import serializers
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


class MySKNVActivitylogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activitylog
        fields = (
            "id",
            "userId",
            "officeId",
            "ipAddress",
            "message",
            "category",
            "isHipaa",
            "timeCreated",
        )


class MySKNVAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "street",
            "city",
            "state",
            "zip",
            "phone",
            "dateCreated",
            "dateUpdated",
        )


class MySKNVAutheventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authevent
        fields = (
            "id",
            "userId",
            "event_type",
            "ipaddress",
            "time_attempted",
        )


class MySKNVBaseelementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baseelement
        fields = (
            "id",
            "name",
            "location",
            "content",
        )


class MySKNVClindiffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clindiff
        fields = (
            "approved",
            "formulaCode",
            "content",
            "modified",
        )


class MySKNVClindiffviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clindiffview
        fields = (
            "approved",
            "formulaCode",
        )


class MySKNVCoachingreportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coachingreport
        fields = "__all__"


class MySKNVCoachingreportinprogressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coachingreportinprogress
        fields = "__all__"


class MySKNVCoachingreportsignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coachingreportsignature
        fields = (
            "id",
            "coachingReportId",
            "s3Url",
            "actions",
            "dateCreated",
        )


class MySKNVCommercialMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commercialmedication
        fields = (
            "id",
            "name",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVCommercialProductIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commercialproductingredient
        fields = (
            "ingredientId",
            "commercialProductId",
        )


class MySKNVCommercialProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commercialproduct
        fields = (
            "id",
            "name",
            "dateCreated",
            "dateModified",
        )


class MySKNVCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "name",
            "dateCreated",
        )


class MySKNVConcernSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concern
        fields = (
            "id",
            "description",
        )


class MySKNVConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conditions
        fields = (
            "id",
            "formulaCode",
            "condition",
        )


class MySKNVConsentSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consentsignature
        fields = (
            "id",
            "netsuiteId",
            "s3Url",
            "name",
            "title",
            "dateCreated",
            "licenseNum",
        )


class MySKNVCorrectorRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correctorrequest
        fields = "__all__"


class MySKNVCosmeticLeafletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cosmeticleaflet
        fields = "__all__"


class MySKNVCosmeticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cosmetic
        fields = (
            "id",
            "netsuiteId",
            "baseCode",
            "sku",
            "displayName",
            "containerSize",
            "unitPrice",
            "dateCreated",
            "dateModified",
            "unitsPerCase",
            "active",
        )


class MySKNVDermacodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dermacode
        fields = (
            "id",
            "code",
        )


class MySKNVDermacodeCosmeticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dermacodecosmetic
        fields = (
            "dermacodeId",
            "baseCode",
            "isOptional",
        )


class MySKNVDermacodePrintoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dermacodeprintout
        fields = (
            "id",
            "officeId",
            "userId",
            "dermacode",
            "s3Key",
            "dateCreated",
        )


class MySKNVDispenseItemDeletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispenseitemdeletion
        fields = (
            "id",
            "dispenseId",
            "dispenseItemId",
            "jsonData",
            "dateCreated",
        )


class MySKNVDispenseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispenseitem
        fields = (
            "id",
            "dispenseId",
            "inventoryId",
            "formulaName",
            "formulaIngredients",
            "price",
            "prescriptionSerialNumber",
            "instructions",
            "log",
        )


class MySKNVDispenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispense
        fields = (
            "id",
            "officeId",
            "patientId",
            "physicianId",
            "amount",
            "dermacode",
            "dateCreated",
        )


class MySKNVEducatedPersonSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educatedpersonsignature
        fields = (
            "educatedPersonId",
            "signature",
        )


class MySKNVEducatedpersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Educatedperson
        fields = (
            "id",
            "employeeId",
            "officeId",
            "name",
            "nameHash",
            "convertedToPatient",
            "interested",
            "s3Url",
            "dateCreated",
        )


class MySKNVEmailListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emaillist
        fields = "__all__"


class MySKNVEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = (
            "id",
            "officeId",
            "name",
            "email",
            "streetAddress",
            "city",
            "state",
            "zip",
            "ssn",
            "ssnIdx",
            "agreementS3Key",
            "w9S3Key",
            "active",
            "isTest",
            "dateCreated",
        )


class MySKNVFormulaIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formulaingredient
        fields = (
            "formulaCode",
            "ingredientId",
            "active",
        )


class MySKNVFormulaPreorderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formulapreorder
        fields = (
            "id",
            "formulaRequestId",
            "userId",
            "officeName",
            "qty",
            "dateCreated",
        )


class MySKNVFormulaRequestCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formularequestcomment
        fields = (
            "id",
            "formulaRequestId",
            "userId",
            "message",
            "dateCreated",
        )


class MySKNVFormulaRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formularequest
        fields = "__all__"


class MySKNVFormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formula
        fields = "__all__"


class MySKNVIngredientConcernSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredientconcern
        fields = (
            "ingredientId",
            "concernId",
        )


class MySKNVIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "description",
            "commercialInactive",
        )


class MySKNVInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = (
            "id",
            "officeId",
            "formulaCode",
            "cosmeticId",
            "amount",
            "price",
            "internalName",
            "instructions",
            "reorderTrigger",
            "reorderNotification",
            "disabled",
            "type",
            "useAlternateLogo",
            "dateUpdated",
        )


class MySKNVIpwhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ipwhitelist
        fields = (
            "id",
            "officeId",
            "cidr",
            "dateCreated",
            "dateModified",
        )


class MySKNVIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "id",
            "userId",
            "username",
            "description",
            "attachments",
            "referrer",
            "useragent",
            "dateCreated",
        )


class MySKNVLeafletIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeafletIngredient
        fields = (
            "leafletId",
            "ingredientId",
            "position",
        )


class MySKNVLeafletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaflet
        fields = "__all__"


class MySKNVLegalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legalinfo
        fields = (
            "id",
            "netsuiteId",
            "physicianGroup",
            "physicianName",
            "physicianEmail",
            "state",
            "dateCreated",
            "dateModified",
        )


class MySKNVLotNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lotnumber
        fields = (
            "id",
            "netsuiteId",
            "formulaCode",
            "lotNumber",
            "qty",
            "hidden",
            "dateAdded",
            "dateCreated",
            "dateModified",
        )


class MySKNVMedicationAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicationassessment
        fields = (
            "id",
            "commercialMedId",
            "formulaCode",
            "notes",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVMedSpaSalesDioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medspasalesdio
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVMedSpaSalesIouSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medspasalesiou
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVNewPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newpermission
        fields = (
            "id",
            "roleId",
            "resource",
            "handler",
            "active",
            "dateCreated",
        )


class MySKNVNewSalesResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsalesresource
        fields = "__all__"


class MySKNVNsEndpointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nsendpoints
        fields = "__all__"


class MySKNVNsOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nsorderitem
        fields = (
            "id",
            "nsOrderId",
            "sku",
            "price",
            "casePrice",
            "unitPrice",
            "cases",
            "units",
            "type",
        )


class MySKNVNsOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nsorder
        fields = (
            "id",
            "customerNsId",
            "transactionId",
            "customerName",
            "trackingNumbers",
            "status",
            "amount",
            "dateCreated",
            "dateModified",
        )


class MySKNVNsOrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nsordertracking
        fields = (
            "id",
            "nsOrderId",
            "tracking",
            "proofOfDeliveryUrl",
        )


class MySKNVOfficeIpaduserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officeipaduser
        fields = (
            "officeId",
            "userId",
        )


class MySKNVOfficePatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officepatient
        fields = (
            "officeId",
            "patientId",
        )


class MySKNVOfficePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officepermission
        fields = (
            "id",
            "roleId",
            "resource",
            "handler",
            "active",
            "dateCreated",
        )


class MySKNVOfficePhysicianExclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officephysicianexclusion
        fields = (
            "officeId",
            "physicianId",
        )


class MySKNVOfficePhysicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officephysician
        fields = (
            "officeId",
            "physicianId",
            "status",
        )


class MySKNVOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = (
            "id",
            "companyId",
            "netsuiteId",
            "email",
            "name",
            "streetAddress",
            "city",
            "state",
            "zip",
            "phone",
            "logo",
            "status",
            "allowCustomInventory",
            "allowMoveInventory",
            "originalLogo",
            "logoCosmetic",
            "logoCosmeticAlt",
            "enableIpad",
            "cosmetics",
            "lastRxNumber",
            "leafletHeaderTemplate",
            "tier",
            "expectedPatients",
            "dateCreated",
            "dateModified",
            "adlOptOut",
        )


class MySKNVOutgoingEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outgoingemail
        fields = (
            "id",
            "emailListId",
            "name",
            "subject",
            "recipients",
            "dateCreated",
            "dateModified",
        )


class MySKNVPatientPhysicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patientphysician
        fields = (
            "patientId",
            "physicianId",
        )


class MySKNVPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class MySKNVPcdContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pcdcontract
        fields = "__all__"


class MySKNVPcinvPcinventoryItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PcinvPcinventoryItems
        fields = (
            "id",
            "item_id",
            "item_name",
            "item_formula",
            "item_price",
            "item_suggested",
            "last_mod",
            "items_in_case",
        )


class MySKNVPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            "id",
            "name",
            "isRoute",
            "scope",
        )


class MySKNVPhinxlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phinxlog
        fields = (
            "version",
            "migration_name",
            "start_time",
            "end_time",
            "breakpoint",
        )


class MySKNVPhysicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Physician
        fields = (
            "id",
            "userId",
            "name",
            "email",
            "streetAddress",
            "city",
            "state",
            "zip",
            "phone",
            "dateCreated",
            "dateUpdated",
        )


class MySKNVQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = (
            "id",
            "payload",
        )


class MySKNVRefillReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refillreminder
        fields = (
            "id",
            "dispenseId",
            "reminderDate",
            "sent",
            "interval",
            "dateSent",
            "dateCreated",
        )


class MySKNVRefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refundrequest
        fields = "__all__"


class MySKNVReplacementMachineRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Replacementmachinerequest
        fields = "__all__"


class MySKNVRolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = (
            "roleId",
            "permissionId",
        )


class MySKNVRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = (
            "id",
            "title",
        )


class MySKNVRxBestMedSpaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxbestmedspa
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVRxBestNumbingDioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxbestnumbingdio
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVRxBestPodiatrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxbestpodiatry
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVRxBestSellerCopy1Serializer(serializers.ModelSerializer):
    class Meta:
        model = RxbestsellerCopy1
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVRxBestSellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxbestseller
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVRxBltSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxblt
        fields = (
            "id",
            "formulaCode",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVRxConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxconsent
        fields = (
            "id",
            "salesOrderId",
            "legalInfoId",
            "consentSignatureId",
            "netsuiteId",
            "formulaCode",
            "dateCreated",
        )


class MySKNVSaasContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saascontract
        fields = "__all__"


class MySKNVSalesContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salescontract
        fields = "__all__"


class MySKNVSalesOrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salesorderproduct
        fields = "__all__"


class MySKNVSalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salesorder
        fields = "__all__"


class MySKNVSalesResourceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salesresourcecategory
        fields = (
            "id",
            "name",
            "active",
            "dateCreated",
            "dateModified",
        )


class MySKNVSalesResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salesresource
        fields = (
            "id",
            "category",
            "title",
            "summary",
            "url",
            "s3Url",
            "comments",
            "dateCreated",
            "dateModified",
        )


class MySKNVShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = (
            "id",
            "netsuiteId",
            "companyId",
            "officeId",
            "formulaCode",
            "sku",
            "netsuiteName",
            "companyName",
            "formulaName",
            "productFullName",
            "productBaseQuantity",
            "caseQuantity",
            "productUnitsFulfilled",
            "fulfillmentDate",
            "shippingAddress",
            "shippingZip",
            "physicianOnOrder",
            "isLoaded",
            "lotNumber",
            "dateCreated",
            "nsShipmentId",
            "nsItemId",
        )


class MySKNVSkincareCorrectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skincarecorrector
        fields = "__all__"


class MySKNVSknvCosmeticLeafletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sknvcosmeticleaflet
        fields = "__all__"


class MySKNVSknvRxLeafletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sknvrxleaflet
        fields = "__all__"


class MySKNVSmsContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Smscontract
        fields = "__all__"


class MySKNVSubEliteContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subelitecontract
        fields = "__all__"


class MySKNVSubElitePlusContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subelitepluscontract
        fields = "__all__"


class MySKNVTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = (
            "id",
            "userId",
            "token",
            "token_type",
            "time_created",
        )


class MySKNVTotalAdlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Totaladl
        fields = (
            "id",
            "office_id",
            "num_dispenses",
        )


class MySKNVTsaContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tsacontract
        fields = "__all__"


class MySKNVUserCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Usercompany
        fields = (
            "userId",
            "companyId",
        )


class MySKNVUserHierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = Userhierarchy
        fields = (
            "parentId",
            "childId",
            "dateCreated",
        )


class MySKNVUserMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usermeta
        fields = (
            "userId",
            "name",
            "email",
            "reminderOptOut",
        )


class MySKNVUserOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Useroffice
        fields = (
            "userId",
            "officeId",
            "isPrimary",
            "roleId",
        )


class MySKNVUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = (
            "id",
            "roleId",
            "email",
            "emailHash",
            "pass_field",
            "name",
            "status",
            "dateCreated",
            "dateModified",
        )


class MySKNVW9Serializer(serializers.ModelSerializer):
    class Meta:
        model = W9
        fields = "__all__"
