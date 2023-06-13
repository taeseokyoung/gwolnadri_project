from rest_framework import serializers
from .models import Store, PurchaseRecord

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
            "location_y",  # 나중에 지우기s
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


# 결제 정보 기록용 Serializer
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


# 결제 정보 조회용 Serializer
class PurchaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRecord
        fields = "__all__"
