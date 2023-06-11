from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Store(models.Model):

    """Store 모델

    한복 상점 정보를 담습니다.

    Attributes:
    user_id (Foreignkey): user_id(판매자)의 값을 가집니다
    hanbok_store (varchar): 상점이름, 50자 제한
    hanbok_address (varchar): 상점주소, 255자 제한
    location_x (Float): 상점 x좌표
    location_y(Float): 상점 y좌표
    star (positiveInt): 별점 1~5 값                -----**평균별점값으로 변경필요!!----
    """

    owner_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stores",
        verbose_name="오너_Id",
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


class Hanbok(models.Model):

    """Hanbok 모델

    한복 상품 정보를 담습니다.

    Attributes:
    store_id (Foreignkey): store_id(한복가게 id)의 값을 가집니다
    hanbok_name (varChar): 제품명, 255자 제한
    hanbok_description (varChar): 제품설명
    hanbok_price (positiveInt): 가격
    hanbok_image (Image) : 제품별 이미지 1장 (media/hanbok 폴더에 저장)
    """

    store_id = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="한복점_Id",
    )

    hanbok_name = models.CharField("제품명", max_length=255)
    hanbok_description = models.TextField("제품설명")
    hanbok_price = models.PositiveIntegerField("가격")
    hanbok_image = models.ImageField(blank=True, upload_to="hanbok")

    def __str__(self):
        return self.hanbok_name
