from rest_framework import serializers
from .models import Store, Hanbok, HanbokComment, PurchaseRecord
import requests, json
import os
import environ
from django.db.models import Avg


# ✅ 위치정보 api
def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": os.environ.get("KakaoAK")}
    location = requests.get(url, headers=headers).json()["documents"][0]
    result = [
        location["x"],
        location["y"],
    ]
    return result


# ✅ 한복집 리스트 (id, 판매자, 가게이름, 가게주소, x좌표, y좌표, 전체 좋아요 수, 평균 별점)
class StoreListSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    avg_stars = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.id

    def get_total_likes(self, obj):
        return obj.likes.count()

    def get_avg_stars(self, obj):
        return HanbokComment.objects.filter(store=obj.id).aggregate(
            avg_stars=Avg("grade")
        )

    class Meta:
        model = Store
        fields = (
            "id",
            "owner",
            "store_name",
            "store_address",
            "location_x",
            "location_y",
            "likes",
            "total_likes",
            "avg_stars",
        )


# ✅ 한복집 추가 (가게이름, 가게주소)
class CreateStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            "store_name",
            "store_address",
        )

    # ✅ 한복집 x,y좌표 | 별점(후기없는경우 0) 추가
    def create(self, validated_data):
        location_result = get_location(validated_data["store_address"])
        print(validated_data)
        store = Store.objects.create(
            owner=validated_data["owner"],
            store_name=validated_data["store_name"],
            store_address=validated_data["store_address"],
            location_x=location_result[0],
            location_y=location_result[1],
            star=0,
        )
        store.save()
        return store


# ✅ 한복상품정보 (제품명, 제품설명, 가격, 이미지)
class HanbokSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_store(self, obj):
        return obj.store.store_name

    def get_owner(self, obj):
        owner = obj.owner.email.split("@")[0]
        return owner

    class Meta:
        model = Hanbok
        fields = (
            "id",
            "store",
            "owner",
            "hanbok_name",
            "hanbok_description",
            "hanbok_price",
            "hanbok_image",
        )


# ✅ 한복상품등록 (제품명, 제품설명, 가격, 이미지)
class CreateHanbokSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hanbok
        fields = [
            "hanbok_name",
            "hanbok_description",
            "hanbok_price",
            "hanbok_image",
        ]


# ✅ 한복점 리뷰 열람 (후기내용, 후기사진, 평점, 생성일, 수정일)
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HanbokComment
        fields = [
            "id",
            "store",
            "user",
            "content",
            "review_image",
            "grade",
            "created_at",
            "updated_at",
        ]


# ✅ 한복점 리뷰 등록 (후기내용, 후기사진, 평점, 생성일, 수정일)
class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HanbokComment
        fields = [
            "content",
            "review_image",
            "grade",
        ]


# ✅ 결제 정보 기록용 Serializer
class PurchaseRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRecord
        fields = [
            "tid",
            "partner_order_id",
            "partner_user_id",
            "item_name",
            "quantity",
            "total_amount",
            "vat_amount",
            "rsrvt_date",
            "rsrvt_time",
            "created_at",
            "payment_method_type",
            "aid",
            "approved_at",
        ]


# ✅ 결제 정보 조회용 Serializer
class PurchaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRecord
        fields = "__all__"
