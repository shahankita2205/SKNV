from django.db import models
from fred.models.dhcoupons import DHCoupons

class CouponEmailRestrictions(models.Model):
    restriction_id = models.AutoField(primary_key=True)

    coupon = models.ForeignKey(
        DHCoupons,
        on_delete=models.DO_NOTHING,
        related_name="email_restrictions",
        db_column="coupon_id",
    )

    email = models.EmailField(max_length=255)

    class Meta:
        db_table = "coupon_email_restrictions"
        managed = False          # existing DB table
        app_label = "fred"

    def __str__(self):
        return self.email
