from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from stores.serializers import StoreListSerializer
from events.serializers import EventBookmarkSerializer


# 회원가입, 정보수정
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user


# 마이 프로필 - 프로필 이미지, 내가 작성한 리뷰 목록, 좋아요목록, 북마크 목록
class UserProfileSerializer(serializers.ModelSerializer):
    bookmark_stores = StoreListSerializer(many=True)
    bookmark_events = EventBookmarkSerializer(many=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "bookmark_stores",
            "bookmark_events",
        )


# 로그인용
class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token
