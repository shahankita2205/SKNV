from django.utils import timezone
from django.conf import settings
from rest_framework import serializers
from fred.models import (
    Address2,
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


class FredAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address2
        fields = "__all__"


class FredAllergensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergens
        fields = "__all__"


class FredAuditTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditTable
        fields = "__all__"


class FredAutomatedtasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automatedtasks
        fields = "__all__"


class FredDeletedofficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deletedoffice
        fields = "__all__"


class FredDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"


class FredDispenselogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispenselogs
        fields = "__all__"


class FredFeatureflagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Featureflag
        fields = "__all__"


class FredFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fee
        fields = "__all__"


class FredFulfillmentpartnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fulfillmentpartners
        fields = "__all__"


class FredIhflogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ihflogs
        fields = "__all__"


class FredIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class FredInhouseeligibilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inhouseeligibility
        fields = "__all__"


class FredInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"


class FredLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = "__all__"


class FredLogspatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logspatient
        fields = "__all__"


class FredLogsrxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logsrx
        fields = "__all__"


class FredLotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lots
        fields = "__all__"


class FredMedalignmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medalignments
        fields = "__all__"


class FredMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = "__all__"


class FredMedleafletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medleaflet
        fields = "__all__"


class FredOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = "__all__"


class FredOfficeagreementtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officeagreementtype
        fields = "__all__"


class FredOfficehistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Officehistory
        fields = "__all__"


class FredOfficeinfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officeinfo
        fields = "__all__"


class FredOfficetypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Officetype
        fields = "__all__"


class FredOthermedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Othermedication
        fields = "__all__"


class FredOutofstockmedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outofstockmedication
        fields = "__all__"


class FredPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class FredPatientlogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patientlogs
        fields = "__all__"


class FredPatientmetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patientmeta
        fields = "__all__"


class FredPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class FredPaymentsnotapprovedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paymentsnotapproved
        fields = "__all__"


class FredPcdAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PcdAgreement
        fields = "__all__"


class FredPcdFormularyAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PcdFormularyAgreement
        fields = "__all__"


class FredPcdInboundNdcSerializer(serializers.ModelSerializer):
    class Meta:
        model = PcdInboundNdc
        fields = "__all__"


class FredPcdNormalizedDrugGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PcdNormalizedDrugGroup
        fields = "__all__"


class FredPrepaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prepaid
        fields = "__all__"


class FredRxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rx
        fields = "__all__"


class FredRxfillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxfill
        fields = "__all__"


class FredRxprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxprint
        fields = "__all__"


class FredRxrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rxraw
        fields = "__all__"


class FredShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = "__all__"


class FredSkincarepairingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skincarepairings
        fields = "__all__"


class FredStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"


class FredSubstatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substatus
        fields = "__all__"


class FredTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class FredTextsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Textsent
        fields = "__all__"


class FredTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = "__all__"


class FredUpdatedskusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Updatedskus
        fields = "__all__"


class FredUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"


class FredUserstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Userstate
        fields = "__all__"


class FredDioItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DioItems
        fields = "__all__"


class DioItemsSkuSerializer(serializers.Serializer):
    """Serializer for dio items SKU data with netsuiteid filter"""

    sku = serializers.CharField(max_length=255, allow_null=True)
    active = serializers.BooleanField()


class PaymentCreateSerializer(serializers.Serializer):
    """
    Serializer for creating payment records
    Matches the createFredPayment function parameters
    """

    patientid = serializers.IntegerField()
    officeid = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    txid = serializers.CharField(max_length=255)
    sqrcid = serializers.CharField(max_length=255, required=False, allow_blank=True)
    type = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=255)
    paymentProvider = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    shippingcost = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    couponDiscountMap = serializers.JSONField(required=False, allow_null=True)
    qty = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )

    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value < 0:
            raise serializers.ValidationError("Amount must be positive")
        return value

    def validate_discount(self, value):
        """Validate discount if provided"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Discount cannot be negative")
        return value

    def validate_shippingcost(self, value):
        """Validate shipping cost if provided"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Shipping cost cannot be negative")
        return value

    def create(self, validated_data):
        """
        Create payment record with validated data
        """
        # Extract paymentProvider and set default if not provided
        payment_provider = validated_data.pop("paymentProvider", None)
        coupon_discount_map = validated_data.pop("couponDiscountMap", None)

        # Set default payment provider if not specified
        if not payment_provider:
            payment_provider = getattr(settings, "DEFAULT_PAYMENT_PROVIDER", "stripe")

        # Create payment data
        payment_data = {
            "patientid": validated_data["patientid"],
            "officeid": validated_data["officeid"],
            "amount": str(validated_data["amount"]),  # Convert to string as per model
            "txid": validated_data["txid"],
            "sqrcid": validated_data.get("sqrcid", ""),
            "type": validated_data["type"],
            "status": validated_data["status"],
            "provider": payment_provider,
            "discount": validated_data.get("discount"),
            "shippingcost": validated_data.get("shippingcost"),
            "discountdetails": coupon_discount_map,
            "qty": validated_data.get("qty"),
            "created": timezone.now(),
        }

        # Create and save payment record
        payment = Payment.objects.using("fred").create(**payment_data)
        return payment


class PaymentResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for payment response data
    """

    class Meta:
        model = Payment
        fields = [
            "id",
            "patientid",
            "officeid",
            "amount",
            "txid",
            "sqrcid",
            "type",
            "status",
            "provider",
            "discount",
            "shippingcost",
            "discountdetails",
            "qty",
            "created",
        ]


class PaymentTransactionSerializer(serializers.Serializer):
    """
    Serializer that matches the exact structure of your createFredPayment function parameter
    """

    patientid = serializers.IntegerField()
    officeid = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    txid = serializers.CharField(max_length=255)
    sqrcid = serializers.CharField(max_length=255, required=False, allow_blank=True)
    type = serializers.CharField(max_length=255)
    status = serializers.CharField(max_length=255)
    paymentProvider = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    discount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True, default=0
    )
    shippingcost = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    couponDiscountMap = serializers.JSONField(required=False, allow_null=True)
    qty = serializers.CharField(
        max_length=255, required=False, allow_blank=True, allow_null=True
    )


class CyberSourceTransactionRequestSerializer(serializers.Serializer):
    """
    Serializer for CyberSource transaction lookup request
    """

    transaction_id = serializers.CharField(
        max_length=255, required=True, allow_blank=False
    )

    def validate_transaction_id(self, value):
        """Validate transaction ID is not empty after stripping whitespace"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Transaction ID cannot be empty")
        return value


class CyberSourceCustomerResponseSerializer(serializers.Serializer):
    """
    Serializer for CyberSource customer ID response
    """

    transaction_id = serializers.CharField(max_length=255)
    customer_id = serializers.CharField(max_length=255, allow_null=True, required=False)
    success = serializers.BooleanField()
    message = serializers.CharField(max_length=500, required=False)


class PaymentMatchSerializer(serializers.Serializer):
    """
    Serializer for matching payment to RxFill
    """

    payment_id = serializers.IntegerField()
    rxfill_id = serializers.IntegerField()
    medication_id = serializers.CharField(
        max_length=255, required=False, allow_null=True
    )
    qty = serializers.IntegerField(required=False, default=1)

    def validate_payment_id(self, value):
        if value < 1:
            raise serializers.ValidationError("payment_id must be positive")
        return value

    def validate_rxfill_id(self, value):
        if value < 1:
            raise serializers.ValidationError("rxfill_id must be positive")
        return value

    def validate_qty(self, value):
        if value not in [1, 2, 3]:
            raise serializers.ValidationError("qty must be 1, 2, or 3")
        return value


class RefillsNoPaymentSerializer(serializers.Serializer):
    """Serializer for refills with no payment data"""

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=255, allow_null=True)
    dob = serializers.CharField(max_length=255, allow_null=True)
    phone = serializers.CharField(max_length=255, allow_null=True)
    email = serializers.CharField(max_length=255, allow_null=True)
    city = serializers.CharField(max_length=255, allow_null=True)
    state = serializers.CharField(max_length=255, allow_null=True)
    rxId = serializers.IntegerField()
    created = serializers.DateTimeField(allow_null=True)
    officeId = serializers.IntegerField()
    officeName = serializers.CharField(max_length=255, allow_null=True)
    indication = serializers.CharField(max_length=255, allow_null=True)
    fillId = serializers.IntegerField()
    fillStatus = serializers.CharField(max_length=255, allow_null=True)
    virx = serializers.BooleanField(allow_null=True)
    callOutcome = serializers.CharField(max_length=255, allow_null=True)
    outreachAttempt = serializers.IntegerField(allow_null=True)
    callSummary = serializers.CharField(allow_null=True, required=False)
    callBack = serializers.CharField(max_length=255, allow_null=True)
    tasked = serializers.BooleanField(required=False)

    formattedPhone = serializers.CharField(
        max_length=255, allow_null=True, required=False
    )
    formattedDob = serializers.CharField(
        max_length=255, allow_null=True, required=False
    )
    formattedCreated = serializers.CharField(
        max_length=255, allow_null=True, required=False
    )
    sortableCreated = serializers.CharField(
        max_length=255, allow_null=True, required=False
    )
    formattedLocation = serializers.CharField(
        max_length=255, allow_null=True, required=False
    )
    fillNumber = serializers.IntegerField(allow_null=True, required=False)
    fillType = serializers.CharField(max_length=10, allow_null=True, required=False)


class RefillsNoPaymentPaginationSerializer(serializers.Serializer):
    """Serializer for pagination metadata"""

    current_page = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_records = serializers.IntegerField()
    per_page = serializers.IntegerField()
    has_more = serializers.BooleanField()


class RefillsNoPaymentFiltersSerializer(serializers.Serializer):
    """Serializer for filter metadata"""

    days = serializers.IntegerField()
    date_from = serializers.CharField(max_length=255)


class RefillsNoPaymentResponseSerializer(serializers.Serializer):
    """Serializer for the complete response"""

    data = RefillsNoPaymentSerializer(many=True)
    pagination = RefillsNoPaymentPaginationSerializer()
    filters = RefillsNoPaymentFiltersSerializer()


class RefillsNoPaymentQuerySerializer(serializers.Serializer):
    """Serializer for validating query parameters"""

    days = serializers.IntegerField(default=30, min_value=1, max_value=365)
    page = serializers.IntegerField(default=1, min_value=1)
    limit = serializers.IntegerField(default=1000, min_value=1, max_value=5000)


class NewRxNoPaymentQuerySerializer(serializers.Serializer):
    """Serializer for validating query parameters for new rx without payment"""

    days = serializers.IntegerField(default=30, min_value=1, max_value=365)
    page = serializers.IntegerField(default=1, min_value=1)
    limit = serializers.IntegerField(default=1000, min_value=1, max_value=5000)
