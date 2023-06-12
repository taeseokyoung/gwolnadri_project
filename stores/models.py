from django.db import models
from users.models import User


# class HanbokStore(models.Model):
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     hanbok_store = models.CharField(max_length=20)

#     def __str__(self):
#         return self.hanbok_store


# class Hanbok(models.Model):
#     store_name = models.ForeignKey(
#         HanbokStore, on_delete=models.CASCADE, related_name="hanbok_list"
#     )
#     hanbok_owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     hanbok_name = models.CharField(
#         max_length=20,
#     )
#     hanbok_description = models.CharField(max_length=100)
#     hanbok_price = models.IntegerField()
#     hanbok_image = models.ImageField(upload_to="media/stores/%m/")

#     def __str__(self):
#         return self.hanbok_name


class PurchaseRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tid = models.CharField(max_length=100)
    partner_order_id = models.BigIntegerField()
    partner_user_id = models.CharField(max_length=50)
    item_name = models.CharField(max_length=50)
    quantity = models.IntegerField()
    total_amount = models.IntegerField()
    vat_amount = models.IntegerField()
    tax_free_amount = models.IntegerField(default=0)
    rsrvt_date = models.DateTimeField()
    rsrvt_time = models.TimeField()
    created_at = models.DateTimeField()
    payment_method_type = models.CharField(max_length=50, blank=True, null=True)
    aid = models.CharField(max_length=100, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
