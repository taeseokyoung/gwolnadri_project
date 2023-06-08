from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Store
from .serializers import StoreListSerializer, CreateStoreSerializer

import requests, json
import os
import environ


def get_location(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": os.environ.get("KakaoAK")}
    api_json = json.loads(str(requests.get(url, headers=headers).text))
    return api_json


# 한복집 리스트
class StoreListView(APIView):
    def get(self, request):
        store = Store.objects.all()
        store_serializer = StoreListSerializer(store, many=True)

        return Response(
            {
                "articles": store_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        data = request.data
        serializer = CreateStoreSerializer(data=data)
        # location_x = get_location(data["hanbok_address"])["documents"][0]["x"]
        # location_y = get_location(data["hanbok_address"])["documents"][0]["y"]
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "한복집리스트"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


# 한복집 상세 페이지
class StoreDetailView(APIView):
    def get(self, request):
        pass
