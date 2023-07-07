from users.models import User
from django.urls import reverse
from rest_framework.test import APITestCase


# unittest pytest : 파이썬에서도 기본적인 테스트를 제공하며 앞으로도 파이썬으로 만들어진 친구들은 이것을 통해 테스트 진행할 것이다.


class UserSignupViewTestCase(APITestCase):
    def test_registration(self):
        url = reverse("signup")
        user_data = {
            "email": "tester@test.com",
            "username": "테스터",
            "password": "qwer@1234",
            "password2": "qwer@1234",
        }
        response = self.client.post(url, user_data)
        self.assertEqual(response.status_code, 201)


# 모든 test는 stateless 해야 한다. 독립적이여야 한다.

# cycle 이 있다.

# setup 모든 메서드 맨 처음 실행
# tearDown 모든 메서드 맨 끝에 실행


class UserLoginTestCase(APITestCase):
    def setUp(self):
        # models.py의 UserManager의 create_user함수에서 받는 정보
        self.data = {
            "email": "tester@test.com",
            "password": "qwer@1234",
            "username": "테스터",
        }
        self.user = User.objects.create_user("tester@test.com", "qwer@1234", "테스터")

    def test_login(self):
        # reverse("urlpatterns의 name")
        response = self.client.post(reverse("login"), self.data)
        # print(response.data["access"])
        self.assertEqual(response.status_code, 200)

    def test_get_user_data(self):
        # 1. 사용자 토큰을 가져온다.
        access_token = self.client.post(reverse("login"), self.data).data["access"]
        # 2. header에 토큰을 넣어서 로그인한다.
        response = self.client.get(
            path=reverse("profile_view"), HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        # print(response.data) : {'id': 1, 'email': 'tester2@test.com', 'username': None, 'profile_image': None, 'bookmark_stores': [], 'bookmark_events': []}
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], self.data["email"])


# class UserLogoutTestCase(APITestCase):
#     def setUp(self):
#         self.data = {
#             "email": "tester2@test.com",
#             "password": "qwer@1234",
#             "username": "테스터2",
#         }
#         self.user = User.objects.create_user("tester2@test.com", "qwer@1234", "테스터2")
#     def test_logout(self):
