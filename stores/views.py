from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from .models import Store, Hanbok
from .serializers import StoreListSerializer, CreateStoreSerializer, HanbokSerializer


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
    """
    해당 한복집의 정보와 등록한 한복 상품 정보 노출
    """

    def get(self, request, store_id):
        store = get_object_or_404(Store, id=store_id)
        hanboks = Hanbok.objects.filter(store_id=store_id)
        store_serializer = StoreListSerializer(store)
        hanbok_serializer = HanbokSerializer(hanboks, many=True)

        return Response(
            {
                "Store": store_serializer.data,
                "Hanbok List": hanbok_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, store_id):
        data = request.data
        serializer = HanbokSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "한복 추가 완료", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": f"${serializer.errors}"}, status=status.HTTP_400_BAD_REQUEST
            )
