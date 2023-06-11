from rest_framework import serializers
from .models import Store, Hanbok

import requests, json
import os
import environ


def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": os.environ.get("KakaoAK")}
    result = [
        requests.get(url, headers=headers).json()["documents"][0]["x"],
        requests.get(url, headers=headers).json()["documents"][0]["y"],
    ]
    return result


class StoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            "id",
            "owner_id",
            "store_name",
            "store_address",
            "location_x",  # 나중에 지우기
            "location_y",  # 나중에 지우기
            "star",
        )


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
            store_name=validated_data["store_name"],
            store_address=validated_data["store_address"],
            location_x=location_result[0],
            location_y=location_result[1],
            star=0,
        )
        store.save()
        return store


# # ✅ 한복상품이미지 (다중이미지 처리)
# class HanbokImageSerializer(serializers.ModelSerializer):
#     hanbok_image = serializers.ImageField(use_url=True)

#     class Meta:
#         model = HanbokImage
#         fields = ["hanbok_image"]


# ✅ 한복상품정보 (제품명, 제품설명, 가격, 다중이미지)
class HanbokSerializer(serializers.ModelSerializer):
    # hanbok_images = serializers.SerializerMethodField()

    # def get_hanbok_images(self, obj):
    #     images = obj.hanbokimage_set.all()
    #     return HanbokImageSerializer(instance=images, many=True, read_only=True).data

    class Meta:
        model = Hanbok
        fields = (
            "store_id",
            "hanbok_name",
            "hanbok_description",
            "hanbok_price",
            "hanbok_image",
        )

    # def create(self, validated_data):
    #     hanbok = Hanbok.objects.create(**validated_data)
    #     print(self)
    #     images_data = self.data["hanbok_images"]
    #     for image_data in images_data.getlist("hanbok_images"):
    #         HanbokImage.objects.create(hanbok=hanbok, image=image_data)

    #     return hanbok
