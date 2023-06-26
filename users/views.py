import os
import requests
from rest_framework import status, permissions, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.generics import get_object_or_404
from django.shortcuts import redirect, get_object_or_404

from django.http import JsonResponse
from json.decoder import JSONDecodeError
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.naver import views as naver_view
from allauth.socialaccount.models import SocialAccount
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
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "가입완료!"}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


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
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "회원 탈퇴 완료"}, status=status.HTTP_204_NO_CONTENT)


# 비밀번호 변경
class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer


# 소셜로그인
BASE_URL = "http://127.0.0.1:8000/"
KAKAO_CALLBACK_URI = BASE_URL + "users/kakao/login/callback/"
# NAVER_CALLBACK_URI = BASE_URL + "users/naver/login/callback/"
# GOOGLE_CALLBACK_URI = BASE_URL + "users/google/login/callback/"
state = os.environ.get("STATE")
KAKAO_REST_API_KEY = os.environ.get("KAKAO_CLIENT_ID")

################## KAKAO Login ##################
class KakaoLoginView(APIView):
    def get(self, request):
        app_key = KAKAO_REST_API_KEY
        redirect_uri = KAKAO_CALLBACK_URI
        kakao_auth_api = "https://kauth.kakao.com/oauth/authorize?response_type=code"
        return redirect(
            f"{kakao_auth_api}&client_id={app_key}&redirect_uri={redirect_uri}"
        )
    
class KakaoCallbackView(APIView):
    def get(self, request):
        auth_code = request.GET.get("code")
        kakao_token_api = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": KAKAO_CALLBACK_URI,
            "code": auth_code,
        }
    
        token_response = requests.post(kakao_token_api, data=data)
        access_token = token_response.json().get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer ${access_token}"}
            )

        # return JsonResponse({"user_info": profile_request.json()})

        profile_json = profile_request.json()
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email")

        # 이메일 없으면 오류: 카카오톡 이메일 없이 가입 가능. 
        if email is None:
            return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)

        profile = kakao_account.get("profile")
        username = profile.get("nickname")
        # 프로필 사진 사이즈 2가지:  "thumbnail_image_url" < "profile_image_url"
        profile_image = profile.get("thumbnail_image_url")   
        
        try:
            user = User.objects.get(email=email)
            user.username = username
            user.profile_image = profile_image
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
            user = User.objects.create_user(email=email, password=password, username=username)
            user.set_unusable_password()
            user.profile_image = profile_image
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
        
class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI