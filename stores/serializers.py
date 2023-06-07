from rest_framework import serializers
from .models import Store


class StoreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            "id",
            "user_id",
            "hanbok_store",
            "hanbok_address",
            "star",
        )


class StoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            "hanbok_store",
            "hanbok_address",
            "star",
        )
