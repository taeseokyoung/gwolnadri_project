from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Store(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="stores", null=True
    )
    hanbok_store = models.CharField(max_length=255)
    hanbok_address = models.CharField(max_length=255)  # 변경 필요
    # hanbok_map =  #카카오 지도 활용해보기
    location_x = models.FloatField(null=True, blank=True)
    location_y = models.FloatField(null=True, blank=True)
    star = models.PositiveIntegerField(
        "별점", validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    def __str__(self):
        return self.hanbok_store
