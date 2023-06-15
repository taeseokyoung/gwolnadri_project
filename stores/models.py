from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Store(models.Model):
    """
    Store 모델
    한복 상점 정보를 담습니다.

    Attributes:
    owner (Foreignkey): owner_id(판매자)의 값을 가집니다
    store_name (varchar): 상점이름, 50자 제한
    store_address (varchar): 상점주소, 255자 제한
    location_x (Float): 상점 x좌표
    location_y(Float): 상점 y좌표
    star (positiveInt): 별점 1~5 값                -----**평균별점값으로 변경필요!!----
    """

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        # related_name="stores",
        verbose_name="판매자",
    )
    store_name = models.CharField("상점이름", max_length=50)
    store_address = models.CharField("상점주소", max_length=255, unique=True)
    location_x = models.FloatField("x좌표", blank=True, null=True)
    location_y = models.FloatField("y좌표", blank=True, null=True)
    likes = models.ManyToManyField(User, related_name="like_stores")
    store_bookmarks = models.ManyToManyField(
        User, related_name="bookmark_stores", blank=True
    )


    def __str__(self):
        return self.store_name


class Hanbok(models.Model):

    """
    Hanbok 모델
    한복 상품 정보를 담습니다.

    Attributes:
    store (Foreignkey): store_id(한복가게 id)의 값을 가집니다
    owner (Foreignkey): owner_id(판매자)의 값을 가집니다
    hanbok_name (varChar): 제품명, 255자 제한
    hanbok_description (varChar): 제품설명
    hanbok_price (positiveInt): 가격
    hanbok_image (Image) : 제품별 이미지 1장 (media/hanbok 폴더에 저장)
    """

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        # related_name="store",
        verbose_name="한복점",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    hanbok_name = models.CharField("제품명", max_length=255)
    hanbok_description = models.TextField("제품설명")
    hanbok_price = models.PositiveIntegerField("가격")
    hanbok_image = models.ImageField("제품이미지", blank=True, null=True, upload_to="hanbok")

    def __str__(self):
        return self.hanbok_name

      
class HanbokComment(models.Model):

    """
    HanbokComment 모델
    한복점 후기 정보를 담습니다.

    Attributes:
    store (Foreignkey): store_id(한복가게 id)의 값을 가집니다
    user (Foreignkey): user_id(사용자)의 값을 가집니다
    content (varChar): 후기내용, 100자 제한
    review_image (Image) : 후기사진, 제품별 이미지 1장 (media/review 폴더에 월별로 저장)
    created_at (datetime) : 생성일
    updated_at (datetime) : 수정일
    grade (positiveInt) : 평점, 1~5점을 부여합니다
    """

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField("후기내용", max_length=50)
    review_image = models.ImageField(
        "후기사진", blank=True, null=True, upload_to="review/%Y/%m/"
    )
    created_at = models.DateTimeField("생성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)
    grade = models.PositiveIntegerField(
        "평점", validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    def __str__(self):
        return self.content

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