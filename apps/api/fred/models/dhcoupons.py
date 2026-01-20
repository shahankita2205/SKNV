from django.db import models


class DHCoupons(models.Model):
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
        db_table = "coupons"
        managed = False            # IMPORTANT: existing DB table
        app_label = "fred"

    def __str__(self):
        return self.code
