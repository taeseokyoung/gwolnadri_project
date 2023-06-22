from rest_framework import serializers
from .models import Store, Hanbok, HanbokComment, PurchaseRecord
import requests, json
import os
import environ
from django.db.models import Avg


def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": os.environ.get("KakaoAK")}
    location = requests.get(url, headers=headers).json()["documents"][0]
    result = [
        location["x"],
        location["y"],
    ]
    return result


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
            "store_bookmarks",
        )


class CreateStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            "store_name",
            "store_address",
        )

    def create(self, validated_data):
        location_result = get_location(validated_data["store_address"])
        print(validated_data)
        store = Store.objects.create(
            owner=validated_data["owner"],
            store_name=validated_data["store_name"],
            store_address=validated_data["store_address"],
            location_x=location_result[0],
            location_y=location_result[1],
        )
        store.save()
        return store


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
        fields = "__all__"


class CreateHanbokSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hanbok
        fields = [
            "hanbok_name",
            "hanbok_description",
            "hanbok_price",
            "hanbok_image",
        ]


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


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HanbokComment
        fields = [
            "content",
            "review_image",
            "grade",
        ]


class PurchaseRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRecord
        fields = [
            "tid",
            "type",
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


class PurchaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRecord
        fields = "__all__"
