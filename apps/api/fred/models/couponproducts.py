from django.db import models
from fred.models.dhcoupons import DHCoupons

class CouponProducts(models.Model):
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
        db_table = "coupon_products"
        managed = False          # existing table
        app_label = "fred"

    def __str__(self):
        return f"{self.coupon_id} - {self.product_id}"
