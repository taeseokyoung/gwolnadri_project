from users.models import User
from stores.models import Store, Hanbok, HanbokComment
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# 이미지 파일을 보내는 과정은 동일. 이미지 파일을 만드는 과정은 좀 더 효율적 방법을 찾아보자. (실제 파일로 할 수 있지만 이 방법은 파이썬에서 제공하는 임시파일을 만들며 진행하므로 좀 복잡할 수 있다.)

# 이미지 업로드 (멀티파트)
from django.test.client import MULTIPART_CONTENT, encode_multipart, BOUNDARY
from PIL import Image
import tempfile


def get_temporary_image(temp_file):
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, "png")
    return temp_file


class StoreCreateTest(APITestCase):
    # classmethod를 쓰지 않고 일반적으로 이렇게 쓴다.
    # def setUpTestData(self):
    #     self.user_data = {
    #         "email": "tester@test.com",
    #         "password": "qwer@1234",
    #         "username": "테스터",
    #         "id": self.user_id,
    #     }
    #     self.store_data = {
    #         "owner": self.user_id,
    #         "store_name": "청춘한복아랑",
    #         "store_address": "서울 종로구 자하문로13길 5 아랑한복",
    #         "location_x": 126.970816,
    #         "location_y": 37.5799334,
    #         "likes": self.user_id,
    #         # "store_bookmarks" : "",
    #         # "tags":"",
    #     }
    #     self.user = User.objects.create_user("tester@test.com", "qwer@1234", "테스터")
    #     access_token = self.client.post(reverse("login"), self.data).data["access"]

    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "tester@test.com",
            "password": "qwer@1234",
            "username": "테스터",
            "id": 1,
            "is_staff": True,
        }
        cls.store_data = {
            "store": 1,
            "owner": 1,
            "store_name": "청춘한복아랑",
            "store_address": "서울 종로구 자하문로13길 5 아랑한복",
            "location_x": 126.970816,
            "location_y": 37.5799334,
            "likes": 1,
            # "store_bookmarks" : "",
            # "tags":"",
        }
        cls.hanbok_data = {
            "store": 1,
            "owner": 1,
            "hanbok_name": "한복",
            "hanbok_description": "한복 상품설명입니다.",
            "hanbok_price": 10000,
        }
        cls.user = User.objects.create_user(**cls.user_data)

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data[
            "access"
        ]

    def test_get_store_if_not_logged_in(self):
        url = reverse("store_list")
        response = self.client.get(url, self.store_data)
        print(response)
        self.assertEqual(response.status_code, 200)

    def test_create_store(self):
        response = self.client.post(
            path=reverse("store_list"),
            data=self.store_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        if self.user.is_staff == True:
            self.assertEqual(response.status_code, 200)
            # self.assertEqual(response.data["message"], "한복집추가완료")
        else:
            self.assertEqual(response.status_code, 403)

    # def test_create_hanbok(self):
    #     response = self.client.post(
    #         path="api/v1/stores/1/",
    #         data=self.hanbok_data,
    #         HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
    #     )
    def test_create_hanbok_with_image(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.name = "image.png"
        image_file = get_temporary_image(temp_file)
        image_file.seek(0)  # 이미지의 첫번째 프레임 받아오기
        self.hanbok_data["hanbok_image"] = image_file

        store_id = 1
        response = self.client.post(
            path=reverse("store_detail_view", args=[store_id]),
            data=encode_multipart(data=self.hanbok_data, boundary=BOUNDARY),
            content_type=MULTIPART_CONTENT,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        print(response, "response")
        # self.assertEqual(response["message"], "한복 추가 완료")
        self.assertEqual(response.status_code, 200)
