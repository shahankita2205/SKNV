"""
Digital Health Models Module

Contains models related to digital health features:
- DHSettings
- DHCoupons
- CouponCategories
- CouponEmailRestrictions
- CouponProducts

Legacy Controller Mapping: DigitalHealthController
"""

from django.db import models


class DHSettings(models.Model):
    """
    Digital Health Settings model.
    Stores configuration settings for digital health features.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    metadata = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "dhsettings"
        verbose_name = "DH Setting"
        verbose_name_plural = "DH Settings"

    def __str__(self):
        return self.name


class DHCoupons(models.Model):
    """
    Digital Health Coupons model.
    Stores coupon codes and their configuration for digital health promotions.
    """

    coupon_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField(blank=True, null=True)
    date_expires = models.DateTimeField(blank=True, null=True)
    usage_count = models.IntegerField(default=0)
    individual_use = models.BooleanField(default=False)
    usage_limit = models.IntegerField(blank=True, null=True)
    usage_limit_per_user = models.IntegerField(blank=True, null=True)
    limit_usage_to_x_items = models.IntegerField(blank=True, null=True)
    free_shipping = models.BooleanField(default=False)
    minimum_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    maximum_amount = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(max_length=50)
    display_text = models.CharField(max_length=255, blank=True, null=True)
    product_restricted = models.BooleanField(default=False)
    category_restricted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "coupons"
        verbose_name = "DH Coupon"
        verbose_name_plural = "DH Coupons"

    def __str__(self):
        return self.code


class CouponCategories(models.Model):
    """
    Coupon category restrictions model.
    Links coupons to specific product categories for inclusion/exclusion rules.
    """

    restriction_id = models.AutoField(primary_key=True)
    coupon = models.ForeignKey(
        DHCoupons,
        on_delete=models.DO_NOTHING,
        related_name="categories",
        db_column="coupon_id",
    )
    category_id = models.CharField(max_length=255)
    included = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "coupon_categories"
        verbose_name = "Coupon Category"
        verbose_name_plural = "Coupon Categories"

    def __str__(self):
        status = "included" if self.included else "excluded"
        return f"{self.category_id} ({status})"


class CouponEmailRestrictions(models.Model):
    """
    Coupon email restrictions model.
    Restricts coupon usage to specific email addresses.
    """

    restriction_id = models.AutoField(primary_key=True)
    coupon = models.ForeignKey(
        DHCoupons,
        on_delete=models.DO_NOTHING,
        related_name="email_restrictions",
        db_column="coupon_id",
    )
    email = models.EmailField(max_length=255)

    class Meta:
        managed = False
        db_table = "coupon_email_restrictions"
        verbose_name = "Coupon Email Restriction"
        verbose_name_plural = "Coupon Email Restrictions"

    def __str__(self):
        return self.email


class CouponProducts(models.Model):
    """
    Coupon product restrictions model.
    Links coupons to specific products for inclusion/exclusion rules.
    """

    restriction_id = models.AutoField(primary_key=True)
    coupon = models.ForeignKey(
        DHCoupons,
        on_delete=models.DO_NOTHING,
        related_name="products",
        db_column="coupon_id",
    )
    product_id = models.CharField(max_length=255)
    included = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "coupon_products"
        verbose_name = "Coupon Product"
        verbose_name_plural = "Coupon Products"

    def __str__(self):
        status = "included" if self.included else "excluded"
        return f"{self.product_id} ({status})"


__all__ = [
    "DHSettings",
    "DHCoupons",
    "CouponCategories",
    "CouponEmailRestrictions",
    "CouponProducts",
]
