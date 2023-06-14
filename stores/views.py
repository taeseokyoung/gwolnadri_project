from rest_framework import status
from rest_framework import permissions

from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Store, Hanbok, HanbokComment, PurchaseRecord
from .serializers import (
    StoreListSerializer,
    CreateStoreSerializer,
    HanbokSerializer,
    CreateHanbokSerializer,
    PurchaseRecordCreateSerializer,
    CommentSerializer,
    CreateCommentSerializer,
)


# 한복집 리스트
class StoreListView(APIView):
    """
    모든 한복집 리스트 -> 궁별 한복집 리스트로 변경할 예정
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        store = Store.objects.all()
        store_serializer = StoreListSerializer(store, many=True)

        return Response(
            {
                "StoreList": store_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if request.user.is_staff == True:
            serializer = CreateStoreSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
                return Response(
                    {"message": "한복집추가완료", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"${serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "권한이 없거나 잘못된 요청입니다."}, status=status.HTTP_403_FORBIDDEN
            )


# 한복집 상세 페이지
class StoreDetailView(APIView):
    """
    해당 한복집의 정보와 등록한 한복 상품 정보 노출
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, store_id):
        store = get_object_or_404(Store, id=store_id)
        hanboks = Hanbok.objects.filter(store=store_id)
        comments = HanbokComment.objects.filter(store=store_id)

        store_serializer = StoreListSerializer(store)
        hanbok_serializer = HanbokSerializer(hanboks, many=True)
        comment_serializer = CommentSerializer(comments, many=True)

        return Response(
            {
                "Store": store_serializer.data,
                "HanbokList": hanbok_serializer.data,
                "Comment": comment_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, store_id):
        """
        staff인지 내가게인지 확인
        """
        my_store = list(Store.objects.filter(owner=request.user))
        this_store = list(Store.objects.filter(id=store_id))

        if (request.user.is_staff == True) and (
            (this_store == my_store) or (this_store[0] in my_store)
        ):
            serializer = CreateHanbokSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(owner=request.user, store_id=store_id)
                return Response(
                    {"message": "한복 추가 완료", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"message": f"${serializer.errors}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": "권한이 없거나 잘못된 요청입니다."}, status=status.HTTP_403_FORBIDDEN
            )


class CommentView(APIView):
    def get(self, request, store_id):
        """
        한복점에 달린 모든 리뷰
        """
        store = Store.objects.get(store_id=store_id)
        comments = store.comments.all()
        comment_serializer = CommentSerializer(comments, many=True)
        return Response(
            {
                "Comment": comment_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, store_id):
        pass

    def delete(self, request, store_id):
        pass


# 결제 승인요청
class PurchaseRecordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        pass

    def post(self, request, user_id):
        decomplete = PurchaseRecord.objects.filter(
            user_id=user_id, approved_at__isnull=True
        )
        if decomplete.exists():
            decomplete.delete()
        serializer = PurchaseRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "db 저장완료"}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 결제 완료
class PutPurchaseRecordView(APIView):
    def get(self, request, tid):
        purchase_record = get_object_or_404(PurchaseRecord, tid=tid)
        serializer = PurchaseRecordCreateSerializer(purchase_record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, tid):
        purchase_record = get_object_or_404(PurchaseRecord, tid=tid)
        serializer = PurchaseRecordCreateSerializer(
            purchase_record, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "결제완료"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
