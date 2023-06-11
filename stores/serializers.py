from rest_framework import serializers
from .models import Store, Hanbok

import requests, json
import os
import environ


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
    owner_id = serializers.SerializerMethodField()

    def get_owner_id(self, obj):
        return obj.owner_id.email

    class Meta:
        model = Store
        fields = ("id", "store_name", "store_address", "owner_id")


# ✅ 한복집 추가 (가게이름, 가게주소)
class CreateStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            "store_name",
            "store_address",
        )

    def create(self, validated_data):
        location_result = get_location(validated_data["store_address"])
        # 한복집 x,y좌표 | 별점(후기없는경우 0) 추가
        store = Store(**validated_data)
        store = Store.objects.create(
            owner_id=validated_data["owner_id"],
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
    class Meta:
        model = Hanbok
        fields = (
            "store_id",
            "hanbok_name",
            "hanbok_description",
            "hanbok_price",
            "hanbok_image",
        )
