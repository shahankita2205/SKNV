"""
Digital Health Serializers Module

Contains serializers and service class for digital health domain.

Legacy Controller Mapping: DigitalHealthController

Serializers:
    - DHSettingsSerializer: Full settings serialization
    - DHSettingsListSerializer: List view
    - DHSettingsUpdateItemSerializer: Single setting update item
    - DHSettingsUpdateRequestSerializer: Bulk update request
    - DHCouponSerializer: Full coupon serialization
    - DHCouponListSerializer: List view with restrictions
    - DHCouponCreateSerializer: Create with validation
    - DHCouponUpdateSerializer: Update with validation
    - DHCouponRestrictionsSerializer: Nested restrictions
    - DHCouponCreateResponseSerializer: Create response
    - DHCouponUpdateResponseSerializer: Update response

Service:
    - DigitalHealthService: Business logic for external API calls
"""

import logging
from datetime import datetime

import requests
from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils.timezone import now
from rest_framework import serializers

from fred.models.digital_health import (
    DHSettings,
    DHCoupons,
    CouponCategories,
    CouponEmailRestrictions,
    CouponProducts,
)

logger = logging.getLogger(__name__)


# =============================================================================
# ERROR CODES
# =============================================================================


class DigitalHealthErrorCodes:
    """Error codes for digital health operations"""

    ERROR_COUPON_NOT_FOUND = 18001
    ERROR_COUPON_ALREADY_EXISTS = 18002
    ERROR_UNABLE_CREATE_COUPON = 18003
    ERROR_UNABLE_UPDATE_COUPON = 18004
    ERROR_UNABLE_DELETE_COUPON = 18005
    ERROR_SETTING_NOT_FOUND = 18006
    ERROR_UNABLE_UPDATE_SETTINGS = 18007


class DigitalHealthServiceException(Exception):
    """Exception for digital health service errors"""

    def __init__(self, message: str, code: int = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


# =============================================================================
# DH SETTINGS SERIALIZERS
# =============================================================================


class DHSettingsSerializer(serializers.ModelSerializer):
    """
    Full DH Settings serializer for detailed views.
    """

    class Meta:
        model = DHSettings
        fields = [
            "id",
            "name",
            "description",
            "metadata",
            "enabled",
        ]


class DHSettingsListSerializer(serializers.ModelSerializer):
    """
    Serializer for settings list views.
    """

    class Meta:
        model = DHSettings
        fields = [
            "id",
            "name",
            "description",
            "enabled",
        ]


class DHSettingsUpdateItemSerializer(serializers.Serializer):
    """
    Serializer for a single setting update item.
    """

    key = serializers.IntegerField(required=True)
    enabled = serializers.BooleanField(required=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_key(self, value):
        """Validate that setting exists"""
        if not DHSettings.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Setting with ID {value} not found")
        return value


class DHSettingsUpdateRequestSerializer(serializers.Serializer):
    """
    Serializer for bulk settings update request.
    """

    settings = DHSettingsUpdateItemSerializer(many=True, required=True)

    def validate_settings(self, value):
        """Validate at least one setting provided"""
        if not value:
            raise serializers.ValidationError("At least one setting is required")
        return value


# =============================================================================
# DH COUPONS SERIALIZERS - BASE
# =============================================================================


class DHCouponSerializer(serializers.ModelSerializer):
    """
    Full DH Coupon serializer for detailed views.
    """

    class Meta:
        model = DHCoupons
        fields = [
            "coupon_id",
            "code",
            "description",
            "discount_type",
            "amount",
            "date_created",
            "date_modified",
            "date_expires",
            "usage_count",
            "individual_use",
            "usage_limit",
            "usage_limit_per_user",
            "limit_usage_to_x_items",
            "free_shipping",
            "minimum_amount",
            "maximum_amount",
            "status",
            "display_text",
            "product_restricted",
            "category_restricted",
        ]


class CouponCategoryItemSerializer(serializers.Serializer):
    """Serializer for coupon category restriction item"""

    restriction_id = serializers.IntegerField(required=False)
    category_id = serializers.CharField()
    included = serializers.BooleanField()


class CouponEmailRestrictionItemSerializer(serializers.Serializer):
    """Serializer for coupon email restriction item"""

    restriction_id = serializers.IntegerField(required=False)
    email = serializers.EmailField()


class DHCouponRestrictionsSerializer(serializers.Serializer):
    """Serializer for coupon restrictions"""

    products = serializers.CharField(required=False, allow_blank=True)
    product_restriction_type = serializers.ChoiceField(
        choices=[("included", "Included"), ("excluded", "Excluded")],
        required=False,
    )
    categories = CouponCategoryItemSerializer(many=True, required=False)
    category_restriction_type = serializers.ChoiceField(
        choices=[("included", "Included"), ("excluded", "Excluded")],
        required=False,
    )
    email_restrictions = serializers.EmailField(required=False, allow_blank=True)


class DHCouponListSerializer(serializers.Serializer):
    """
    Serializer for coupon list with restrictions.
    Used in list endpoint.
    """

    coupon_id = serializers.IntegerField()
    code = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    discount_type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    date_created = serializers.DateTimeField()
    date_modified = serializers.DateTimeField(allow_null=True)
    date_expires = serializers.DateTimeField(allow_null=True)
    usage_count = serializers.IntegerField()
    individual_use = serializers.BooleanField()
    usage_limit = serializers.IntegerField(allow_null=True)
    usage_limit_per_user = serializers.IntegerField(allow_null=True)
    limit_usage_to_x_items = serializers.IntegerField(allow_null=True)
    free_shipping = serializers.BooleanField()
    minimum_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    maximum_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, allow_null=True
    )
    status = serializers.CharField()
    display_text = serializers.CharField(allow_null=True)
    products = serializers.CharField()
    email_restrictions = CouponEmailRestrictionItemSerializer(many=True)
    categories = CouponCategoryItemSerializer(many=True)


# =============================================================================
# DH COUPONS SERIALIZERS - CREATE
# =============================================================================


class DHCouponCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new DH coupon.
    Includes validation and create logic.
    """

    code = serializers.CharField(required=True, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    discount_type = serializers.CharField(required=True, max_length=50)
    amount = serializers.DecimalField(
        required=True, max_digits=10, decimal_places=2, min_value=0
    )
    usage_limit = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    usage_limit_per_user = serializers.IntegerField(
        required=False, min_value=0, allow_null=True
    )
    status = serializers.CharField(required=True, max_length=50)
    display_text = serializers.CharField(required=False, max_length=255, allow_blank=True)
    individual_use = serializers.BooleanField(required=False, default=False)
    free_shipping = serializers.BooleanField(required=False, default=False)
    limit_usage_to_x_items = serializers.IntegerField(
        required=False, min_value=0, allow_null=True
    )
    minimum_amount = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2, min_value=0, allow_null=True
    )
    maximum_amount = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2, min_value=0, allow_null=True
    )
    date_expires = serializers.DateTimeField(required=False, allow_null=True)

    # Restrictions
    product_id = serializers.CharField(required=False, allow_blank=True)
    product_restriction_type = serializers.ChoiceField(
        choices=[("included", "Included"), ("excluded", "Excluded")],
        required=False,
    )
    category_id = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    category_restriction_type = serializers.ChoiceField(
        choices=[("included", "Included"), ("excluded", "Excluded")],
        required=False,
    )
    email_restrictions = serializers.EmailField(required=False, allow_blank=True)

    def validate_code(self, value):
        """Validate code is not empty and check uniqueness"""
        if not value or not value.strip():
            raise serializers.ValidationError("Code is required")
        code = value.strip()
        if DHCoupons.objects.filter(code=code).exclude(status="trash").exists():
            raise serializers.ValidationError(f"A coupon with code '{code}' already exists")
        return code

    def validate_discount_type(self, value):
        """Validate discount type"""
        valid_types = ["percent", "fixed", "fixed_cart"]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Discount type must be one of: {', '.join(valid_types)}"
            )
        return value

    def validate_status(self, value):
        """Validate status"""
        valid_statuses = ["active", "inactive", "trash"]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_statuses)}"
            )
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        if attrs.get("minimum_amount") and attrs.get("maximum_amount"):
            if attrs["minimum_amount"] > attrs["maximum_amount"]:
                raise serializers.ValidationError(
                    "Minimum amount cannot be greater than maximum amount"
                )
        return attrs

    def create(self, validated_data):
        """
        Create a new coupon with restrictions.

        Returns:
            DHCoupons: Created coupon instance

        Raises:
            DigitalHealthServiceException: If creation fails
        """
        try:
            with transaction.atomic():
                # Extract restrictions data
                product_ids = validated_data.pop("product_id", None)
                product_restriction_type = validated_data.pop("product_restriction_type", None)
                category_ids = validated_data.pop("category_id", None)
                category_restriction_type = validated_data.pop(
                    "category_restriction_type", None
                )
                email_restrictions = validated_data.pop("email_restrictions", None)

                # Create coupon
                coupon = DHCoupons.objects.create(
                    code=validated_data["code"],
                    description=validated_data.get("description"),
                    discount_type=validated_data["discount_type"],
                    amount=validated_data["amount"],
                    usage_limit=validated_data.get("usage_limit"),
                    usage_limit_per_user=validated_data.get("usage_limit_per_user"),
                    status=validated_data["status"],
                    display_text=validated_data.get("display_text"),
                    individual_use=validated_data.get("individual_use", False),
                    free_shipping=validated_data.get("free_shipping", False),
                    limit_usage_to_x_items=validated_data.get("limit_usage_to_x_items"),
                    usage_count=0,
                    minimum_amount=validated_data.get("minimum_amount"),
                    maximum_amount=validated_data.get("maximum_amount"),
                    product_restricted=False,
                    category_restricted=False,
                    date_created=now(),
                    date_modified=now(),
                    date_expires=validated_data.get("date_expires"),
                )

                # Product Restrictions
                product_restricted = False
                if product_ids:
                    if isinstance(product_ids, str):
                        product_ids = [
                            pid.strip() for pid in product_ids.split(",") if pid.strip()
                        ]

                    for product_id in product_ids:
                        CouponProducts.objects.create(
                            coupon=coupon,
                            product_id=product_id,
                            included=product_restriction_type == "included",
                        )
                        product_restricted = True

                coupon.product_restricted = product_restricted

                # Category Restrictions
                category_restricted = False
                if category_ids:
                    category_ids_str = ",".join(
                        [cid.strip() for cid in category_ids if cid.strip()]
                    )
                    if category_ids_str:
                        CouponCategories.objects.create(
                            coupon=coupon,
                            category_id=category_ids_str,
                            included=category_restriction_type == "included",
                        )
                        category_restricted = True

                coupon.category_restricted = category_restricted

                # Email Restrictions
                if email_restrictions:
                    CouponEmailRestrictions.objects.create(
                        coupon=coupon, email=email_restrictions
                    )

                coupon.save(update_fields=["product_restricted", "category_restricted"])

                logger.info(f"DH Coupon #{coupon.coupon_id} created: {coupon.code}")
                return coupon

        except IntegrityError as e:
            error_str = str(e)
            if "coupons_code_key" in error_str or "duplicate" in error_str.lower():
                code = validated_data.get("code", "this code")
                raise DigitalHealthServiceException(
                    f"A coupon with code '{code}' already exists",
                    DigitalHealthErrorCodes.ERROR_COUPON_ALREADY_EXISTS,
                )
            logger.error(f"Error creating DH coupon: {e}")
            raise DigitalHealthServiceException(
                "Unable to create coupon",
                DigitalHealthErrorCodes.ERROR_UNABLE_CREATE_COUPON,
            )
        except Exception as e:
            logger.error(f"Error creating DH coupon: {e}")
            raise DigitalHealthServiceException(
                "Unable to create coupon",
                DigitalHealthErrorCodes.ERROR_UNABLE_CREATE_COUPON,
            )


# =============================================================================
# DH COUPONS SERIALIZERS - UPDATE
# =============================================================================


class DHCouponUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating an existing DH coupon.
    """

    code = serializers.CharField(required=False, max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    discount_type = serializers.CharField(required=False, max_length=50)
    amount = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2, min_value=0
    )
    usage_limit = serializers.IntegerField(required=False, min_value=0, allow_null=True)
    usage_limit_per_user = serializers.IntegerField(
        required=False, min_value=0, allow_null=True
    )
    status = serializers.CharField(required=False, max_length=50)
    display_text = serializers.CharField(required=False, max_length=255, allow_blank=True)
    individual_use = serializers.BooleanField(required=False)
    free_shipping = serializers.BooleanField(required=False)
    limit_usage_to_x_items = serializers.IntegerField(
        required=False, min_value=0, allow_null=True
    )
    minimum_amount = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2, min_value=0, allow_null=True
    )
    maximum_amount = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2, min_value=0, allow_null=True
    )
    date_expires = serializers.DateTimeField(required=False, allow_null=True)

    # Restrictions
    product_id = serializers.CharField(required=False, allow_blank=True)
    product_restriction_type = serializers.ChoiceField(
        choices=[("included", "Included"), ("excluded", "Excluded")],
        required=False,
    )
    category_id = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    category_restriction_type = serializers.ChoiceField(
        choices=[("included", "Included"), ("excluded", "Excluded")],
        required=False,
    )
    email_restrictions = serializers.EmailField(required=False, allow_blank=True)

    def validate_code(self, value):
        """Validate code uniqueness if provided"""
        if value:
            code = value.strip()
            coupon_id = self.context.get("coupon_id")
            queryset = DHCoupons.objects.filter(code=code).exclude(status="trash")
            if coupon_id:
                queryset = queryset.exclude(coupon_id=coupon_id)
            if queryset.exists():
                raise serializers.ValidationError(f"A coupon with code '{code}' already exists")
            return code
        return value

    def validate_discount_type(self, value):
        """Validate discount type"""
        if value:
            valid_types = ["percent", "fixed", "fixed_cart"]
            if value not in valid_types:
                raise serializers.ValidationError(
                    f"Discount type must be one of: {', '.join(valid_types)}"
                )
        return value

    def validate_status(self, value):
        """Validate status"""
        if value:
            valid_statuses = ["active", "inactive", "trash"]
            if value not in valid_statuses:
                raise serializers.ValidationError(
                    f"Status must be one of: {', '.join(valid_statuses)}"
                )
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        if attrs.get("minimum_amount") and attrs.get("maximum_amount"):
            if attrs["minimum_amount"] > attrs["maximum_amount"]:
                raise serializers.ValidationError(
                    "Minimum amount cannot be greater than maximum amount"
                )
        return attrs

    def update(self, instance, validated_data):
        """
        Update an existing coupon.

        Args:
            instance: DHCoupons instance to update
            validated_data: Validated data from request

        Returns:
            DHCoupons: Updated coupon instance

        Raises:
            DigitalHealthServiceException: If update fails
        """
        try:
            with transaction.atomic():
                # Extract restrictions data
                product_ids = validated_data.pop("product_id", None)
                product_restriction_type = validated_data.pop("product_restriction_type", None)
                category_ids = validated_data.pop("category_id", None)
                category_restriction_type = validated_data.pop(
                    "category_restriction_type", None
                )
                email_restrictions = validated_data.pop("email_restrictions", None)

                # Update coupon fields
                updatable_fields = [
                    "code",
                    "description",
                    "discount_type",
                    "amount",
                    "usage_limit",
                    "usage_limit_per_user",
                    "minimum_amount",
                    "maximum_amount",
                    "status",
                    "individual_use",
                    "free_shipping",
                    "limit_usage_to_x_items",
                    "display_text",
                ]

                for field in updatable_fields:
                    if field in validated_data:
                        value = validated_data[field]
                        if field in ["minimum_amount", "maximum_amount"] and value == "":
                            value = None
                        setattr(instance, field, value)

                # Product Restrictions
                if product_ids is not None:
                    CouponProducts.objects.filter(coupon=instance).delete()
                    product_restricted = False

                    if product_ids:
                        if isinstance(product_ids, str):
                            product_ids = [
                                pid.strip() for pid in product_ids.split(",") if pid.strip()
                            ]

                        for product_id in product_ids:
                            CouponProducts.objects.create(
                                coupon=instance,
                                product_id=product_id,
                                included=product_restriction_type == "included",
                            )
                            product_restricted = True
                else:
                    product_restricted = CouponProducts.objects.filter(
                        coupon=instance
                    ).exists()

                instance.product_restricted = product_restricted

                # Category Restrictions
                if category_ids is not None:
                    CouponCategories.objects.filter(coupon=instance).delete()
                    category_restricted = False

                    if category_ids:
                        category_ids_str = ",".join(
                            cid.strip() for cid in category_ids if cid.strip()
                        )
                        if category_ids_str:
                            CouponCategories.objects.create(
                                coupon=instance,
                                category_id=category_ids_str,
                                included=category_restriction_type == "included",
                            )
                            category_restricted = True
                else:
                    category_restricted = CouponCategories.objects.filter(
                        coupon=instance
                    ).exists()

                instance.category_restricted = category_restricted

                # Email Restrictions
                if email_restrictions is not None:
                    CouponEmailRestrictions.objects.filter(coupon=instance).delete()

                    if email_restrictions:
                        CouponEmailRestrictions.objects.create(
                            coupon=instance, email=email_restrictions
                        )

                # Date handling
                instance.date_modified = now()

                if "date_expires" in validated_data:
                    instance.date_expires = validated_data["date_expires"]

                instance.save()

                logger.info(f"DH Coupon #{instance.coupon_id} updated: {instance.code}")
                return instance

        except Exception as e:
            logger.error(f"Error updating DH coupon #{instance.coupon_id}: {e}")
            raise DigitalHealthServiceException(
                "Unable to update coupon",
                DigitalHealthErrorCodes.ERROR_UNABLE_UPDATE_COUPON,
            )


# =============================================================================
# RESPONSE SERIALIZERS
# =============================================================================


class DHCouponCreateResponseSerializer(serializers.Serializer):
    """Response serializer for create endpoint"""

    coupon_id = serializers.IntegerField()
    code = serializers.CharField()
    message = serializers.CharField()


class DHCouponUpdateResponseSerializer(serializers.Serializer):
    """Response serializer for update endpoint"""

    coupon_id = serializers.IntegerField()
    message = serializers.CharField()


class DHCouponDeleteResponseSerializer(serializers.Serializer):
    """Response serializer for delete endpoint"""

    message = serializers.CharField()


# =============================================================================
# DIGITAL HEALTH SERVICE
# =============================================================================


class DigitalHealthService:
    """
    Service class for digital health external API operations.

    Contains methods for external API calls that don't fit into serializers.
    """

    def __init__(self):
        self.api_url = getattr(settings, "DIGITAL_HEALTH_API_URL", None)
        self.api_token = getattr(settings, "DIGITAL_HEALTH_API_TOKEN", None)

    def get_feedbacks(self):
        """
        Fetch feedbacks from external digital health API.

        Returns:
            dict: Feedbacks data from API
            False: If request fails
        """
        if not self.api_url or not self.api_token:
            logger.warning("Digital Health API URL or token not configured")
            return False

        url = f"{self.api_url}/patient/getfeedbacks"
        headers = {
            "sknvtoken": self.api_token,
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as exc:
            logger.error(f"Error fetching feedbacks: {exc}")
            return False

    @staticmethod
    @transaction.atomic
    def update_dh_settings(settings_payload, user):
        """
        Update multiple digital health settings.

        Args:
            settings_payload: List of dicts with 'key', 'enabled', and optional 'description'
            user: Request user for logging
        """
        for setting_data in settings_payload:
            setting_id = setting_data["key"]
            enabled = bool(setting_data["enabled"])

            try:
                setting = DHSettings.objects.get(id=setting_id)
            except DHSettings.DoesNotExist:
                logger.info(f"Setting with ID #{setting_id} not found")
                raise DigitalHealthServiceException(
                    f"Setting with ID {setting_id} not found",
                    DigitalHealthErrorCodes.ERROR_SETTING_NOT_FOUND,
                )

            setting.enabled = enabled
            setting.save(update_fields=["enabled"])

            status_text = "Enabled" if enabled else "Disabled"
            description = setting_data.get("description", "")
            log_message = f"{description} {status_text}".strip()

            logger.info(
                f"{log_message} - User: {getattr(user, 'id', 'SYS')}, "
                f"Endpoint: /digital-health/settings/update/"
            )

    @staticmethod
    def get_dh_coupons():
        """
        Get all digital health coupons with their restrictions.

        Returns:
            list: List of coupon dicts with products, email_restrictions, categories
        """
        try:
            coupons = DHCoupons.objects.exclude(status="trash").order_by("coupon_id")
            result = []

            for coupon in coupons:
                coupon_data = {
                    "coupon_id": coupon.coupon_id,
                    "code": coupon.code,
                    "description": coupon.description,
                    "discount_type": coupon.discount_type,
                    "amount": coupon.amount,
                    "date_created": coupon.date_created,

                    
                    "date_modified": coupon.date_modified,
                    "date_expires": coupon.date_expires,
                    "usage_count": coupon.usage_count,
                    "individual_use": coupon.individual_use,
                    "usage_limit": coupon.usage_limit,
                    "usage_limit_per_user": coupon.usage_limit_per_user,
                    "limit_usage_to_x_items": coupon.limit_usage_to_x_items,
                    "free_shipping": coupon.free_shipping,
                    "minimum_amount": coupon.minimum_amount,
                    "maximum_amount": coupon.maximum_amount,
                    "status": coupon.status,
                    "display_text": coupon.display_text,
                    "products": "",
                    "email_restrictions": [],
                    "categories": [],
                }

                # Products
                products = CouponProducts.objects.filter(coupon=coupon)
                product_ids = []
                for product in products:
                    product_ids.append(str(product.product_id))
                    coupon_data["product_restriction_type"] = product.included

                coupon_data["products"] = ",".join(product_ids)

                # Email Restrictions
                email_restrictions = CouponEmailRestrictions.objects.filter(coupon=coupon)
                for restriction in email_restrictions:
                    coupon_data["email_restrictions"].append({
                        "restriction_id": restriction.restriction_id,
                        "email": restriction.email,
                    })

                # Categories
                categories = CouponCategories.objects.filter(coupon=coupon)
                for category in categories:
                    coupon_data["categories"].append({
                        "restriction_id": category.restriction_id,
                        "category_id": category.category_id,
                        "included": category.included,
                    })

                result.append(coupon_data)

            return result
        except Exception as exc:
            logger.error(f"Failed to fetch DH Coupons: {exc}")
            raise

    @staticmethod
    def delete_dh_coupon(coupon_id):
        """
        Soft delete a coupon by setting status to 'trash'.

        Args:
            coupon_id: Coupon primary key

        Returns:
            dict: Success message

        Raises:
            DigitalHealthServiceException: If coupon not found
        """
        try:
            coupon = DHCoupons.objects.filter(coupon_id=coupon_id).first()

            if not coupon:
                raise DigitalHealthServiceException(
                    "Coupon not found",
                    DigitalHealthErrorCodes.ERROR_COUPON_NOT_FOUND,
                )

            coupon.status = "trash"
            coupon.save(update_fields=["status"])

            logger.info(f"DH Coupon #{coupon_id} moved to trash")
            return {"message": "Coupon moved to trash successfully"}

        except DigitalHealthServiceException:
            raise
        except Exception as e:
            logger.error(f"Error deleting DH coupon #{coupon_id}: {e}")
            raise DigitalHealthServiceException(
                "Unable to delete coupon",
                DigitalHealthErrorCodes.ERROR_UNABLE_DELETE_COUPON,
            )


__all__ = [
    "DigitalHealthErrorCodes",
    "DigitalHealthServiceException",
    "DHSettingsSerializer",
    "DHSettingsListSerializer",
    "DHSettingsUpdateItemSerializer",
    "DHSettingsUpdateRequestSerializer",
    "DHCouponSerializer",
    "DHCouponListSerializer",
    "DHCouponCreateSerializer",
    "DHCouponUpdateSerializer",
    "DHCouponRestrictionsSerializer",
    "DHCouponCreateResponseSerializer",
    "DHCouponUpdateResponseSerializer",
    "DHCouponDeleteResponseSerializer",
    "DigitalHealthService",
]
