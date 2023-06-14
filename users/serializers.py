from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# 회원가입, 정보수정
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "pk",
            "profile_image",
            "email",
            "username",
        ]

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


# 로그인용
class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

# 마이 프로필 - 프로필 이미지, 내가 작성한 리뷰 목록, 좋아요목록, 북마크 목록
class UserProfileSerializer(serializers.ModelSerializer):
    profile_img = serializers.ImageField(
        max_length=None,
        use_url=True,
        required=False,
    )
    # event_review = serializers.SerializerMethodField()
    # hanbok_review = serializers.SerializerMethodField()
    # likes = serializers.SerializerMethodField()
    # bookmark = serializers.SerializerMethodField()

    # #게시글 목록
    # def my_hanbok_reviews(self, obj):
    #     hanbok_reviews = HanbokReview.objects.filter(user=obj)
    #     return HanbokReviewSerializer(hanbok_reviews, many=True).data
    #
    # def my_event_reviews(self, obj):
    #     event_reviews = EventReview.objects.filter(user=obj)
    #     return EventReviewSerializer(event_reviews, many=True).data

    class Meta:
        model = User
        fields = ("user_id", "username", "profile_image",)
                  #my_hanbok_reviews, my_event_reviews...등등 등록하기


#회원정보 수정
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username",  "profile_img")
        read_only_fields = ["email","password",]
        extra_kwargs = {
            "username": {
                "required": True,
            },
        }

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user
