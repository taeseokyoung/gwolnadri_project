from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Store
from .serializers import StoreListSerializer, StoreCreateSerializer


# 회원가입
class StoreListView(APIView):
    def get(self, request):
        store = Store.objects.all()
        store_serializer = StoreListSerializer(store, many=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response({"message": "한복집리스트"}, status=status.HTTP_200_OK)
        # else:
        #     return Response(
        #         {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
        #     )
        return Response(
            {
                "articles": store_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class StoreDetailView(APIView):
    def get(self, request):
        pass
