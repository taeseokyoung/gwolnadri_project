from django.urls import path, include
from users import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("token/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", views.Me.as_view(), name="profile_view"),
    path("me/modify/", views.UpdateProfileView.as_view(), name="profile_modify"),
    # path("me/delete/", views.UpdateProfileView.as_view(), name="profile_delete"),
    path(
        "me/<int:pk>/password/",
        views.ChangePasswordView.as_view(),
        name="change_password",
    ),
    path(
        "kakao/login/callback/",
        views.KakaoCallbackView.as_view(),
        name="kakao_callback",
    ),
]
