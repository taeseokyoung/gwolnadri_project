from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


"""
Store 모델

한복 상점 정보를 담습니다.

Attributes:
user_id (Foreignkey): user_id(판매자)의 값을 가집니다
hanbok_store (varchar): 상점이름, 50자 제한
hanbok_address (varchar): 상점주소, 255자 제한
location_x (Float): 상점 x좌표
location_y(Float): 상점 y좌표  
star (positiveInt): 별점 1~5 값  -----**평균별점값으로 변경필요!!----
"""


class Store(models.Model):
    owner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stores",
        verbose_name="판매자",
        null=True,
    )
    store_name = models.CharField("상점이름", max_length=50)
    store_address = models.CharField("상점주소", max_length=255)
    location_x = models.FloatField("x좌표", blank=True, null=True)
    location_y = models.FloatField("y좌표", blank=True, null=True)
    star = models.PositiveIntegerField(
        "별점",
        validators=[MaxValueValidator(5), MinValueValidator(1)],
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.store_name


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
