from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Store
from .serializers import StoreListSerializer, CreateStoreSerializer


# 한복집 리스트
class StoreListView(APIView):
    def get(self, request):
        store = Store.objects.all()
        store_serializer = StoreListSerializer(store, many=True)

        return Response(
            {
                "Store List": store_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        data = request.data
        serializer = CreateStoreSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "한복집추가완료", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )


# 한복집 상세 페이지
class StoreDetailView(APIView):
    def get(self, request):
        pass
