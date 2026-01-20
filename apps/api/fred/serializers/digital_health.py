"""
digital health Serializers Module

Contains serializers related to digital health domain.
"""
from datetime import datetime
from django.db import IntegrityError
import requests
from venv import logger
from fred.models.couponcategories import CouponCategories
from fred.models.couponemailrestrictions import CouponEmailRestrictions
from fred.models.couponproducts import CouponProducts
from fred.models.dhcoupons import DHCoupons
from fred.models.digital_health import DHSettings
from rest_framework import serializers
from django.db import DatabaseError
from django.utils.timezone import now
from django.conf import settings
from django.db import transaction

# TODO: Migrate digital_health-related serializers from serializers.py


class DigitalHealthService:
    def __init__(self):
        self.api_url = settings.DIGITAL_HEALTH_API_URL
        self.api_token = settings.DIGITAL_HEALTH_API_TOKEN

    def get_feedbacks(self):
        print(self.api_token)
        print(self.api_url)
        url = f"{self.api_url}/patient/getfeedbacks"
        print(url)
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
    def get_dh_settings(self):
        try:
            queryset = DHSettings.objects.all().order_by("id")
            return list(queryset.values())

        except Exception as exc:
            logger.error(f"Error fetching DH settings: {exc}")
            raise

    @staticmethod
    @transaction.atomic
    def update_dh_settings(settings_payload, user):
        for setting_data in settings_payload:
            setting_id = setting_data["key"]
            enabled = bool(setting_data["enabled"])

            try:
                setting = DHSettings.objects.get(id=setting_id)
            except DHSettings.DoesNotExist:
                logger.info(
                    "Setting with ID #%s not found", setting_id,
                    extra={"module": "DH Settings"}
                )
                raise Exception(f"Setting with ID {setting_id} not found")

            setting.enabled = enabled
            setting.save(update_fields=["enabled"])

            status_text = "Enabled" if enabled else "Disabled"
            description = setting_data.get("description", "")
            log_message = f"{description} {status_text}".strip()

            logger.info(
                log_message,
                extra={
                    "user_id": getattr(user, "id", "SYS"),
                    "endpoint": "/digitalhealth/dhsettings",
                    "category": "Feature Flags",
                    "source": "app"
                }
            )

        # 🔁 External API call (same as PHP)
        DigitalHealthService._notify_admin_service()


    @staticmethod
    def _notify_admin_service():
        # Check if admin API settings exist
        admin_api_url = getattr(settings, 'ADMIN_API_URL', None)
        admin_api_token = getattr(settings, 'ADMIN_API_TOKEN', None)
        
        if not admin_api_url or not admin_api_token:
            logger.warning("Admin API URL or token not configured, skipping notification")
            return False
        
        url = f"{admin_api_url}/updatedhfeatures"

        headers = {
            "sknvtoken": admin_api_token,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.exception("Failed calling admin update API")
            return False
    
    @staticmethod
    def get_dh_coupons():
        try:
            coupons = (
                DHCoupons.objects
                .exclude(status="trash")
                .order_by("coupon_id")
            )

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

                # 🔹 Products
                products = CouponProducts.objects.filter(coupon=coupon)
                product_ids = []
                for product in products:
                    product_ids.append(str(product.product_id))
                    coupon_data["product_restriction_type"] = product.included

                coupon_data["products"] = ",".join(product_ids)

                # 🔹 Email Restrictions
                email_restrictions = CouponEmailRestrictions.objects.filter(coupon=coupon)
                for restriction in email_restrictions:
                    coupon_data["email_restrictions"].append(
                        {
                            "restriction_id": restriction.restriction_id,
                            "email": restriction.email,
                        }
                    )

                # 🔹 Categories
                categories = CouponCategories.objects.filter(coupon=coupon)
                for category in categories:
                    coupon_data["categories"].append(
                        {
                            "restriction_id": category.restriction_id,
                            "category_id": category.category_id,
                            "included": category.included,
                        }
                    )

                result.append(coupon_data)

            return result

        except Exception as exc:
            logger.info(
                "Fail to fetch DH Coupons %s", str(exc),
                extra={
                    "user": "SYS",
                    "module": "DH Coupons",
                    "source": "app"
                }
            )
            raise

    @staticmethod
    @transaction.atomic
    def create_dh_coupon(payload):
        try:
            coupon = DHCoupons.objects.create(
                code=payload["code"],
                description=payload.get("description"),
                discount_type=payload["discount_type"],
                amount=payload["amount"],
                usage_limit=payload.get("usage_limit"),
                usage_limit_per_user=payload.get("usage_limit_per_user"),
                status=payload["status"],
                display_text=payload.get("display_text"),
                individual_use=payload.get("individual_use", False),
                free_shipping=payload.get("free_shipping", False),
                limit_usage_to_x_items=payload.get("limit_usage_to_x_items"),
                usage_count=0,
                minimum_amount=payload.get("minimum_amount") or None,
                maximum_amount=payload.get("maximum_amount") or None,
                product_restricted=False,
                category_restricted=False,
                date_created=now(),
                date_modified=now(),
                date_expires=(
                    datetime.fromisoformat(payload["date_expires"])
                    if payload.get("date_expires")
                    else None
                ),
            )

            # -------------------------
            # Product Restrictions
            # -------------------------
            product_restricted = False
            product_ids = payload.get("product_id")

            if product_ids:
                if isinstance(product_ids, str):
                    product_ids = [
                        pid.strip() for pid in product_ids.split(",") if pid.strip()
                    ]

                for product_id in product_ids:
                    CouponProducts.objects.create(
                        coupon=coupon,
                        product_id=product_id,
                        included=payload.get("product_restriction_type") == "included",
                    )
                    product_restricted = True

            coupon.product_restricted = product_restricted

            # -------------------------
            # Category Restrictions
            # -------------------------
            category_restricted = False
            category_ids = payload.get("category_id")

            if category_ids:
                if isinstance(category_ids, list):
                    category_ids = ",".join(
                        [cid.strip() for cid in category_ids if cid.strip()]
                    )

                if category_ids:
                    CouponCategories.objects.create(
                        coupon=coupon,
                        category_id=category_ids,
                        included=payload.get("category_restriction_type") == "included",
                    )
                    category_restricted = True

            coupon.category_restricted = category_restricted

            # -------------------------
            # Email Restrictions
            # -------------------------
            if payload.get("email_restrictions"):
                CouponEmailRestrictions.objects.create(
                    coupon=coupon,
                    email=payload["email_restrictions"],
                )

            coupon.save(update_fields=["product_restricted", "category_restricted"])

            return {
                "coupon_id": coupon.coupon_id,
                "code": coupon.code,
                "message": "Coupon created successfully",
            }

        except IntegrityError as e:
            error_str = str(e)
            if "coupons_code_key" in error_str or "duplicate" in error_str.lower():
                # Extract the code from the error message if possible
                code = payload.get("code", "this code")
                raise Exception(f"A coupon with code '{code}' already exists")
            raise
        except Exception:
            raise
    
    @staticmethod
    @transaction.atomic
    def update_dh_coupon(coupon_id, payload):
        coupon = DHCoupons.objects.filter(coupon_id=coupon_id).first()
        if not coupon:
            raise Exception("Coupon not found")

        # -------------------------
        # Update coupon fields
        # -------------------------
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
            if field in payload:
                value = payload[field]
                if field in ["minimum_amount", "maximum_amount"] and value == "":
                    value = None
                setattr(coupon, field, value)

        # -------------------------
        # Product Restrictions
        # -------------------------
        if "product_id" in payload:
            CouponProducts.objects.filter(coupon=coupon).delete()
            product_restricted = False

            product_ids = payload.get("product_id")
            if product_ids:
                if isinstance(product_ids, str):
                    product_ids = [
                        pid.strip() for pid in product_ids.split(",") if pid.strip()
                    ]

                for product_id in product_ids:
                    CouponProducts.objects.create(
                        coupon=coupon,
                        product_id=product_id,
                        included=payload.get("product_restriction_type") == "included",
                    )
                    product_restricted = True
        else:
            product_restricted = CouponProducts.objects.filter(coupon=coupon).exists()

        coupon.product_restricted = product_restricted

        # -------------------------
        # Category Restrictions
        # -------------------------
        if "category_id" in payload:
            CouponCategories.objects.filter(coupon=coupon).delete()
            category_restricted = False

            category_ids = payload.get("category_id")
            if category_ids:
                if isinstance(category_ids, list):
                    category_ids = ",".join(
                        cid.strip() for cid in category_ids if cid.strip()
                    )

                if category_ids:
                    CouponCategories.objects.create(
                        coupon=coupon,
                        category_id=category_ids,
                        included=payload.get("category_restriction_type") == "included",
                    )
                    category_restricted = True
        else:
            category_restricted = CouponCategories.objects.filter(
                coupon=coupon
            ).exists()

        coupon.category_restricted = category_restricted

        # -------------------------
        # Email Restrictions
        # -------------------------
        if "email_restrictions" in payload:
            CouponEmailRestrictions.objects.filter(coupon=coupon).delete()

            if payload.get("email_restrictions"):
                CouponEmailRestrictions.objects.create(
                    coupon=coupon,
                    email=payload["email_restrictions"],
                )

        # -------------------------
        # Date handling
        # -------------------------
        coupon.date_modified = now()

        if "date_expires" in payload:
            if payload["date_expires"]:
                coupon.date_expires = datetime.fromisoformat(
                    payload["date_expires"]
                )
            else:
                coupon.date_expires = None

        coupon.save()

        return {
            "coupon_id": coupon.coupon_id,
            "message": "Coupon updated successfully",
        }
    
    @staticmethod
    def delete_dh_coupon(coupon_id):
        coupon = DHCoupons.objects.filter(coupon_id=coupon_id).first()

        if not coupon:
            raise Exception("Coupon not found")

        coupon.status = "trash"
        coupon.save(update_fields=["status"])

        return {
            "message": "Coupon moved to trash successfully",
        }



__all__ = [
    "get_feedbacks",
    "get_dh_settings",
    "update_dh_settings",
    "get_dh_coupons",
    "create_dh_coupon",
    "update_dh_coupon",
    "delete_dh_coupon",
]
