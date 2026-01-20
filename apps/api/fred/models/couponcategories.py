from django.db import models
from fred.models.dhcoupons import DHCoupons

class CouponCategories(models.Model):
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
        db_table ="coupon_categories"
        managed = False          # existing table in fred schema
        app_label = "fred"

    def __str__(self):
        return f"{self.category_id} ({'included' if self.included else 'excluded'})"
