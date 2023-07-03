import os
import requests
import random, string
from django.http import JsonResponse
from rest_framework import status, permissions, generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken


from .models import User
from .serializers import (
    UserTokenObtainPairSerializer,
    UserSerializer,
    UserProfileSerializer,
    UpdateUserSerializer,
    ChangePasswordSerializer,
)


# 회원가입
class SignupView(APIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        email = request.data.get("email", "")
        if User.objects.filter(email=email).exists():
            return Response(
                {"email": "이미 가입된 이메일입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        username = request.data.get("username", "")
        if User.objects.filter(username=username).exists():
            return Response(
                {"username": "이미 존재하는 유저네임입니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        password = request.data.get("password", "")
        password2 = request.data.get("password2", "")
        if password != password2:
            return Response(
                {"password2": "비밀번호가 불일치합니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "가입완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)


# 로그인
class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenObtainPairSerializer


class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token["email"] = user.email
        return token


def generate_jwt_token(user):
    refresh = CustomRefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


# 로그아웃
class LogoutView(APIView):
    def post(self, request):
        response = Response({"message": "로그아웃 완료"}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


# 마이페이지 보기
class Me(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user:
            serializer = UserProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


# 회원정보 수정하기, 탈퇴하기
class UpdateProfileView(generics.UpdateAPIView):
    def get_serializer_class(self):
        if self.request.data.get("password"):
            return ChangePasswordSerializer
        return UpdateUserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()
        if "profile_image" not in data:
            data["profile_image"] = instance.profile_image
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 회원탈퇴
    # def delete(self, request):
    #     user = request.user
    #     user.delete()
    #     return Response({"message": "회원 탈퇴 완료"}, status=status.HTTP_204_NO_CONTENT)



# 비밀번호 변경
class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer


# KAKAO Login
KAKAO_CALLBACK_URI = os.environ.get("KAKAO_CALLBACK_URI")
KAKAO_REDIRECT_URI = os.environ.get("KAKAO_REDIRECT_URI")


class KakaoCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": os.environ.get("KAKAO_CLIENT_ID"),
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": code,
        }

        token_response = requests.post(kakao_token_api, data=data)
        access_token = token_response.json().get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer ${access_token}"},
        )
        profile_json = profile_request.json()
        kakao_account = profile_json["kakao_account"]
        email = kakao_account["email"]

        if email is None:
            return JsonResponse(
                {"err_msg": "카카오 이메일을 가져오지 못했습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        random_string = ""
        random_number = random.randint(0, 9999)
        for i in range(3):
            random_string += str(random.choice(string.ascii_letters + str(random_number)))

        username = "kakao_" + random_string

        try:
            user = User.objects.get(email=email)
            user.username = username
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            password = User.objects.make_random_password()
            user = User.objects.create_user(
                email=email, password=password, username=username
            )
            user.username = username
            user.set_unusable_password()
            user.save()
            refresh = RefreshToken.for_user(user)
            refresh["email"] = user.email
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
